---
name: news-aggregator-safe
description: "news-aggregator-skill 的安全包装层。当用户需要使用 news-aggregator-skill 或类似新闻聚合技能时自动触发，负责验证时间戳、限制信源、审计输出、防止陈旧数据/幻觉/供应链投毒。不替代原技能，而是在外层加护栏。"
---

# News Aggregator Safe Wrapper

**定位**：news-aggregator-skill 的安全包装层（wrapper），不是替代品。

**核心职责**：在调用原技能前后加护栏，防止：
- 陈旧缓存数据被当作实时新闻
- 时间戳格式化错误导致 AI 误判
- 信源爬虫失效导致 AI 幻觉补全
- 供应链投毒（恶意脚本执行）
- 输出未经校验直接呈现给用户

---

## 使用方式

用户触发词：
- "跑一份新闻早报"
- "看看今天 HN 有什么"
- "生成科技日报"
- 任何调用 news-aggregator-skill 的请求

**本 wrapper 自动接管**，按以下流程执行。

---

## 安全协议（四层护栏）

### 第一层：环境预检

在执行任何命令前，验证：

```bash
# 1. 检查 skill 是否存在且路径正确
ls -la <skill-path>/SKILL.md

# 2. 检查 requirements.txt 是否有可疑依赖
grep -E "^(os|sys|subprocess|eval|exec|pickle|marshal)" <skill-path>/requirements.txt

# 3. 检查 scripts/ 下是否有可疑脚本
find <skill-path>/scripts -name "*.py" -exec grep -l "eval\|exec\|__import__\|base64" {} \;

# 4. 确认当前日期（用于后续校验）
date +%Y-%m-%d
```

**红线**：如果发现 `eval()`、`exec()`、`base64 -d | bash` 等，立即停止并报告用户。

---

### 第二层：信源白名单

**默认只允许以下稳定信源**（可被用户显式覆盖）：

| 信源 | Key | 稳定性 | 备注 |
|------|-----|--------|------|
| Hacker News | `hackernews` | ✅ 高 | 有 Algolia API + 页面 fallback |
| GitHub Trending | `github` | ✅ 高 | 官方页面 |
| Hugging Face Papers | `huggingface` | ✅ 高 | 官方 API |
| V2EX | `v2ex` | 🟡 中 | 国内，偶尔反爬 |
| Product Hunt | `producthunt` | 🟡 中 | 偶尔改版 |

**默认禁用信源**（需用户显式请求 + 二次确认）：
- `weibo`（反爬严，易失效）
- `wallstreetcn`（时间戳曾出 bug）
- `36kr`（反爬严）
- `tencent`（反爬严）
- 所有聚合类信源（`ai_newsletters`、`podcasts`、`essays`）

**用户显式请求时**（如"帮我跑一份微博热搜"）：
1. 告知用户该信源稳定性等级
2. 告知可能失败或数据延迟
3. 用户确认后再执行

---

### 第三层：输出校验

原技能执行后，**必须**通过以下校验才能呈现给用户：

#### 3.1 时间戳校验

```python
# 伪代码逻辑
for item in report:
    # 检查时间字段格式
    if item.time matches "HH:MM" and not "YYYY-MM-DD":
        flag("时间戳丢失日期信息，可能误判")
    
    # 检查是否陈旧数据
    if item.date < (today - 2 days):
        flag("发现超过 2 天的旧闻，可能缓存污染")
    
    # 检查"X 小时前"是否合理
    if item.time contains "小时前":
        计算实际小时差 = now - item.timestamp
        if abs(计算实际小时差 - 报告小时差) > 3:
            flag("时间计算错误，实际差{X}小时，报告说{Y}小时")
```

#### 3.2 数据完整性校验

```python
# 检查是否有空数据
if len(report.items) == 0:
    flag("信源返回 0 条数据，可能爬虫失效")
    # 不允许 AI 幻觉补全，直接报告失败

# 检查是否有必填字段缺失
for item in report.items:
    if not item.title or not item.url:
        flag("条目缺少标题或链接，可能解析失败")
```

#### 3.3 幻觉检测

```python
# 检查是否有 AI 自行添加的内容
if report contains:
    - "据分析"
    - "可以看出"
    - "综上所述"
    - "值得注意的是"
    - 任何不在原数据中的"解读"
    flag("检测到 AI 自行添加的解读，可能幻觉")
```

---

### 第四层：熔断机制

满足任一条件时，**立即停止**并报告用户：

| 触发条件 | 熔断动作 |
|----------|----------|
| 时间戳校验失败 ≥ 3 条 | 停止，报告"时间戳异常，可能缓存污染" |
| 信源返回 0 条数据 | 停止，报告"信源失效，建议切换信源" |
| 检测到 eval/exec/base64 | 停止，报告"发现可疑代码，已阻断" |
| 输出包含"据分析/可以看出"等 | 停止，要求原技能重新生成（禁止自行解读） |
| 文件写入位置不在 `reports/YYYY-MM-DD/` | 停止，报告"写入路径异常" |

---

## 标准工作流程

### Step 1: 接收请求

用户说："帮我跑一份科技早报"

