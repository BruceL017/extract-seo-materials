import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from project_sessions import build_inventory  # noqa: E402


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)


def write_rollout(path: Path, session_id: str, cwd: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": "2026-01-01T00:00:00Z",
        "type": "session_meta",
        "payload": {
            "id": session_id,
            "cwd": str(cwd),
            "timestamp": "2026-01-01T00:00:00Z",
        },
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")


def write_state_db(codex_home: Path, rows: list[tuple[str, Path]]) -> None:
    database = codex_home / "state_5.sqlite"
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT)")
        connection.executemany(
            "INSERT INTO threads (id, rollout_path) VALUES (?, ?)",
            [(session_id, str(path)) for session_id, path in rows],
        )
        connection.commit()
    finally:
        connection.close()


def write_state_db_with_cwd(
    codex_home: Path, rows: list[tuple[str, Path, Path]]
) -> None:
    database = codex_home / "state_5.sqlite"
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, cwd TEXT)"
        )
        connection.executemany(
            "INSERT INTO threads (id, rollout_path, cwd) VALUES (?, ?, ?)",
            [(session_id, str(path), str(cwd)) for session_id, path, cwd in rows],
        )
        connection.commit()
    finally:
        connection.close()


class ProjectSessionInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        self.other = self.root / "project-old"
        self.codex_home = self.root / "codex"
        init_repo(self.project)
        init_repo(self.other)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def inventory(self) -> dict:
        return build_inventory(
            project_root=self.project,
            codex_home=self.codex_home,
            agents_sessions_root=None,
            scan_cutoff_at="2026-08-18T00:00:00Z",
        )

    def test_finds_old_project_session_without_recent_task_list(self) -> None:
        old_session = "019fa7f9-c6eb-7b81-9762-26be61260295"
        other_session = "019f8dc2-7b0e-72c0-94c9-496c0cab2d6d"
        old_path = self.codex_home / "sessions/2026/01/01" / f"rollout-{old_session}.jsonl"
        other_path = self.codex_home / "sessions/2026/08/18" / f"rollout-{other_session}.jsonl"
        write_rollout(old_path, old_session, self.project)
        write_rollout(other_path, other_session, self.other)
        os.utime(old_path, (1, 1))
        write_state_db(self.codex_home, [(old_session, old_path), (other_session, other_path)])

        inventory = self.inventory()

        self.assertEqual(inventory["coverage_status"], "complete")
        self.assertEqual(inventory["discovered_thread_count"], 1)
        self.assertEqual(inventory["in_scope_thread_count"], 1)
        self.assertEqual([thread["id"] for thread in inventory["threads"]], [old_session])

    def test_includes_active_and_archived_rollouts(self) -> None:
        active_id = "019fa7f9-c6eb-7b81-9762-26be61260295"
        archived_id = "019f8dc2-7b0e-72c0-94c9-496c0cab2d6d"
        active = self.codex_home / "sessions/2026/01/01" / f"rollout-{active_id}.jsonl"
        archived = self.codex_home / "archived_sessions" / f"rollout-{archived_id}.jsonl"
        write_rollout(active, active_id, self.project)
        write_rollout(archived, archived_id, self.project / "src")
        (self.project / "src").mkdir()
        write_state_db(self.codex_home, [(active_id, active), (archived_id, archived)])

        inventory = self.inventory()

        self.assertEqual(inventory["coverage_status"], "complete")
        self.assertEqual(
            [thread["id"] for thread in inventory["threads"]],
            sorted([active_id, archived_id]),
        )

    def test_excludes_sibling_prefix_and_nested_git_repository(self) -> None:
        sibling_id = "019fa7f9-c6eb-7b81-9762-26be61260295"
        nested_id = "019f8dc2-7b0e-72c0-94c9-496c0cab2d6d"
        nested = self.project / "vendor" / "nested"
        init_repo(nested)
        sibling = self.codex_home / "sessions" / f"rollout-{sibling_id}.jsonl"
        nested_path = self.codex_home / "sessions" / f"rollout-{nested_id}.jsonl"
        write_rollout(sibling, sibling_id, self.other)
        write_rollout(nested_path, nested_id, nested)
        write_state_db(self.codex_home, [(sibling_id, sibling), (nested_id, nested_path)])

        inventory = self.inventory()

        self.assertEqual(inventory["coverage_status"], "complete")
        self.assertEqual(inventory["in_scope_thread_count"], 0)
        self.assertEqual(inventory["threads"], [])

    def test_missing_database_rollout_makes_coverage_partial(self) -> None:
        session_id = "019fa7f9-c6eb-7b81-9762-26be61260295"
        missing = self.codex_home / "sessions" / f"rollout-{session_id}.jsonl"
        write_state_db(self.codex_home, [(session_id, missing)])

        inventory = self.inventory()

        self.assertEqual(inventory["coverage_status"], "partial")
        self.assertEqual(inventory["unreadable_scope_reasons"], {"missing_rollout": 1})

    def test_missing_rollout_from_other_project_does_not_reduce_coverage(self) -> None:
        project_id = "019fa7f9-c6eb-7b81-9762-26be61260295"
        other_id = "019f8dc2-7b0e-72c0-94c9-496c0cab2d6d"
        project_path = self.codex_home / "sessions" / f"rollout-{project_id}.jsonl"
        missing_other_path = self.codex_home / "sessions" / f"rollout-{other_id}.jsonl"
        write_rollout(project_path, project_id, self.project)
        write_state_db_with_cwd(
            self.codex_home,
            [
                (project_id, project_path, self.project),
                (other_id, missing_other_path, self.other),
            ],
        )

        inventory = self.inventory()

        self.assertEqual(inventory["coverage_status"], "complete")
        self.assertEqual(inventory["discovered_thread_count"], 1)
        self.assertEqual(inventory["in_scope_thread_count"], 1)
        self.assertEqual(inventory["unreadable_scope_reasons"], {})

    def test_ignores_non_codex_jsonl_in_agents_session_root(self) -> None:
        self.codex_home.mkdir()
        agents_root = self.root / "agents/sessions"
        agents_root.mkdir(parents=True)
        (agents_root / "other-agent.jsonl").write_text("{}\n", encoding="utf-8")

        inventory = build_inventory(
            project_root=self.project,
            codex_home=self.codex_home,
            agents_sessions_root=agents_root,
            scan_cutoff_at="2026-08-18T00:00:00Z",
        )

        self.assertEqual(inventory["coverage_status"], "complete")
        self.assertEqual(inventory["discovered_thread_count"], 0)
        self.assertEqual(inventory["unreadable_scope_reasons"], {})


if __name__ == "__main__":
    unittest.main()
