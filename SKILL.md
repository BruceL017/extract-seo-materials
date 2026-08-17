---
name: extract-seo-materials
description: Extract and summarize Chinese SEO content material from the current visible Codex product-development conversation, save at most one timestamped session Markdown file, and rebuild the single project-level material summary from prior generated session files in the same local project. Use when the user says or implies “总结当前会话 SEO 素材”, “提取当前会话 SEO 内容素材”, “汇总当前会话 SEO 素材”, “SEO 内容素材”, “SEO 素材”, “沉淀本次开发内容”, or asks to update the project SEO material summary. Apply to products and domains of any kind, not only Web3. Do not use for article drafting, keyword metrics, SERP research, another Codex thread, or cross-repository aggregation.
---

# Extract SEO Materials

Run one invocation as a two-stage pipeline: extract the current visible conversation, then rebuild the project summary from generated session files. Treat session files as retained sources and the summary as a generated view.

Before writing anything, read [references/output-contract.md](references/output-contract.md) completely and follow its schemas and merge rules.

## Hard boundaries

- Use only the current visible developer-Agent conversation for new material. Do not read another Codex thread or hidden reasoning.
- Exclude system/tool orchestration and discussion about this Skill itself unless it reveals a user-facing product issue.
- Do not browse the web, call SEO data services, perform keyword research, or claim search demand.
- Do not inspect project source code or unrelated project documents. A code or test result counts only when the visible conversation explicitly explains its meaning.
- During summary rebuild, read only generated `*.md` files directly inside `_content_materials/sessions/`. Never read the existing summary as source.
- Produce source material, not article prose, publishing copy, or a finished outline.
- Write in Chinese while preserving exact product, platform, protocol, and English technical terms.

## Locate the project

1. Treat the active Codex working directory as the complete project boundary. Do not walk into a parent repository or aggregate another working directory.
2. Use that directory's leaf name as `project`.
3. Store outputs only under:
   - `_content_materials/sessions/`
   - `_content_materials/summary/project-seo-materials.md`

Create missing output directories. Do not create a database, manifest, or sidecar format.

## Stage 1: extract the current session

### Select material

Identify every distinct issue that satisfies all of these conditions:

- A product user could experience the problem, risk, decision, misconception, or use case.
- The visible conversation contains a concrete discussion, conclusion, constraint, failed approach, or explicitly labeled hypothesis about it.
- The material can be explained without mining source code.
- It contributes something more specific than generic industry advice or product promotion.

Exclude routine refactors, ordinary debugging, code mechanics, Agent coordination, and implementation details with no user-visible consequence. Merge repeated discussion of the same user problem into one material package; keep different user problems separate.

Classify each package with only these controlled values:

- Contribution types: `问题发现`, `原理解释`, `解决方案`, `验证证据`, `失败经验`, `风险限制`, `用户案例`.
- Fact states: `已验证事实`, `工程结论`, `待验证假设`, `失败方案`.
- Search intents: `信息了解`, `问题排查`, `风险判断`, `比较选择`, `工具评估`.

Do not upgrade a hypothesis into a conclusion. Do not infer validation from implementation activity alone.

### Apply the safety filter

- Omit API keys, tokens, credentials, personal data, identity-linked account identifiers or addresses, private endpoints, and exploitable vulnerability details. Never reproduce their values, including in source summaries.
- Summarize unreleased features or commercially sensitive decisions only when essential, and set the public boundary to `发布前确认`.
- Use `可公开` only when the conversation supplies no known publication restriction.

### Write at most one session file

If no item passes the selection gate, do not create a session file and continue to Stage 2.

Otherwise:

1. Obtain the local timestamp in both `YYYYMMDD-HHmmss` and ISO 8601 with timezone forms.
2. Derive a concise kebab-case session-topic slug; use `development-session` if no safe slug is available.
3. Use `<timestamp>-<slug>.md`. If that name already exists, append a numeric suffix instead of overwriting it.
4. Put every selected material package into that one file using the session schema in the reference.
5. Record only a source summary, never a full transcript or verbatim dialogue excerpt.

Treat an invocation as one session snapshot. Never modify or delete an older session file.

## Stage 2: rebuild the project summary

1. Enumerate session files by ascending filename timestamp.
2. Accept current documents and both legacy formats defined in the reference. Ignore truly foreign Markdown. If a file contains any recognized current or legacy `generated_by` or `document_type` value but does not form an exact accepted pair or violates its schema, stop the rebuild, preserve the old summary, and report the file.
3. Read every accepted source completely. If any accepted source is truncated or unreadable, stop before replacing the summary.
4. Assign `[S001]`, `[S002]`, and subsequent source labels in chronological filename order.
5. Group packages only when they share the underlying user problem and search intent. Use product/module and domain entities as supporting signals, not as sufficient grouping criteria. When uncertain, keep topics separate.
6. Merge semantically equivalent claims and union all supporting source labels. Preserve materially different platform, environment, protocol, or scenario behavior as subcases.
7. Surface conflicting or revised conclusions with their fact states, timestamps, and source labels. Never silently choose the newest claim or declare it correct without explicit evidence.
8. Calculate content maturity using the ordered checklist in the reference. Apply the checklist to source readiness, not to optional ideas that would merely enrich an already supportable answer.
9. Rebuild the complete summary from accepted session files. Assemble and verify the full replacement before touching the old summary; never append to or summarize the previous summary.
10. Replace the summary atomically: write the complete candidate to `_content_materials/summary/.project-seo-materials.md.tmp`, verify it, then rename it over `project-seo-materials.md` on the same filesystem. Never delete the old summary first. Remove a leftover temp file after a failed attempt without changing the old summary.

Every fact, conclusion, failed experience, risk, limitation, and conflict statement in the summary must end with at least one valid source label. Recommended content angles need no citation. The source index must list every accepted session file even when several files contribute to one topic.

## Verify and report

Before finishing, check that:

- The current invocation created zero or one session file.
- Exactly one fixed summary path is used.
- `source_session_count` matches the source index and accepted session files.
- `topic_count` matches the rendered topic sections.
- Every `[Sxxx]` citation resolves to the source index.
- No summary text was used as source and no sensitive value was copied.

Report the number of extracted packages, the new session path or `本次提取 0 条`, the summary path, accepted source count, topic count, and any ignored foreign files or blocking malformed files. Assume sequential invocations; if the session file set changes during rebuild, rerun the rebuild instead of adding a locking system.
