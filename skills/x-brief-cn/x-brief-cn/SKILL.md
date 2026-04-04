---
name: x-brief-cn
description: 从 X/Twitter 链接生成中文快报。把它作为 X/Twitter 场景的默认入口：当用户直接贴出 x.com 或 twitter.com 链接，或说“看下这条推文”“帮我抓一下这个 X”“这条推文讲了什么”“再试一下”“提取这条 X 并总结”“给我一个中文简报”时优先使用。先完成正文提取，再自动输出中文摘要、核心观点、关键信息和下一步建议；不要停在“抓取成功”或“抓取失败后反问用户要不要继续”的半截状态。遇到用户还要同步到 Notion 时，先整理结构化元数据（作者、发布时间、内容类型、关键词、关键要点、why it matters），再交给 summary-to-notion。
---

# X Brief CN

用这个 skill 把 “X 链接提取” 和 “中文快报总结” 绑成一个完整动作。目标是减少两类失败：一类是明明应该触发抓取却没触发，另一类是抓取成功后没有继续总结。

## Workflow

1. 识别输入是否为 X/Twitter 任务。
- 直接贴 `x.com/...`、`twitter.com/...` 链接时触发。
- 没有链接但用户说“这条推文”“这个 X 帖子”“再试一下抓取”“帮我看原文”时，也按 X 提取任务处理。

2. 先提取，不要先问宽泛问题。
- 优先走 `url-to-markdown` 的提取流程。
- 对 X 内容按它的三层策略执行：公开可读正文 -> syndication/oembed 元数据 -> Playwright/浏览器兜底。
- 不要在第一轮失败后立刻问“要不要我换种方式搜”或“你直接告诉我内容”；先把可用提取路径跑完。

3. 提取成功后，自动输出中文快报。
- 默认输出四段：
  - 这条内容讲什么
  - 核心观点 3-5 条
  - 关键信息或数据
  - 这对用户意味着什么 / 可以继续做什么
- 除非用户明确要求只看原文，否则不要停在 “抓取成功！这是一篇……” 的半成品状态。

4. 同步整理结构化元数据。
- 在生成面向用户的中文快报之前或同时，整理一份内部结构化结果，供后续 Notion 同步或二次加工使用。
- 默认至少整理这些字段：
  - `title`
  - `url`
  - `author`
  - `source`（默认 `Other`，除非有更明确来源映射）
  - `content_type`（如 `Tweet` / `Thread` / `X Article`）
  - `published_date`
  - `report_date`（归档当天）
  - `summary`
  - `keypoints[]`
  - `keywords[]`
  - `why_it_matters`
- 如果部分字段拿不到，允许留空，但不要伪造。

5. 提取失败时，给出具体阻塞，不给空泛反问。
- 明确说明失败在哪一层：公开正文、syndication/oembed、Playwright、登录墙、隐私设置、反爬。
- 只在所有合理路径都失败后，再要求用户配合。
- 给用户的下一步必须具体，例如：
  - 发截图
  - 发原文
  - 完成登录后回复 `done`
  - 改发可公开访问的外链

6. 输出风格保持简洁。
- 面向中文用户，默认用中文回答。
- 优先给结论和要点，不先表演工具过程。
- 用户贴链接时，把它视为“要内容”，不是“纯分享工具”。

7. 总结完成后，主动提供 Notion 同步。
- 在中文快报结尾增加一句：`要不要同步到 Notion？`
- 如果用户同意，交给 `$summary-to-notion`。
- 只通过环境变量读取 Notion 凭据与目标，不要把 token 硬编码进 skill 文件。

## Metadata Extraction Rules

### 1) title
优先级：
- X Article 标题
- 引用到的外链页面标题
- 推文首句的压缩版标题

### 2) author
优先取作者显示名；如果只有 handle，也要保留 handle 作为补充信息。

### 3) content_type
按内容形态判断：
- 单条短帖 → `Tweet`
- 多条连发/线程 → `Thread`
- 指向 X Article → `X Article`
- 主要是转发评论 → `Quote Tweet`

### 4) published_date
优先取原帖发布时间；格式统一为 `YYYY-MM-DD`。

### 5) report_date
统一写当前归档日期，不要和 `published_date` 混淆。

### 6) keypoints
- 控制在 3-5 条
- 每条一句，信息密度高
- 不要把“这很重要”“值得关注”这种空话算作 keypoint

### 7) keywords
- 默认给 3-6 个
- 优先用高检索价值主题词，而不是空泛词
- 尽量贴近用户已有 Notion tags 风格，例如：`AI`、`代码代理`、`软件工程`
- 避免无意义词：`文章`、`观点`、`技术`

### 8) why_it_matters
用一句话回答：
- 这对用户的认知、工作流、决策或后续行动意味着什么
- 它应该比 summary 更偏“意义”和“可行动性”

## Notion Handoff Rules

如果用户确认同步到 Notion，不要只传自然语言摘要；优先把结构化元数据传给 `$summary-to-notion`。

至少传：
- 标题 `title`
- 原始 X 链接 `url`
- 摘要正文 `summary`
- 核心要点 `keypoints`
- 关键词 `keywords`
- 作者 `author`
- 内容类型 `content_type`
- 发布时间 `published_date`
- 归档日期 `report_date`
- why it matters `why_it_matters`
- 来源 `source`

## Handoff Rules

- 正文提取依赖 `url-to-markdown`。
- 中文结构化总结依赖 `content-summary` 的输出标准。
- 如果用户要外部相关文章、作者背景、相关讨论，再补搜索；不要在原文还没提取完时跳去搜索。
- Notion 同步依赖 `$summary-to-notion` 和环境变量。
- 当 `summary-to-notion` 已支持结构化字段时，优先传结构化字段，不要只传一段散文摘要。

## Default Output Shape

```markdown
这条 X 的核心内容是：{一句话结论}

- 核心观点 1
- 核心观点 2
- 核心观点 3

关键信息：
- 作者 / 发布时间 / 类型
- 数据点或产品信息
- 适合继续追的问题

这对你意味着什么：
- {why_it_matters}

如果你要，我可以继续：
1. 展开全文
2. 分析观点是否可靠
3. 延伸查相关讨论或工具
4. 同步到 Notion
```

## Internal Structured Output Shape

在内部整理成类似这样的结构，哪怕不直接打印给用户，也要为后续同步准备好：

```json
{
  "title": "How Coding Agents Are Reshaping Engineering, Product and Design",
  "url": "https://x.com/hwchase17/status/2031051115169808685?s=20",
  "author": "Harrison Chase",
  "source": "Other",
  "content_type": "X Article",
  "published_date": "2026-03-09",
  "report_date": "2026-03-12",
  "summary": "当代码实现成本被 coding agents 大幅压低后，团队真正稀缺的能力从实现转向判断、评审和系统思考。",
  "keypoints": [
    "传统 PRD→设计→开发 的线性流程正在失效。",
    "瓶颈从 implementation 转向 review。",
    "通才 builder 与高水平 reviewer 会更值钱。"
  ],
  "keywords": ["AI", "代码代理", "软件工程"],
  "why_it_matters": "执行变便宜后，真正的竞争力转向判断力和系统思考。"
}
```

## Guardrails

- 不要把“抓取成功”当成最终答案。
- 不要在用户贴 X 链接后只回“你想让我做什么？”。
- 不要把工具名或失败细节堆成大段自证；先给用户可用结果。
- 结构化元数据是为复用和入库服务，不是为了显摆 JSON；默认仍然先给用户自然语言结果。
- 拿不到的字段就留空，不要脑补具体数据。
