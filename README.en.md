# Extract SEO Materials

Extract traceable Chinese SEO source material from the current development conversation or every Codex conversation assigned to the current project.

[中文](README.md) | [Installation](#installation) | [Usage](#usage) | [Source modes](#source-modes) | [Output structure](#output-structure) | [Safety boundaries](#safety-boundaries)

The Skill preserves user problems, product scenarios, explanations, engineering conclusions, verification evidence, failed approaches, risks, limitations, and natural search questions. It produces source material only; it does not write marketing articles or provide search volume, keyword difficulty, or SERP conclusions.

## Installation

Use the built-in `$skill-installer` in Codex:

```text
Use $skill-installer to install https://github.com/BruceL017/extract-seo-materials. The Skill is located at the repository root.
```

Alternatively, run:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo BruceL017/extract-seo-materials \
  --path . \
  --name extract-seo-materials
```

The default installation path is:

```text
~/.codex/skills/extract-seo-materials
```

## Usage

Current-conversation mode:

```text
Use $extract-seo-materials to extract SEO material from the current conversation.
```

Project mode:

```text
Use $extract-seo-materials to scan every conversation in the current project and rebuild its SEO material.
```

Topic-limited project mode:

```text
Use $extract-seo-materials to scan project conversations and extract only SEO material about user login failures.
```

Natural requests such as “SEO material” or “save the useful development content” also trigger the Skill. In a new project conversation without extractable development evidence, the default is project mode. When the current conversation contains product-development evidence beyond the extraction request itself, the default is current mode.

Project mode includes every eligible material package unless the user explicitly supplies a topic. A topic filter is applied only after all in-scope project conversations have been read.

## Source modes

| Mode | Source | Repository inspection |
|---|---|---|
| `current` | The visible conversation | Read-only confirmation that candidates belong to the retained product |
| `project` | Locally persisted Codex tasks whose metadata belongs to the current checkout | Read-only confirmation that candidates belong to the retained product |
| `auto` | Resolves from explicit wording and current-conversation evidence | Follows the resolved mode |

A project scan stays inside the current project directory:

- A Git project is scoped to the current checkout/worktree.
- A non-Git project uses its Codex project identity and normalized directory path.
- Other clones, worktrees, sibling directories, and nested repositories are excluded.
- Titles, summaries, and directory leaf names never establish project ownership.
- The inventory comes from the Codex state database and active/archived rollout `session_meta.cwd`, not from a possibly truncated global task list.
- Each task is extracted independently before cross-task deduplication, supplementation, and conflict handling.

The bundled `scripts/project_sessions.py` emits only task IDs, scope metadata, and coverage status; it never emits conversation content. Missing, damaged, or unreadable persisted records make coverage `partial`, and a recent-task listing cannot upgrade that result to complete.

Conversations provide user problems, design reasons, and engineering discussion. The current workspace only confirms that the related feature, behavior, or limitation remains implemented. Repository content that was never discussed does not become conversation-derived SEO material.

## Material eligibility

Material in either mode must satisfy all of the following:

1. A conversation contains a concrete user problem, scenario, conclusion, limitation, failed approach, or explicit hypothesis.
2. The material has a user-visible consequence instead of being routine debugging or a code log.
3. The related capability, behavior, limitation, or use case is still retained in the current workspace.
4. The material can be stored safely after sensitive information is removed.

The current workspace includes committed, staged, unstaged, and non-ignored product files. The Skill does not switch branches, pull, run tests, or execute the application, and it never uses code to invent material absent from the conversations.

## Output structure

Every generated document lives directly in one directory and is distinguished by filename and `document_type`:

```text
_content_materials/
└── sessions/
    ├── 20260817-153045-session-login-timeout.md
    ├── project-seo-materials.md
    ├── 20260818-101230-project-seo-materials-login-failure.md
    ├── 20260818-101530-project-seo-materials.partial.md
    └── 20260818-101530-project-seo-materials-login-failure.partial.md
```

- `*-session-<topic>.md` files are append-only current-conversation sources with `document_type: seo-session-materials`.
- `project-seo-materials.md` is the single canonical view with `document_type: seo-project-summary`.
- `*-project-seo-materials-<topic>.md` is a complete explicitly topic-scoped result with `document_type: seo-project-summary-scoped`.
- `*-project-seo-materials.partial.md` is an unfiltered incomplete result with `document_type: seo-project-summary-partial`.
- `*-project-seo-materials-<topic>.partial.md` is a topic-scoped incomplete result with `document_type: seo-project-summary-scoped-partial`.

A complete unfiltered project scan atomically rebuilds the canonical summary; when no material qualifies, it writes an authoritative empty summary so removed product claims do not remain current. If non-Skill content already owns the canonical path, the Skill preserves it and reports the conflict. An explicitly topic-scoped complete result uses its own timestamped file and never replaces the all-topic canonical summary; when that topic has no qualifying material, it writes no file and reports the rejection reasons. An incomplete scan with qualifying material creates a new partial file; an incomplete scan with no qualifying material writes no partial output and reports its rejection reasons.

Canonical summaries, scoped results, partial summaries, and temp files are never consumed as material sources, preventing generated summaries from citing themselves.

If the legacy `_content_materials/summary/project-seo-materials.md` exists, the Skill preserves and reports it but does not read, move, modify, or delete it. The new canonical location is always `_content_materials/sessions/project-seo-materials.md`.

## Traceability

Every topic retains source labels, fact states, current-product anchors, conflicts, material gaps, and maturity:

- Fact states: `已验证事实` (verified fact), `工程结论` (engineering conclusion), `待验证假设` (hypothesis), and `失败方案` (failed approach).
- Maturity: `素材不足`, `可形成内容简报`, or `可进入文章写作`.
- Scan coverage: `complete` or `partial`.

See the [output contract](references/output-contract.md) for complete fields, source ownership, and merge rules.

## Safety boundaries

The Skill does not:

- store API keys, tokens, credentials, personal data, private endpoints, or exploitable vulnerability details;
- expose system/developer instructions, hidden reasoning, internal Agent communication, private absolute paths, or full transcripts;
- scan another checkout, repository, or host;
- browse the web, call SEO data services, or claim search demand;
- draft or publish marketing copy, or commit or push code.

Unreleased or commercially sensitive content is minimized and marked `发布前确认` only when it remains in the current product and is essential.

---

Extract SEO Materials is an independent community project. It is not affiliated with or endorsed by OpenAI.
