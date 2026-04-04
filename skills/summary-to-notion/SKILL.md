---
name: summary-to-notion
description: 把已经完成的摘要、快报、网页总结、推文总结、会议纪要同步到 Notion 页面或数据库。当用户说“同步到 Notion”“记到 Notion”“存到知识库”“写入 Notion 数据库”“同步过去”时使用。它适合作为所有总结类 skill 的统一落点，不负责提取原文，只负责把现成总结整理并写入 Notion。遇到用户已经有固定数据库 schema（如 Keywords、ReportDate、Author、PublishedDate、KeyPoints）时，优先使用这个 skill 做结构化字段映射，而不是只写标题和摘要。
---

# Summary To Notion

用这个 skill 统一处理“把总结写进 Notion”的动作。它面向已经产出的内容，例如中文快报、网页总结、推文摘要、会议纪要、研究笔记。

## When To Use

- 用户已经拿到摘要，接下来要同步到 Notion。
- 用户明确提到 `Notion`、`知识库`、`数据库`、`归档`、`沉淀`。
- 用户提到要补齐或映射结构化字段，比如：`Keywords`、`ReportDate`、`Author`、`PublishedDate`、`ContentType`、`KeyPoints`。
- 上游 skill 已经完成正文提取或总结，不要在这里重新做内容分析。

## Inputs

同步前尽量整理好这些信息：
- 标题
- 摘要正文 Markdown
- 原始来源链接（可选）
- 核心要点（可选）
- 关键词列表（可选）
- 作者（可选）
- 原文发布时间（可选）
- 归档日期 / ReportDate（可选，建议默认当天）
- 内容类型（可选，如 `X Article` / `Blog Post` / `Tweet`）
- 来源渠道（可选，如 `Other` / `Hacker News`）
- 分数字段（可选）
- Why it matters / Takeaway（可选）

## Environment

凭据和目标只从环境变量读取，不要硬编码到 skill 文件。

- `NOTION_TOKEN` 或 `NOTION_API_KEY`
- `NOTION_DATABASE_ID` 或 `NOTION_PARENT_PAGE_ID`

推荐优先配置数据库：
- 有 `NOTION_DATABASE_ID` 时，先尝试写入数据库
- 数据库失败且存在 `NOTION_PARENT_PAGE_ID` 时，回退为在父页面下创建普通页面
- 只有 `NOTION_PARENT_PAGE_ID` 时，直接创建子页面

## Workflow

1. 确认上游已经完成总结，不在这里重新抓取或分析。
2. 把摘要内容写入一个临时 Markdown 文件。
3. 如果有核心要点，单独写成一个临时文件，传给 `--keypoints-file`。
4. 让脚本先读取目标 database schema，优先自动匹配真实列名；只有自动匹配不准时，才显式传 property 名称。
5. 调用 `scripts/sync_to_notion.py` 执行同步。
6. 成功后回传 Notion 页面链接；失败时返回 API 错误正文，方便用户修正权限、schema 或 select options。

## Command

最小写入：

```bash
python3 scripts/sync_to_notion.py \
  --title "<标题>" \
  --source-url "<来源链接>" \
  --summary-file "<摘要 markdown 文件>"
```

如果有结构化字段，一并传：

```bash
python3 scripts/sync_to_notion.py \
  --title "<标题>" \
  --source-url "<来源链接>" \
  --summary-file "<摘要 markdown 文件>" \
  --keypoints-file "<关键要点文件>" \
  --keywords "AI,代码代理,软件工程" \
  --author "Harrison Chase" \
  --source "Other" \
  --content-type "X Article" \
  --published-date "2026-03-09" \
  --report-date "2026-03-12" \
  --score "4" \
  --why-it-matters "执行变便宜后，判断力和 review 成为瓶颈。"
```

如果数据库列名不是常见默认名，再显式覆盖：

```bash
--title-property "Title"
--url-property "URL"
--summary-property "Summary"
--keypoints-property "KeyPoints"
--keywords-property "Keywords"
--report-date-property "ReportDate"
--published-date-property "PublishedDate"
--author-property "Author"
--source-property "Source"
--content-type-property "ContentType"
--score-property "Score"
--why-it-matters-property "WhyItMatters"
```

如果要先看 schema：

```bash
python3 scripts/sync_to_notion.py --title x --summary-file /tmp/a.md --print-schema
```

## Schema Matching Rules

脚本会优先尝试自动匹配这些常见字段：

- `Title` / `Name`
- `URL` / `Source URL` / `Link`
- `Summary` / `Abstract`
- `KeyPoints` / `Key Points` / `Highlights`
- `Keywords` / `Tags` / `Topics`
- `ReportDate` / `Report Date`
- `PublishedDate` / `Published Date` / `Date`
- `Author` / `Authors`
- `Source` / `Channel`
- `ContentType` / `Content Type` / `Type`
- `Score` / `Importance` / `Priority`
- `WhyItMatters` / `Why It Matters` / `Takeaway`

自动匹配的目的，是让 skill 适配不同 Notion 数据库，而不是把列名写死在 prompt 里。

## Output Contract

- 成功时返回 JSON，包含：
  - `mode`: `database` 或 `page`
  - `page_id`
  - `url`
  - `properties_written`
- 失败时直接保留 Notion API 返回正文，便于判断是权限、页面共享、数据库列名、select options 还是目标 ID 问题

## Handoff Rules

- `x-brief-cn` 产出中文快报后，如用户确认同步，交给 `$summary-to-notion`。
- `content-summary` 产出结构化摘要后，如用户要求归档到 Notion，交给 `$summary-to-notion`。
- 如果上游 skill 已有结构化 metadata（author / keywords / dates / keypoints），不要丢掉，直接映射到 Notion。
- 其他总结类 skill 也应复用这个入口，而不是各自维护一份 Notion 写入脚本。
