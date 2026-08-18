# Output contract

Use these exact structures. Quote free-text YAML values and keep counts numeric.

## Contents

- [Directory contract](#directory-contract)
- [Source ownership](#source-ownership)
- [Session source document](#session-source-document)
- [Canonical project summary](#canonical-project-summary)
- [Topic-scoped project summary](#topic-scoped-project-summary)
- [Partial project summary](#partial-project-summary)
- [Source acceptance and legacy compatibility](#source-acceptance-and-legacy-compatibility)
- [Schema-version-2 validation](#schema-version-2-validation)
- [Legacy schema requirements](#legacy-schema-requirements)
- [Topic grouping](#topic-grouping)
- [Claim merging and conflict handling](#claim-merging-and-conflict-handling)
- [Current-product retention](#current-product-retention)
- [Content maturity](#content-maturity)
- [Atomic write and no-output rules](#atomic-write-and-no-output-rules)

## Directory contract

Write every generated document directly inside one directory:

```text
_content_materials/
└── sessions/
    ├── YYYYMMDD-HHmmss-session-<topic-slug>.md
    ├── project-seo-materials.md
    ├── YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.md
    ├── YYYYMMDD-HHmmss-project-seo-materials.partial.md
    └── YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.partial.md
```

The five filename classes have different ownership:

| Filename | Document type | Purpose |
|---|---|---|
| `YYYYMMDD-HHmmss-session-<topic-slug>.md` | `seo-session-materials` | Append-only source extracted in current mode |
| `project-seo-materials.md` | `seo-project-summary` | The single canonical generated project view |
| `YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.md` | `seo-project-summary-scoped` | An append-only complete result limited by an explicit topic |
| `YYYYMMDD-HHmmss-project-seo-materials.partial.md` | `seo-project-summary-partial` | A non-canonical result from an incomplete project scan |
| `YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.partial.md` | `seo-project-summary-scoped-partial` | An incomplete result limited by an explicit topic |

For a session source or complete scoped result, append `-2`, `-3`, and so on before `.md` when the preferred name already exists. For either partial class, append the suffix before `.partial.md`, producing names such as `...-2.partial.md`. Claim a final timestamped name with a filesystem exclusive-create or atomic no-replace operation. If another invocation wins the same name, advance the suffix and retry. Never use an overwrite-capable rename for a timestamped result.

Use a concise, non-sensitive kebab-case `topic-slug`; fall back to `development-session` for a current source and `requested-topic` for a scoped project result when no safe slug is available.

Never create `_content_materials/summary/`. If the legacy `_content_materials/summary/project-seo-materials.md` exists, leave it unchanged, never read it as evidence, and report it as a legacy output.

Use a unique same-directory temporary file such as `_content_materials/sessions/.project-seo-materials.<invocation-id>.tmp` while atomically replacing the canonical summary. Never share a canonical temp name between invocations. Temp and lock artifacts are never sources.

## Source ownership

- Current mode reads accepted `seo-session-materials` documents directly inside `_content_materials/sessions/` and may create one new source document.
- Project mode reads raw, in-scope Codex tasks and the current workspace retention anchors. It never reads generated Markdown as evidence and does not create per-task session source files.
- `seo-project-summary`, `seo-project-summary-scoped`, `seo-project-summary-partial`, `seo-project-summary-scoped-partial`, temp files, and foreign Markdown are never source documents.
- A partial summary never updates the canonical summary and never enters a later rebuild.
- A complete project-mode canonical summary owns the canonical path. A later current-mode run may append a session source but must not replace that broader canonical view.
- A complete unfiltered project-mode run may replace any valid Skill-owned or recognized malformed canonical summary after the full candidate has been assembled and validated.
- A topic-scoped project run never updates the all-topic canonical summary, regardless of coverage.

## Session source document

New current-mode sources use schema version 2. Schema version 1 remains a readable legacy source.

```markdown
---
document_type: seo-session-materials
schema_version: 2
generated_by: extract-seo-materials
project: "<project-directory-name>"
session_id: "<final filename stem, including any -2 or later collision suffix>"
session_topic: "<short Chinese topic>"
extracted_at: "<ISO-8601 timestamp with timezone>"
source_scope: "current-visible-conversation"
workspace_checked_at: "<ISO-8601 timestamp with timezone>"
checkout_scope: "current-workspace"
material_count: <integer>
---

# 会话 SEO 素材：<session topic>

## 会话摘要

<Summarize the product work covered by the visible conversation and its user-facing conclusions. Do not quote the dialogue.>

## M001｜<user-first material title>

- 主题标签：`<normalized problem phrase>`
- 产品/模块：`<product or module; use 未明确 when absent>`
- 领域实体：`<products, platforms, protocols, standards, systems, or 无>`
- 搜索意图：`信息了解 | 问题排查 | 风险判断 | 比较选择 | 工具评估`
- 贡献类型：`<one or more controlled contribution types>`
- 事实状态：`<one or more controlled fact states>`
- 当前产品状态：`已实现并保留`
- 当前产品锚点：`<safe relative module, route, configuration, or product surface>`
- 公开边界：`可公开 | 发布前确认`

### 用户问题与场景

<Describe the user's situation and question in non-developer language.>

### 本次讨论

<Summarize the relevant options, constraints, or failed path discussed in this conversation.>

### 结论与证据状态

- `[已验证事实]` <Only a fact explicitly described as verified in the conversation.>
- `[工程结论]` <A conclusion explicitly reached by the developer and Agent.>
- `[待验证假设]` <A useful but unresolved possibility.>
- `[失败方案]` <A rejected approach and the discussed reason.>

Omit unused fact-state bullets. Never emit an empty placeholder as evidence.

### 对普通用户的意义

<Explain the effect on user decisions, cost, safety, reliability, or task completion.>

### 用户可能如何搜索

- <Natural user question; no volume or competitiveness claim.>

### 可继续使用的内容点

- <Reusable explanation, example, distinction, or caution.>

### 尚缺素材

- <Evidence, example, limitation, or clarification another session could supply; use 无 when complete.>

### 来源摘要

<Summarize the supporting part of the visible conversation without copying dialogue.>
```

Continue with `M002`, `M003`, and so on inside the same file. `material_count` must equal the number of `## Mxxx` sections.

## Canonical project summary

Write the canonical file to `_content_materials/sessions/project-seo-materials.md`.

New canonical summaries use schema version 2 in both resolved modes:

```markdown
---
document_type: seo-project-summary
schema_version: 2
generated_by: extract-seo-materials
project: "<project-directory-name>"
last_rebuilt_at: "<ISO-8601 timestamp with timezone>"
requested_source_mode: "current | project | auto"
resolved_source_mode: "current | project"
topic_filter: "none"
coverage_status: "complete"
checkout_scope: "current-workspace"
scan_cutoff_at: "<mode-specific scan cutoff>"
source_session_count: <integer>
source_thread_count: <integer>
discovered_thread_count: <integer>
in_scope_thread_count: <integer>
read_thread_count: <integer>
unread_thread_count: 0
material_count: <integer>
rejected_candidate_count: <integer>
topic_count: <integer>
generated_only: true
---

# 项目 SEO 素材总表

> 此文件是可重建的项目素材视图，不是营销文章。请勿直接编辑。

## 汇总概况

- 最后重建：<timestamp>
- 请求来源模式：`<current | project | auto>`
- 实际来源模式：`<current | project>`
- 主题限定：`none`
- 扫描覆盖：`complete`
- 扫描截点：`<resolved scan cutoff>`
- 来源会话素材：<source_session_count>
- 来源 Codex 会话：<source_thread_count>
- 合格素材：<material_count>
- 淘汰候选：<rejected_candidate_count>
- SEO 主题：<topic_count>

## 扫描覆盖

- 发现会话：<discovered_thread_count>
- 当前项目范围：<in_scope_thread_count>
- 成功读取：<read_thread_count>
- 未读取：0

`scan_cutoff_at` is always a YAML string: write the exact sentinel `"not-applicable"` for resolved `current`, and a valid ISO-8601 timestamp with timezone for resolved `project`; reject every other value. For current mode, all four task-scan counts and `source_thread_count` are `0`. For project mode, set `source_session_count` to `0`. `source_session_count` and `source_thread_count` count only distinct rows that contribute retained material to the source index, and the material counts in those rows sum to `material_count`. `read_thread_count` records every fully read in-scope task, including tasks that contributed no accepted material. `source_thread_count` must never exceed `read_thread_count`. An empty summary therefore has zero contributing sources even when its project scan read tasks.

## 淘汰概况

| 原因 | 数量 |
|---|---:|
| `<safe rejection reason>` | <count> |

Use `本次没有淘汰候选。` when the count is zero. The row counts must sum to `rejected_candidate_count`. Do not name policy-excluded content or expose a private task identifier in a rejection reason.

## 来源索引

| 引用 | 来源类型 | 安全来源描述 | 来源时间 | 素材数 |
|---|---|---|---|---:|
| [S001] | `<source_kind>` | `<filename or safely summarized task title>` | <timestamp> | <count> |

Use `暂无来源。` instead of a table when no source exists. `source_kind` must be one of `会话素材文件` or `Codex 会话`. Do not expose an absolute path, raw task ID, account identifier, or transcript excerpt. A project-mode source label is local to that rebuild.

## SEO 主题

### T001｜<normalized user-first topic>

- 内容成熟度：`素材不足 | 可形成内容简报 | 可进入文章写作`
- 搜索意图：`<one or more controlled intents>`
- 用户可能搜索：`<deduplicated natural questions>`
- 产品关联：`<product/module relationship>`
- 领域实体：`<relevant entities or 无>`
- 当前产品状态：`已实现并保留`
- 当前产品锚点：`<safe relative module, route, configuration, or product surface>`
- 覆盖来源：`[S001] [S003]`

#### 用户问题

<Consolidated user problem and scenario.> [Sxxx]

#### 跨会话结论与证据

- `[已验证事实]` <deduplicated claim> [Sxxx] [Syyy]
- `[工程结论]` <deduplicated claim> [Sxxx]
- `[待验证假设]` <unresolved claim> [Syyy]

#### 解决方案与产品关联

- <How the retained product responds to the problem, without promotional copy.> [Sxxx]

#### 失败经验、风险与限制

- <Relevant failed path, caution, or boundary tied to the retained product.> [Sxxx]

#### 结论变化或冲突

- <Describe competing or revised conclusions with dates and sources.>

Use `未发现跨会话冲突。` when none exists.

#### 当前素材缺口

- <Missing evidence, examples, limitations, or user explanation.>

Use `无关键缺口。` only when the maturity rules support it.

#### 推荐内容角度

- <A user-first SEO content angle, not an article draft.>
```

Continue with `T002`, `T003`, and so on. `material_count` counts accepted material packages before topic grouping. `rejected_candidate_count` counts candidates that reached a selection gate but were not accepted, including `topic_mismatch` candidates in a topic-scoped project run. `topic_count` equals the number of `### Txxx` sections.

When `topic_count` is `0`, write `暂无与当前保留产品相关的合格 SEO 主题。` under `## SEO 主题`. A complete empty summary is authoritative and replaces an older canonical so removed product claims do not remain current.

Every topic in either resolved mode must use `已实现并保留` and a nonempty safe anchor. When rebuilding from a legacy schema-version-1 session source, re-apply the current-product retention gate without modifying the source file.

## Topic-scoped project summary

An explicit topic narrows the requested result, not the all-topic canonical summary. Even with complete coverage, never write a topic-scoped result to `project-seo-materials.md`.

When coverage is complete and at least one material package qualifies, write `_content_materials/sessions/YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.md`. Use the canonical schema and body with these required differences:

```yaml
document_type: seo-project-summary-scoped
schema_version: 2
resolved_source_mode: "project"
topic_filter: "<normalized explicit topic>"
coverage_status: "complete"
generated_only: true
```

Use the heading `# 项目 SEO 主题限定素材` and state the normalized topic in `## 汇总概况`. The scan, source, material, rejection, and topic counts describe the full read followed by the explicit topic filter. Candidates excluded only by that filter are counted as `topic_mismatch`.

If complete coverage yields no qualifying package for the topic, create no scoped file, preserve the canonical summary, and report the rejection reasons.

## Partial project summary

Without an explicit topic, write a partial result to `_content_materials/sessions/YYYYMMDD-HHmmss-project-seo-materials.partial.md`. Append `-2`, `-3`, and so on before `.partial.md` when needed.

Use the canonical schema and body with these required differences:

```yaml
document_type: seo-project-summary-partial
schema_version: 2
resolved_source_mode: "project"
topic_filter: "none"
coverage_status: "partial"
unread_thread_count: <positive integer when task reads failed; otherwise 0>
generated_only: true
```

Every rendered coverage label must say `partial`, and all source, material, rejection, topic, read, and unread counts must describe only this partial run. `scan_cutoff_at` is required and fixes the latest task history covered by the file.

A package qualifies for partial output when it passes the material-selection, safety, and current-product retention gates. It may retain the controlled state `待验证假设` or `失败方案`; content maturity records its limits. Do not impose a separate undefined “sufficient evidence” threshold.

Only a task counted in `read_thread_count` may contribute a package to a partial result. Exclude all candidates from a task with any unread user/assistant page. For a fully read task with an unavailable decisive tool result, cite only independently available evidence, do not retain the unavailable claim, record the evidence gap, and re-apply the gates before inclusion.

With an explicit topic, use `_content_materials/sessions/YYYYMMDD-HHmmss-project-seo-materials-<topic-slug>.partial.md`, the same body, and these field changes:

```yaml
document_type: seo-project-summary-scoped-partial
topic_filter: "<normalized explicit topic>"
```

Replace the rendered `主题限定` value with the normalized explicit topic. Append collision suffixes before `.partial.md`. Both partial types are non-canonical and never alter `project-seo-materials.md`.

Use the heading `# 项目 SEO 素材部分结果` and warning:

```markdown
> 本文件仅覆盖本次成功读取的项目会话，不代表完整项目历史，也不会替换项目素材总表。
```

Add this section after `## 扫描覆盖`:

```markdown
## 未覆盖范围

| 原因 | 数量 |
|---|---:|
| `<safe reason code>` | <count> |
```

Do not list private paths, task IDs, or sensitive titles in failure details. The reason count must explain why coverage is partial, including an unprovable regular-task inventory, missing metadata, unreadable pages, decisive truncation, or a changing snapshot.

## Source acceptance and legacy compatibility

During a current-mode rebuild, enumerate only direct `.md` children of `_content_materials/sessions/`:

- Exclude the exact canonical filename and temp files from the source set. Inspect the exact canonical separately only to determine ownership.
- Reserve filenames matching `YYYYMMDD-HHmmss-project-seo-materials*.md` for derived project results. Before excluding a reserved name, accept it only when the entire document fully validates as a schema-version-1 current or legacy session source defined below; report that legacy filename exception. Exclude every other reserved-name document before malformed-session checks so an intact or damaged scoped/partial result cannot block or enter a rebuild.
- Accept schema-version-1 and schema-version-2 session sources with `generated_by: extract-seo-materials` and `document_type: seo-session-materials`.
- Also accept the prior pair `extract-session-seo-materials` with `seo-session-materials`.
- Also accept the original pair `extract-web3-seo-materials` with `web3-seo-session-materials`; map `Web3 实体` to `领域实体` without modifying the source.
- Explicitly exclude documents with `document_type: seo-project-summary`, `seo-project-summary-scoped`, `seo-project-summary-partial`, or `seo-project-summary-scoped-partial`. They are derived outputs, not foreign files and not sources.
- Ignore truly foreign Markdown and report it.
- Treat a source containing a recognized session generator or session document type as blocking when the exact pair is incomplete or mismatched. Missing required metadata, mismatched counts, malformed material sections, or unreadable content are also blocking.

Canonical ownership is determined only after validating the document at `_content_materials/sessions/project-seo-materials.md`:

- a valid schema-version-1 canonical is current-owned;
- a valid schema-version-2 canonical with `resolved_source_mode: current`, `topic_filter: none`, and `coverage_status: complete` is current-owned;
- a valid schema-version-2 canonical with `resolved_source_mode: project`, `topic_filter: none`, and `coverage_status: complete` is project-owned;
- a recognized but malformed canonical has blocked ownership;
- unrecognized or foreign content at the canonical filename is user-owned and must not be overwritten automatically.

A successful current rebuild may replace only an absent or current-owned canonical. A complete, unfiltered project rebuild may replace an absent, current-owned, project-owned, or recognized malformed canonical after validating the full replacement. Topic-scoped and partial runs never replace it.

The old `_content_materials/summary/project-seo-materials.md` is never an accepted source or canonical target. Do not move, modify, or delete it automatically.

A malformed recognized session source blocks only the current-source summary rebuild. It does not prevent writing a separately validated, unused current-session source document. Project mode ignores generated session sources entirely.

Treat a canonical as recognized when its frontmatter contains `generated_by: extract-seo-materials` or any of the four project-summary document types defined by this contract. If it is recognized but malformed, current mode must preserve it and report blocked ownership; a complete unfiltered project-mode rebuild may replace it after independently validating the full new summary. If the canonical content is unrecognized, malformed frontmatter without a recognized marker, or foreign, every mode preserves it and reports the path conflict.

## Schema-version-2 validation

Validate schema-version-2 documents deterministically; a missing, empty, mismatched, or malformed required field is blocking for a recognized source or canonical. Free-text fields may vary, but controlled values and counts must follow this contract.

### v2 session source

An accepted v2 session source must have all of these frontmatter fields:

```yaml
document_type: seo-session-materials
schema_version: 2
generated_by: extract-seo-materials
project: "<nonempty string>"
session_id: "<final filename stem>"
session_topic: "<nonempty string>"
extracted_at: "<valid ISO-8601 timestamp with timezone>"
source_scope: "current-visible-conversation"
workspace_checked_at: "<valid ISO-8601 timestamp with timezone>"
checkout_scope: "current-workspace"
material_count: <nonnegative integer>
```

The `session_id` must equal the final filename stem, including a collision suffix such as `-2`. The body must contain exactly one `## 会话摘要` and exactly `material_count` sequential `## Mxxx` sections. Every material section must contain the nonempty `主题标签`, `产品/模块`, and `领域实体` fields; the controlled fields for search intent, contribution type, fact state, current-product state, public boundary, and a nonempty current-product anchor; plus the user-problem, discussion, conclusion/evidence, user-significance, search-question, reusable-point, missing-material, and source-summary subsections. A v2 source missing any of these fields or sections blocks a current-source rebuild; project mode does not consume generated sources.

### v2 canonical, scoped, and partial summaries

All v2 project documents must contain these common frontmatter fields with the stated types:

```yaml
document_type: "<one of the project document types>"
schema_version: 2
generated_by: extract-seo-materials
project: "<nonempty string>"
last_rebuilt_at: "<valid ISO-8601 timestamp with timezone>"
requested_source_mode: "current | project | auto"
resolved_source_mode: "current | project"
topic_filter: "<none or nonempty normalized topic>"
coverage_status: "complete | partial"
checkout_scope: "current-workspace"
scan_cutoff_at: "<mode-specific scan cutoff>"
source_session_count: <nonnegative integer>
source_thread_count: <nonnegative integer>
discovered_thread_count: <nonnegative integer>
in_scope_thread_count: <nonnegative integer>
read_thread_count: <nonnegative integer>
unread_thread_count: <nonnegative integer>
material_count: <nonnegative integer>
rejected_candidate_count: <nonnegative integer>
topic_count: <nonnegative integer>
generated_only: true
```

The `scan_cutoff_at` line resolves to one of these exact forms; do not emit the placeholder literally:

```yaml
resolved_source_mode: current
scan_cutoff_at: "not-applicable"
```

```yaml
resolved_source_mode: project
scan_cutoff_at: "<valid ISO-8601 timestamp with timezone>"
```

Apply these document-specific constraints:

- `seo-project-summary`: `topic_filter: "none"`, `coverage_status: "complete"`, and either resolved source mode. This is the only canonical document type.
- `seo-project-summary-scoped`: `resolved_source_mode: "project"`, a nonempty `topic_filter`, and `coverage_status: "complete"`. It is timestamped and never canonical.
- `seo-project-summary-partial`: `resolved_source_mode: "project"`, `topic_filter: "none"`, and `coverage_status: "partial"`.
- `seo-project-summary-scoped-partial`: `resolved_source_mode: "project"`, a nonempty `topic_filter`, and `coverage_status: "partial"`.
- For resolved `current`, `scan_cutoff_at` must be exactly `"not-applicable"`; for resolved `project`, it must be a valid ISO-8601 timestamp with timezone. Partial project documents always use the latter.
- A complete document has `unread_thread_count: 0`; a partial document may use a positive value when task reads failed, otherwise `0`. For project documents, `read_thread_count <= in_scope_thread_count <= discovered_thread_count`; for current documents, all four task-scan counts and `source_thread_count` are `0`.
- `source_session_count` and `source_thread_count` equal the distinct matching rows in the source index; their row material counts sum to `material_count`. The rejection table sums to `rejected_candidate_count`, and `topic_count` equals the number of `### Txxx` sections.
- Every rendered source label must resolve to one source-index row, and every topic must use `已实现并保留` with a nonempty safe anchor. A mismatch in these relationships is malformed, not a best-effort document.

## Legacy schema requirements

Validate a schema-version-1 current source against these required fields:

```yaml
document_type: seo-session-materials
schema_version: 1
generated_by: extract-seo-materials
project: "<nonempty string>"
session_id: "<nonempty string>"
session_topic: "<nonempty string>"
extracted_at: "<valid timestamp>"
source_scope: "current-visible-conversation"
material_count: <nonnegative integer>
```

The prior generic source uses the same required fields with `generated_by: extract-session-seo-materials`. The original Web3 source uses `generated_by: extract-web3-seo-materials`, `document_type: web3-seo-session-materials`, and `Web3 实体` in place of `领域实体`.

Every accepted schema-version-1 source must contain one `## 会话摘要`, exactly `material_count` sequential `## Mxxx` sections, the controlled search-intent/contribution/fact/public-boundary fields, and the required user-problem, discussion, conclusion, user-significance, search-question, reusable-point, missing-material, and source-summary subsections from the session schema. It does not require the schema-version-2 workspace fields or product-anchor fields; re-apply the retention gate during the rebuild.

Validate a schema-version-1 canonical only for ownership, never as evidence. It requires:

```yaml
document_type: seo-project-summary
schema_version: 1
generated_by: extract-seo-materials
project: "<nonempty string>"
last_rebuilt_at: "<valid timestamp>"
source_session_count: <nonnegative integer>
topic_count: <nonnegative integer>
generated_only: true
```

It must also contain matching source-index and topic counts. A valid schema-version-1 canonical is current-owned. Any recognized schema-version-1 document missing these requirements is malformed and follows the conservative ownership rule above.

## Topic grouping

Group packages only when they share the same underlying user job, problem, and intent. Product wording may differ across sources. Treat platform, protocol, environment, or implementation variations as subcases when they answer the same question; split them when behavior changes the answer or user intent. Shared modules or entities alone never justify merging.

Do not force one material package to become one article. A summary topic may use one complete package or combine complementary packages from several sources.

## Claim merging and conflict handling

- Merge semantically equivalent claims and attach every supporting source label.
- Keep a narrower exception alongside a broader claim instead of deleting it.
- Record both sides of a contradiction. Mark a prior claim as superseded only when a later source explicitly establishes the revision.
- Preserve fact states. Repeated engineering conclusions do not become verified facts.
- Keep source labels on facts, conclusions, product behavior, failed experiences, limitations, risks, and conflict statements.
- In either mode, reject a claim that cannot be tied to the current retained product even when several sources repeat it.

## Current-product retention

Use current-workspace inspection only as an eligibility gate in both modes:

- `retained`: the conversation candidate maps to an implemented user-facing capability, behavior, limitation, or use case still present in the current workspace;
- `removed`: the capability was deleted, reverted, or belongs only to another checkout;
- `planned`: the source discusses an intention or experiment with no retained implementation;
- `uncertain`: the available current workspace cannot establish retention safely.

Only `retained` candidates enter a session source, canonical summary, scoped summary, or partial summary. Record safe rejection-reason counts for the other states. Repository content cannot create a candidate or upgrade a conversation fact state by itself.

## Content maturity

Apply this decision order:

1. Use `素材不足` when the topic lacks any one of a clear user problem, an explicit conclusion, or user significance; also use it when the topic consists only of hypotheses.
2. Otherwise use `可进入文章写作` only when all of these are true:
   - The user question and search intent are clear.
   - At least one verified fact or concrete discussed scenario supports the topic.
   - At least one explicit engineering conclusion or retained product response answers the user question.
   - At least one relevant risk, limitation, or failed path is recorded.
   - No unresolved conflict would change the core answer.
   - The core material is marked `可公开`; optional enrichment may still be missing.
3. Use `可形成内容简报` for every topic between those two states, including a supported topic with a blocking evidence gap, unresolved core conflict, or publication boundary.

Maturity describes source readiness only. It is not evidence of keyword demand or permission to publish.

## Atomic write and no-output rules

- For any invocation that may rebuild the canonical summary, use the fixed lock path `_content_materials/sessions/.project-seo-materials.lock`. Acquire it by exclusive creation (`O_CREAT|O_EXCL` or an equivalent atomic directory lock) before snapshotting summary inputs or deciding ownership. Store an invocation ID, host, PID, and acquisition timestamp in the lock, hold it through validation and installation, and release it only when the owner token matches. If the lock exists, wait and retry; take over only when its recorded owner is on the current host and its PID is confirmed no longer alive. If the metadata is missing, belongs to another host, or liveness is uncertain, do not delete it or rebuild unlocked—report a lock conflict.
- While holding the lock, inspect canonical ownership, assemble the full candidate in a unique same-directory temp file, and validate counts and citations. Immediately before installation, re-read the canonical target. If it changed since the ownership decision, preserve it and abort the replacement; re-evaluate ownership only to classify and report the conflict, never to continue installing that candidate.
- Install the validated unique temp over `project-seo-materials.md` with an atomic same-filesystem rename only after the lock-held ownership check succeeds. Never delete the old canonical first.
- The lock serializes `extract-seo-materials` invocations that honor this contract. If any external target change is observed, treat it as a conflict and abort the replacement. A non-cooperating process that writes in the final system-call interval after the last ownership check is outside this portable file-based concurrency guarantee; do not claim otherwise.
- On failure, remove only the current invocation's temp file, leave the canonical unchanged, and release the lock. Never remove or reuse another invocation's temp artifact.
- Assemble a scoped or partial result under a unique temporary name, validate it, then install it with an exclusive no-replace operation. On a final-name collision, select the next suffix and retry; never overwrite the winner. Apply the same exclusive final-name rule when creating a session source.
- A current run with no new qualifying conversation material creates no session source, but still rebuilds a permitted current-owned canonical summary from the complete accepted source set after re-applying the retention gate. Write a valid empty canonical when no retained material remains.
- A complete unfiltered project scan writes the canonical summary, including a valid empty canonical when no material qualifies, unless user-owned content blocks the canonical path.
- A complete topic-scoped project scan with qualifying material appends a scoped result and preserves the canonical; with no qualifying material it creates no file.
- A partial project scan with no qualifying material creates no partial document and preserves every existing canonical and legacy file.
