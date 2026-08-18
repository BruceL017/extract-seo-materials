#!/usr/bin/env python3
"""Enumerate locally persisted Codex sessions for one Git worktree."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


def _iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _git_root(path: Path) -> Optional[Path]:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def _state_databases(codex_home: Path) -> Iterable[Path]:
    for path in (codex_home / "state_5.sqlite", codex_home / "sqlite/state_5.sqlite"):
        if path.is_file():
            yield path


def _state_rows(database: Path) -> List[Tuple[str, Optional[str], Optional[str]]]:
    uri = "file:{}?mode=ro".format(database.resolve().as_posix())
    connection = sqlite3.connect(uri, uri=True)
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(threads)").fetchall()
        }
        cwd_column = "cwd" if "cwd" in columns else "NULL"
        return connection.execute(
            "SELECT id, rollout_path, {} FROM threads".format(cwd_column)
        ).fetchall()
    finally:
        connection.close()


def _rollout_files(roots: Iterable[Tuple[Path, bool]], errors: Counter) -> Set[Path]:
    paths: Set[Path] = set()
    for root, required_codex_format in roots:
        if not root.exists():
            continue
        walk_failed = False

        def onerror(_error: OSError) -> None:
            nonlocal walk_failed
            walk_failed = True

        for directory, _subdirectories, filenames in os.walk(root, onerror=onerror):
            paths.update(
                (Path(directory) / filename).resolve()
                for filename in filenames
                if filename.endswith(".jsonl")
            )
        if walk_failed and required_codex_format:
            errors["session_root_unreadable"] += 1
    return paths


def _session_meta(path: Path) -> Tuple[Optional[dict], Optional[str]]:
    try:
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= 256:
                    break
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") == "session_meta" and isinstance(record.get("payload"), dict):
                    return record["payload"], None
    except OSError:
        return None, "unreadable_rollout"
    return None, "missing_session_meta"


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _scope_status(
    cwd_value: object,
    project_root: Path,
    project_git_root: Optional[Path],
) -> str:
    if not isinstance(cwd_value, str) or not cwd_value:
        return "unknown"
    cwd = Path(cwd_value).expanduser().resolve()
    if not _inside(cwd, project_root):
        return "out"
    cwd_git_root = _git_root(cwd)
    if project_git_root is not None and cwd_git_root is None:
        return "unknown"
    return "in" if cwd_git_root == project_git_root else "out"


def build_inventory(
    project_root: Path,
    codex_home: Path,
    agents_sessions_root: Optional[Path],
    scan_cutoff_at: str,
) -> dict:
    """Build a complete local session inventory for the current project boundary."""
    cutoff = _iso_datetime(scan_cutoff_at)
    if cutoff.tzinfo is None:
        raise ValueError("--scan-cutoff-at must include a timezone")
    project_root = project_root.resolve()
    codex_home = codex_home.expanduser().resolve()
    project_git_root = _git_root(project_root)
    if project_git_root is not None:
        project_root = project_git_root

    errors: Counter = Counter()
    if not codex_home.exists():
        errors["codex_home_missing"] += 1
    state_paths: Dict[Path, Set[str]] = defaultdict(set)
    state_scope: Dict[Path, List[Tuple[str, str]]] = defaultdict(list)
    discovered_ids: Set[str] = set()
    state_row_count = 0

    for database in _state_databases(codex_home):
        try:
            rows = _state_rows(database)
        except (OSError, sqlite3.DatabaseError):
            errors["state_db_unreadable"] += 1
            continue
        state_row_count += len(rows)
        for session_id, rollout_path, cwd_value in rows:
            if not session_id:
                if _scope_status(cwd_value, project_root, project_git_root) != "out":
                    errors["missing_session_id"] += 1
                continue
            scope = _scope_status(cwd_value, project_root, project_git_root)
            if not rollout_path:
                if scope != "out":
                    discovered_ids.add(session_id)
                    errors["missing_rollout"] += 1
                continue
            path = Path(rollout_path).expanduser().resolve()
            if not path.is_file():
                if scope != "out":
                    discovered_ids.add(session_id)
                    errors["missing_rollout"] += 1
                continue
            state_paths[path].add(session_id)
            state_scope[path].append((session_id, scope))

    roots: List[Tuple[Path, bool]] = [
        (codex_home / "sessions", True),
        (codex_home / "archived_sessions", True),
    ]
    if agents_sessions_root is not None:
        roots.append((agents_sessions_root.expanduser().resolve(), False))
    rollout_paths = _rollout_files(roots, errors) | set(state_paths)

    threads_by_id: Dict[str, dict] = {}
    seen_paths_by_id: Dict[str, Set[Path]] = defaultdict(set)
    for path in sorted(rollout_paths):
        meta, error = _session_meta(path)
        if meta is None:
            linked_candidates = [
                session_id
                for session_id, scope in state_scope.get(path, [])
                if scope != "out"
            ]
            is_codex_rollout = any(
                required and _inside(path, root) for root, required in roots
            )
            if linked_candidates or (not state_scope.get(path) and is_codex_rollout):
                errors[error or "unreadable_rollout"] += 1
                discovered_ids.update(linked_candidates)
            continue

        cwd_value = meta.get("cwd")
        scope = _scope_status(cwd_value, project_root, project_git_root)
        if scope == "out":
            continue
        if scope == "unknown":
            if not isinstance(cwd_value, str) or not cwd_value:
                errors["missing_cwd"] += 1
            else:
                errors["git_root_unresolved"] += 1
            discovered_ids.update(
                session_id
                for session_id, linked_scope in state_scope.get(path, [])
                if linked_scope != "out"
            )
            continue

        session_id = meta.get("id") or meta.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            errors["missing_session_id"] += 1
            continue
        if state_paths.get(path) and session_id not in state_paths[path]:
            errors["session_id_mismatch"] += 1

        started_at = meta.get("timestamp")
        if isinstance(started_at, str):
            try:
                if _iso_datetime(started_at) > cutoff:
                    continue
            except (TypeError, ValueError):
                errors["invalid_session_timestamp"] += 1
        else:
            errors["missing_session_timestamp"] += 1

        discovered_ids.add(session_id)
        discovered_ids.update(state_paths.get(path, set()))
        seen_paths_by_id[session_id].add(path)

        cwd = Path(cwd_value).expanduser().resolve()
        threads_by_id.setdefault(
            session_id,
            {
                "id": session_id,
                "cwd": str(cwd),
                "rollout_path": str(path),
                "session_started_at": started_at,
            },
        )

    for paths in seen_paths_by_id.values():
        if len(paths) > 1:
            errors["ambiguous_rollout"] += 1

    reasons = dict(sorted(errors.items()))
    threads = [threads_by_id[session_id] for session_id in sorted(threads_by_id)]
    return {
        "schema_version": 1,
        "scan_cutoff_at": scan_cutoff_at,
        "project_root": str(project_root),
        "coverage_status": "partial" if reasons else "complete",
        "discovered_thread_count": len(discovered_ids),
        "in_scope_thread_count": len(threads),
        "threads": threads,
        "unreadable_scope_reasons": reasons,
        "inventory_sources": {
            "state_db_rows": state_row_count,
            "rollout_files": len(rollout_paths),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enumerate persisted Codex sessions for one project boundary."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")),
    )
    parser.add_argument(
        "--agents-sessions-root",
        type=Path,
        default=Path.home() / ".agents/sessions",
    )
    parser.add_argument("--no-agents-sessions", action="store_true")
    parser.add_argument("--scan-cutoff-at", required=True)
    args = parser.parse_args()
    agents_root = None if args.no_agents_sessions else args.agents_sessions_root
    inventory = build_inventory(
        args.project_root,
        args.codex_home,
        agents_root,
        args.scan_cutoff_at,
    )
    print(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
