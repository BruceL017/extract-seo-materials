# Extract SEO Materials

从当前开发会话或当前项目的全部 Codex 会话中，提取可追溯的中文 SEO 内容素材。

[English](README.en.md) | [安装](#安装) | [使用方式](#使用方式) | [来源模式](#来源模式) | [输出结构](#输出结构) | [安全边界](#安全边界)

该 Skill 保存用户问题、产品场景、原理解释、工程结论、验证证据、失败方案、风险限制和自然搜索问法。它只生成内容素材，不撰写营销文章，也不提供搜索量、关键词难度或 SERP 结论。

## 安装

在 Codex 中使用内置的 `$skill-installer`：

```text
使用 $skill-installer 安装 https://github.com/BruceL017/extract-seo-materials，Skill 位于仓库根目录。
```

也可以运行安装脚本：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo BruceL017/extract-seo-materials \
  --path . \
  --name extract-seo-materials
```

默认安装到：

```text
~/.codex/skills/extract-seo-materials
```

## 使用方式

当前会话模式：

```text
使用 $extract-seo-materials 提取当前会话的 SEO 素材。
```

项目模式：

```text
使用 $extract-seo-materials 扫描当前项目的所有会话，重建项目 SEO 素材。
```

限定主题：

```text
使用 $extract-seo-materials 扫描当前项目会话，只提取与用户登录故障有关的 SEO 素材。
```

也可以直接说“SEO 素材”或“沉淀开发内容”。在没有可提取开发证据的新项目会话中，默认执行项目模式；当前会话已有提取请求之外的产品开发证据时，默认处理当前会话。

项目模式未指定主题时汇总全部合格素材；只有用户明确指定主题时才在完整读取所有项目会话后缩小结果范围。

## 来源模式

| 模式 | 来源 | 仓库检查 |
|---|---|---|
| `current` | 当前可见会话 | 只读确认候选是否属于当前保留产品 |
| `project` | 本机持久化记录中属于当前 checkout 的 Codex 会话 | 只读确认候选是否属于当前保留产品 |
| `auto` | 根据明确措辞和当前会话是否已有开发证据选择 | 跟随解析后的模式 |

项目扫描只覆盖当前项目目录：

- Git 项目以当前 checkout/worktree 为边界；
- 非 Git 项目使用 Codex 项目身份和规范化目录路径；
- 排除其他 clone、worktree、兄弟目录和嵌套仓库；
- 不根据标题、摘要或同名文件夹猜测归属；
- 通过 Codex 状态数据库和 active/archived rollout 的 `session_meta.cwd` 建立全量清单，不依赖可能截断的全局任务列表；
- 逐会话提炼后再跨会话去重、补充和处理冲突。

仓库内置的 `scripts/project_sessions.py` 只输出会话 ID、范围元数据和覆盖状态，不输出对话正文。若持久化记录缺失、损坏或无法读取，扫描会标记为 `partial`，不会用最近任务列表把它误判为完整结果。

会话负责提供用户问题、设计原因和工程讨论；当前工作区只负责确认相关功能、行为或限制仍然实现并保留。代码中存在但会话没有讨论的内容，不会被凭空扩展为 SEO 素材。

## 内容门槛

两种模式的素材都必须同时满足：

1. 会话中存在具体的用户问题、场景、结论、限制、失败方案或明确假设；
2. 内容具有用户可感知的意义，而不是普通调试或代码日志；
3. 对应能力、行为、限制或用例仍保留在调用时的当前工作区；
4. 内容能够在移除敏感信息后安全保存。

当前工作区包括已提交、已暂存、未暂存和未被忽略的产品文件。Skill 不切换分支、不拉取远端、不运行测试或应用，也不使用代码创造会话中不存在的素材。

## 输出结构

所有文件都直接保存在同一个目录，通过文件名和 `document_type` 严格区分：

```text
_content_materials/
└── sessions/
    ├── 20260817-153045-session-login-timeout.md
    ├── project-seo-materials.md
    ├── 20260818-101230-project-seo-materials-login-failure.md
    ├── 20260818-101530-project-seo-materials.partial.md
    └── 20260818-101530-project-seo-materials-login-failure.partial.md
```

- `*-session-<topic>.md`：当前会话模式生成的追加式来源，`document_type: seo-session-materials`。
- `project-seo-materials.md`：唯一权威项目总表，`document_type: seo-project-summary`。
- `*-project-seo-materials-<topic>.md`：用户明确限定主题后的完整结果，`document_type: seo-project-summary-scoped`。
- `*-project-seo-materials.partial.md`：未限定主题的部分结果，`document_type: seo-project-summary-partial`。
- `*-project-seo-materials-<topic>.partial.md`：主题限定的部分结果，`document_type: seo-project-summary-scoped-partial`。

未指定主题且扫描完整时，Skill 原子重建项目总表；若没有合格素材，则写入权威的空总表，避免已经删除的产品内容继续残留。如果权威路径已被非 Skill 内容占用，则保留该文件并报告冲突。明确指定主题时，完整结果使用带时间戳的独立文件，不会用窄范围结果覆盖全量总表；若该主题没有合格素材，则不生成文件，只报告淘汰原因。扫描不完整但存在合格素材时，只新增 partial 文件；扫描不完整且没有合格素材时不生成 partial 文件，并报告淘汰原因。

项目总表、主题限定结果、partial 文件和临时文件永远不会被再次读取为素材来源，因此不会形成“汇总引用汇总”的循环。

如果项目仍存在旧的 `_content_materials/summary/project-seo-materials.md`，Skill 会保留并报告它，但不会读取、移动、修改或删除。新的权威路径始终是 `_content_materials/sessions/project-seo-materials.md`。

## 可追溯性

每个主题保留来源编号、事实状态、产品锚点、冲突、素材缺口和成熟度：

- 事实状态：`已验证事实`、`工程结论`、`待验证假设`、`失败方案`；
- 成熟度：`素材不足`、`可形成内容简报`、`可进入文章写作`；
- 扫描覆盖：`complete` 或 `partial`。

完整字段、来源所有权和合并规则见 [output contract](references/output-contract.md)。

## 安全边界

Skill 不会：

- 保存 API Key、Token、凭证、个人数据、私有端点或可利用漏洞细节；
- 暴露系统/开发者指令、隐藏推理、内部 Agent 通信、绝对私有路径或完整会话；
- 扫描其他 checkout、仓库或主机；
- 浏览网页、调用 SEO 数据服务或声称存在搜索需求；
- 撰写、发布营销文章，或提交、推送代码。

未发布或商业敏感内容只有在当前产品仍保留且确有必要时才会最小化保存，并标记为 `发布前确认`。

---

Extract SEO Materials is an independent community project. It is not affiliated with or endorsed by OpenAI.