**本 wrapper 响应**：
> 收到。我将使用 news-aggregator-skill，默认信源：HN + GitHub + HuggingFace。
> 
> 预计执行时间：2-3 分钟。
> 
> 是否需要添加其他信源？（可选：V2EX、Product Hunt、微博热搜*、华尔街见闻*）
> *标注信源需二次确认

---

### Step 2: 环境预检

执行第一层检查，输出：
```
✅ SKILL.md 存在
✅ 无 eval/exec 依赖
✅ 脚本无 base64/eval 调用
✅ 当前日期：2026-03-09
```

如有异常，立即停止。

---

### Step 3: 执行原技能

```bash
cd <skill-path>
python3 scripts/fetch_news.py --source hackernews,github,huggingface --limit 10 --no-save
```

**关键**：捕获 stdout 输出，不依赖生成的 Markdown 文件（防止缓存污染）。

---

### Step 4: 输出校验

对原始 JSON/输出执行第三层校验。

**通过** → 进入 Step 5
**失败** → 触发熔断，报告用户具体失败原因

---

### Step 5: 呈现给用户

格式：

```markdown
## 📰 科技早报 | 2026-03-09

**信源**：Hacker News, GitHub, HuggingFace  
**生成时间**：2026-03-09 23:07  
**校验状态**：✅ 时间戳正常 | ✅ 无陈旧数据 | ✅ 无幻觉内容

---

### Hacker News (5 条)

1. [标题](url) - 🔥 123 points - 2h ago
   - 摘要：...

### GitHub Trending (5 条)
...

---

**备注**：所有时间已校验，无缓存污染。
```

---

## 特殊情况处理

### 情况 1：原技能返回 0 条数据

**不**让 AI 自行发挥补全。

**正确做法**：
> ❌ Hacker News 信源返回 0 条数据（可能 API 失效或网络问题）
> 
> 建议：
> 1. 切换到页面抓取模式（成功率较低）
> 2. 更换信源（GitHub、HuggingFace 仍可用）
> 3. 稍后重试

---

### 情况 2：时间戳校验失败

> ⚠️ 检测到时间戳异常
> 
> 问题：3 条新闻显示"1h ago"，但实际时间戳是 12 小时前
> 根因：原技能只输出 HH:MM 格式，丢失日期信息
> 
> 已过滤异常条目，剩余 7 条正常新闻：
> [呈现正常部分]

---

### 情况 3：用户要求禁用信源

用户："不要用 wrapper，直接跑原技能"

**响应**：
> 可以，但请注意以下风险：
> 1. 陈旧缓存数据可能被当作实时新闻
> 2. 时间戳错误不会被检测
> 3. AI 可能自行"解读"新闻
> 
> 确认要绕过安全协议吗？[是/否]

用户确认后，直接调用原技能，但**仍保留熔断机制**（ eval/exec 检测不可关闭）。

---

## 安装与配置

### 安装

```bash
# 方法 1：手动安装
git clone git@github.com:Liubo111111111/pi-skills.git
cp pi-skills/skills/news-aggregator-safe ~/.openclaw/workspace/skills/

# 方法 2：等待 clawhub 发布（待发布）
clawhub install news-aggregator-safe
```

### 依赖

无需额外依赖，复用 news-aggregator-skill 的 `requirements.txt`。

### 配置

可选配置文件 `~/.openclaw/workspace/skills/news-aggregator-safe/config.json`：

```json
{
  "default_sources": ["hackernews", "github", "huggingface"],
  "restricted_sources": ["weibo", "wallstreetcn", "36kr", "tencent"],
  "max_age_hours": 48,
  "enable_hallucination_check": true
}
```

---

## 与 agent-safety-guard 的关系

本 wrapper 是 `agent-safety-guard` 在**新闻聚合场景**的具体实现：

| agent-safety-guard | news-aggregator-safe |
|-------------------|---------------------|
| 高危命令确认 | 信源白名单 + 二次确认 |
| 删除阈值保护 | 输出校验 + 熔断 |
| 目录隔离 | 写入路径校验 |
| 同步熔断 | 陈旧数据熔断 |

**建议**：两个 skill 一起使用，形成完整的安全体系。

---

## 已知限制

1. **无法防止信源本身造假**（如假新闻）—— 这是信源选择问题
2. **无法防止原技能被篡改后绕过校验** —— 需定期审计原技能代码
3. **时间戳校验依赖原技能输出原始时间戳** —— 如原技能只输出"1h ago"无法校验
4. **无法防止 AI 在"解读"部分注入主观内容** —— 只能检测并过滤

---

## 审计日志

每次执行后，自动记录到 `memory/news-aggregator-safe-log.md`：

```markdown
## 2026-03-09 23:07

- 请求：科技早报
- 信源：hackernews, github, huggingface
- 返回条目：15
- 校验结果：✅ 通过
- 异常条目：0
- 执行时间：2m34s
```

---

## 核心原则

> **宁可少报，不可错报。**
> 
> 0 条新闻 > 假新闻
> 
> "信源失效" > AI 幻觉补全
> 
> 用户明确知道"没拿到数据"，比"拿到错误数据"更安全。
