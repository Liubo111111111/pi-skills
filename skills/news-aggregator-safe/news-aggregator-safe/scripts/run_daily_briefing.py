#!/usr/bin/env python3
"""
Daily Briefing Runner for news-aggregator-safe wrapper.
Runs multiple news sources and outputs a consolidated Markdown report.
"""

import subprocess
import sys
import os
import json
from collections import Counter
from datetime import datetime

# Configuration
SKILL_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_SKILL_CANDIDATES = [
    os.path.join(os.path.dirname(SKILL_PATH), "news-aggregator-skill"),
    os.path.join(os.path.dirname(SKILL_PATH), "news-aggregator"),
]
PARENT_SKILL_PATH = next(
    (path for path in PARENT_SKILL_CANDIDATES if os.path.exists(path)),
    PARENT_SKILL_CANDIDATES[0],
)
OUTPUT_DIR = os.path.join(os.path.dirname(SKILL_PATH), "output")
REPORTS_DIR = os.path.join(PARENT_SKILL_PATH, "reports", datetime.now().strftime("%Y-%m-%d"))

# Default sources (stable ones)
DEFAULT_SOURCES = ["hackernews", "github", "huggingface", "v2ex"]

SOURCE_LABELS = {
    "hackernews": "Hacker News",
    "github": "GitHub Trending",
    "huggingface": "HuggingFace Papers",
    "v2ex": "V2EX",
    "producthunt": "Product Hunt",
}

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def run_fetch(sources, limit=15):
    """Run the fetch_news.py script from parent skill."""
    fetch_script = os.path.join(PARENT_SKILL_PATH, "scripts", "fetch_news.py")
    
    if not os.path.exists(fetch_script):
        print(f"Error: fetch_news.py not found at {fetch_script}", file=sys.stderr)
        sys.exit(1)
    
    cmd = [
        "python3", fetch_script,
        "--source", ",".join(sources),
        "--limit", str(limit)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Fetch timed out after 5 minutes", 1
    except Exception as e:
        return "", str(e), 1

def parse_items(stdout):
    """Parse fetch output JSON."""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"抓取输出不是有效 JSON: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError("抓取输出不是 JSON 数组")

    return payload


def summarize_sources(items, requested_sources):
    label_counts = Counter(item.get("source", "") for item in items)
    summary = []

    for source in requested_sources:
        label = SOURCE_LABELS.get(source, source)
        summary.append((source, label, label_counts.get(label, 0)))

    return summary


def generate_report(items, sources, stderr=""):
    """Generate a Markdown report from parsed items."""
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    source_labels = [SOURCE_LABELS.get(source, source) for source in sources]
    source_summary = summarize_sources(items, sources)
    missing_sources = [label for _, label, count in source_summary if count == 0]
    status_bits = ["✅ 原始 JSON 有效"]
    if missing_sources:
        status_bits.append(f"⚠️ 缺失信源: {', '.join(missing_sources)}")
    else:
        status_bits.append("✅ 所有信源均有返回")
    if stderr.strip():
        status_bits.append("ℹ️ 抓取日志已附带")

    summary_lines = [
        f"- **{label}**: {count} 条"
        for _, label, count in source_summary
    ]
    anomaly_line = (
        ", ".join(f"{label} 0 条" for label in missing_sources)
        if missing_sources
        else "暂无明显异常"
    )
    raw_json = json.dumps(items, indent=2, ensure_ascii=False)
    if len(raw_json) > 50000:
        raw_json = raw_json[:50000]
        raw_json_note = "\n- 原始 JSON 已截断到 50000 字符，完整数据以抓取结果为准\n"
    else:
        raw_json_note = ""
    stderr_block = ""
    if stderr.strip():
        stderr_block = f"""
## 抓取日志

```text
{stderr.strip()[:8000]}
```

"""
    
    report = f"""# 📰 每日科技早报 | {today}

**生成时间**: {timestamp}  
**信源**: {', '.join(source_labels)}  
**校验状态**: {' | '.join(status_bits)}

---

## 今日概括

- **一句话总览**: 待根据已校验条目提炼，不超过 30 字
- **重点趋势**: 待归纳 2-3 个重复出现的主题
- **最值得关注**: 待选出 2-3 条最值得点开的内容，并说明原因
- **风险/异常**: {anomaly_line}

## 三点速览

1. 待填写
2. 待填写
3. 待填写

---

## 抓取统计

{chr(10).join(summary_lines)}

---

## 原始数据

```json
{raw_json}
```

---

## 输出要求

- 必须先完成“今日概括”和“三点速览”，再展开分信源详情
- 概括只能基于原始数据归纳，不得补充未出现的事实
- 如存在失败信源或异常条目，需在“风险/异常”中明确说明

---

## 说明

- 原始数据已捕获，需由 AI 先概括后展开地格式化呈现
- 时间戳已保留完整格式（YYYY-MM-DD HH:MM）
- 所有条目需经过 news-aggregator-safe 校验层
{raw_json_note}

"""
    if stderr_block:
        report += stderr_block
    return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Briefing Runner")
    parser.add_argument("--sources", type=str, default=",".join(DEFAULT_SOURCES),
                        help="Comma-separated source keys")
    parser.add_argument("--limit", type=int, default=15,
                        help="Max items per source")
    parser.add_argument("--output", type=str, 
                        default=os.path.join(OUTPUT_DIR, f"daily-briefing-{datetime.now().strftime('%Y-%m-%d')}.md"),
                        help="Output file path")
    
    args = parser.parse_args()
    sources = [s.strip() for s in args.sources.split(",")]
    
    print(f"🚀 开始抓取新闻...")
    print(f"   信源：{', '.join(sources)}")
    print(f"   限制：{args.limit} 条/信源")
    
    ensure_dirs()
    stdout, stderr, returncode = run_fetch(sources, args.limit)
    
    if returncode != 0:
        print(f"❌ 抓取失败：{stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        items = parse_items(stdout)
    except ValueError as exc:
        print(f"❌ 抓取失败：{exc}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ 抓取完成")
    
    report = generate_report(items, sources, stderr)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📄 报告已保存：{args.output}")
    
    # Also save to reports directory for the parent skill
    parent_report = os.path.join(REPORTS_DIR, "daily_briefing.md")
    with open(parent_report, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📄 副本已保存：{parent_report}")

if __name__ == "__main__":
    main()
