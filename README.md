# Extract SEO Materials

Turn product-development conversations into traceable SEO source material for OpenAI Codex.

[English](README.en.md) | [安装](#安装) | [使用方法](#使用方法) | [工作流程](#工作流程) | [输出结构](#输出结构) | [安全边界](#安全边界)

Extract SEO Materials 是一个 Codex Skill，用于从开发者在当前产品开发会话中，提取可复用、可追溯、可持续累积的 SEO 初始素材。

如果当前会话存在合格素材，一次运行会先生成一份带时间戳的素材文档，再读取同一项目内已有的会话素材，完整重建唯一的项目汇总。不同会话不需要直接互相读取；它们通过项目目录中的 Markdown 文件共同补充同一个主题。

它保存的重点不是代码本身，而是开发过程中最容易流失的内容：用户遇到的问题、具体场景、原理解释、工程结论、验证证据、失败方案、风险限制，以及用户可能如何搜索这些问题。

它不会直接撰写 SEO 文章，也不会生成搜索量、关键词难度或 SERP 结论。

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

默认安装位置为：

```text
~/.codex/skills/extract-seo-materials
```

安装完成后，在新的 Codex 任务中使用该 Skill。

## 使用方法

显式调用：

```text
使用 $extract-seo-materials 总结当前会话的 SEO 内容素材，并重建项目汇总。
```

也可以直接使用通俗表达触发：

- 总结当前会话 SEO 素材
- 提取当前会话 SEO 内容素材
- 汇总当前会话 SEO 素材
- SEO 内容素材
- SEO 素材
- 沉淀本次开发内容

建议在一个开发任务结束、关键结论已经形成后运行一次。

## 工作流程

一次调用严格执行两个阶段。

### 阶段一：提取当前会话

- 只使用当前可见的开发者–Agent 对话。
- 围绕普通用户可感知的问题组织素材，而不是围绕代码改动罗列日志。
- 一次运行最多新增一份会话文档；同一会话可以包含多个用户问题素材包。
- 没有达到标准的素材时，不创建会话文档，但仍继续重建项目汇总。
- 不读取其他 Codex 会话，不为补充素材而扫描代码仓库。

### 阶段二：重建项目汇总

- 只读取当前项目 `_content_materials/sessions/` 中由该 Skill 生成的会话文档。
- 根据底层用户问题与搜索意图进行主题聚合。
- 合并重复结论，同时保留所有来源编号。
- 遇到跨会话修订或冲突时同时记录，不静默覆盖旧结论。
- 每次从全部会话来源完整重建唯一汇总，不把旧汇总再次作为输入。

这个文件协作方式使同一个项目中的多个独立开发会话，可以逐步补齐同一篇 SEO 内容所需的素材。

## 输出结构

运行产物始终保存在当前项目中：

```text
_content_materials/
├── sessions/
│   ├── 20260817-153045-login-timeout.md
│   ├── 20260818-101230-session-recovery.md
│   └── ...
└── summary/
    └── project-seo-materials.md
```

- `sessions/` 中的文档是带时间戳的历史来源，只新增，不自动覆盖或删除。
- `project-seo-materials.md` 是唯一的派生汇总，每次运行都会完整重建。
- 汇总中的关键事实、结论、失败经验和限制均使用 `[S001]`、`[S002]` 等编号追溯到来源会话。
- 汇总文档由 Skill 自动生成，人工编辑会在下次成功重建时被覆盖。

每个素材包可以记录：

- 用户问题与具体场景
- 产品、模块与领域实体
- 本次讨论和明确结论
- 贡献类型与事实状态
- 对普通用户的意义
- 搜索意图与自然搜索问法
- 可继续用于内容创作的关键点
- 尚缺证据或需要其他会话补充的部分

事实状态严格保留为：`已验证事实`、`工程结论`、`待验证假设` 或 `失败方案`。项目汇总会将主题成熟度标记为：`素材不足`、`可形成内容简报` 或 `可进入文章写作`。

完整字段与合并规则见 [output contract](references/output-contract.md)。

## 安全边界

以下内容不会写入素材文档：

- API Key、Token、凭证和私有端点
- 个人数据或可关联身份的账户与地址
- 可直接利用的漏洞细节
- 当前会话没有明确讨论过的实现事实
- 从外部 SEO 服务推测的搜索量、关键词难度或 SERP 结论

未发布功能或商业敏感决策只保留必要摘要，并标记为 `发布前确认`。

## 适用范围

该 Skill 可用于 Web3、SaaS、开发者工具、电商或其他产品领域，不依赖特定行业。

它负责沉淀 SEO 内容素材，不负责文章正文、编辑审核、内容发布或效果监测。当前工作目录是项目边界，不进行跨仓库汇总。

---

Extract SEO Materials is an independent community project. It is not affiliated with or endorsed by OpenAI.
