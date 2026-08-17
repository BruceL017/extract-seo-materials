# Output contract

Use these exact structures. Quote free-text YAML values. Keep counts numeric.

## Directory contract

```text
_content_materials/
├── sessions/
│   └── YYYYMMDD-HHmmss-session-topic.md
└── summary/
    └── project-seo-materials.md
```

Treat `sessions` as append-only. Treat the summary as generated-only and replace it completely on every successful rebuild.

## Session document

```markdown
---
document_type: seo-session-materials
schema_version: 1
generated_by: extract-seo-materials
project: "<project-directory-name>"
session_id: "<YYYYMMDD-HHmmss-session-topic>"
session_topic: "<short Chinese topic>"
extracted_at: "<ISO-8601 timestamp with timezone>"
source_scope: "current-visible-conversation"
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

<Summarize the part of the current visible conversation that supports this package without copying dialogue.>
```

Continue with `M002`, `M003`, and so on inside the same file. `material_count` must equal the number of `## Mxxx` sections.

## Project summary document

```markdown
---
document_type: seo-project-summary
schema_version: 1
generated_by: extract-seo-materials
project: "<project-directory-name>"
last_rebuilt_at: "<ISO-8601 timestamp with timezone>"
source_session_count: <integer>
topic_count: <integer>
generated_only: true
---

# 项目 SEO 素材总表

> 此文件由会话素材完整重建。请勿直接编辑；下一次运行会覆盖人工修改。

## 汇总概况

- 最后重建：<timestamp>
- 来源会话：<count>
- SEO 主题：<count>

## 来源索引

| 引用 | 会话文件 | 提取时间 | 会话主题 | 素材数 |
|---|---|---|---|---:|
| [S001] | `<filename>` | <timestamp> | <topic> | <count> |

Use `暂无来源会话。` instead of a table row when the count is zero.

## SEO 主题

### T001｜<normalized user-first topic>

- 内容成熟度：`素材不足 | 可形成内容简报 | 可进入文章写作`
- 搜索意图：`<one or more controlled intents>`
- 用户可能搜索：`<deduplicated natural questions>`
- 产品关联：`<product/module relationship>`
- 领域实体：`<relevant entities or 无>`
- 覆盖来源：`[S001] [S003]`

#### 用户问题

<Consolidated user problem and scenario.> [Sxxx]

#### 跨会话结论与证据

- `[已验证事实]` <deduplicated claim> [Sxxx] [Syyy]
- `[工程结论]` <deduplicated claim> [Sxxx]
- `[待验证假设]` <unresolved claim> [Syyy]

#### 解决方案与产品关联

- <How the product responds to the problem, without promotional copy.> [Sxxx]

#### 失败经验、风险与限制

- <Relevant failed path, caution, or boundary.> [Sxxx]

#### 结论变化或冲突

- <Describe competing or revised conclusions with dates and sources.>

Use `未发现跨会话冲突。` when none exists.

#### 当前素材缺口

- <Missing evidence, examples, limitations, or user explanation.>

Use `无关键缺口。` only when the maturity rules support it.

#### 推荐内容角度

- <A user-first SEO content angle, not an article draft.>
```

Continue with `T002`, `T003`, and so on. If no topics exist, write `暂无可汇总的 SEO 主题。` under `## SEO 主题`.

## Source acceptance and legacy compatibility

- Accept only direct children of `_content_materials/sessions/` with an `.md` suffix and `schema_version: 1`.
- Accept the current marker pair: `generated_by: extract-seo-materials` with `document_type: seo-session-materials`.
- Also accept the prior generic marker pair: `generated_by: extract-session-seo-materials` with `document_type: seo-session-materials`.
- Also accept the original Web3 marker pair: `generated_by: extract-web3-seo-materials` with `document_type: web3-seo-session-materials`. Map its `Web3 实体` field to the current `领域实体` field during aggregation without modifying the legacy source.
- Ignore foreign Markdown and report it; do not treat it as content evidence.
- Treat a source containing any recognized generator (`extract-seo-materials`, `extract-session-seo-materials`, `extract-web3-seo-materials`) or recognized document type (`seo-session-materials`, `web3-seo-session-materials`) as blocking when the exact pair is incomplete or mismatched. Missing required metadata, mismatched counts, malformed material sections, or unreadable content are also blocking. Preserve the old summary instead of rebuilding from a partial source set.

## Topic grouping

Group packages only when they share the same underlying user job, problem, and intent. Product wording may differ across sessions. Treat platform, protocol, environment, or implementation variations as subcases when they answer the same question; split them when behavior changes the answer or the user intent. Shared modules or entities alone never justify merging.

Do not force one material package to become one article. A summary topic may use one complete package or combine complementary packages from many sessions.

## Claim merging and conflict handling

- Merge semantically equivalent claims and attach every supporting source label.
- Keep a narrower exception alongside a broader claim instead of deleting it.
- Record both sides of a contradiction. Mark a prior claim as superseded only when a later source explicitly establishes the revision.
- Preserve fact states. Repeated engineering conclusions do not become a verified fact.
- Keep source labels on facts, conclusions, product behavior, failed experiences, limitations, risks, and conflict statements.

## Content maturity

Apply this decision order:

1. Use `素材不足` when the topic lacks any one of: a clear user problem, an explicit conclusion, or user significance; also use it when the topic consists only of hypotheses.
2. Otherwise use `可进入文章写作` only when all of these are true:
   - The user question and search intent are clear.
   - At least one verified fact or concrete discussed scenario supports the topic.
   - At least one explicit engineering conclusion or product response answers the user question.
   - At least one relevant risk, limitation, or failed path is recorded.
   - No unresolved conflict would change the core answer.
   - The core material is marked `可公开`; optional examples or enrichment may still be missing.
3. Use `可形成内容简报` for every topic between those two states, including a supported topic with a blocking evidence gap, unresolved core conflict, or publication boundary.

Maturity describes source readiness only. It is not evidence of keyword demand or permission to publish.
