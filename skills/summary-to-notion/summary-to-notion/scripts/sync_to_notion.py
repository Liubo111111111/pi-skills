#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


NOTION_VERSION = "2025-09-03"


def normalize_id(raw: str) -> str:
    value = raw.strip()
    return value.replace("-", "")


def notion_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def request_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in notion_headers(token).items():
        req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def split_lines(text: str, chunk_size: int = 1800) -> list[str]:
    text = text.strip()
    if not text:
        return []
    lines = []
    remaining = text
    while remaining:
        lines.append(remaining[:chunk_size])
        remaining = remaining[chunk_size:]
    return lines


def markdown_to_blocks(markdown_text: str, source_url: str) -> list[dict]:
    children = []
    if source_url:
        children.append(
            {
                "object": "block",
                "type": "bookmark",
                "bookmark": {"url": source_url},
            }
        )
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            children.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[4:]}}]
                    },
                }
            )
            continue
        if stripped.startswith("## "):
            children.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[3:]}}]
                    },
                }
            )
            continue
        if stripped.startswith("# "):
            children.append(
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                    },
                }
            )
            continue
        if stripped.startswith(("- ", "* ")):
            children.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                    },
                }
            )
            continue
        for chunk in split_lines(stripped):
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    },
                }
            )
    return children[:100]


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def read_optional_file(path: str | None) -> str:
    if not path:
        return ""
    return read_file(path).strip()


def parse_keywords(raw: str) -> list[str]:
    if not raw:
        return []
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def fetch_database_meta(token: str, database_id: str) -> dict:
    return request_json("GET", f"https://api.notion.com/v1/databases/{normalize_id(database_id)}", token)


def fetch_data_source_meta(token: str, data_source_id: str) -> dict:
    return request_json("GET", f"https://api.notion.com/v1/data_sources/{normalize_id(data_source_id)}", token)


def get_data_source_id(token: str, database_id: str) -> str | None:
    meta = fetch_database_meta(token, database_id)
    sources = meta.get("data_sources") or []
    if not sources:
        return None
    return sources[0].get("id")


def get_data_source_properties(token: str, database_id: str) -> dict[str, dict]:
    data_source_id = get_data_source_id(token, database_id)
    if not data_source_id:
        return {}
    meta = fetch_data_source_meta(token, data_source_id)
    return meta.get("properties", {})


def normalize_prop_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def resolve_property(properties: dict[str, dict], explicit: str | None, candidates: list[str], prop_type: str | None = None) -> str | None:
    if explicit:
        explicit_norm = normalize_prop_name(explicit)
        for name, meta in properties.items():
            if normalize_prop_name(name) != explicit_norm:
                continue
            if not prop_type or meta.get("type") == prop_type:
                return name
        return explicit

    normalized = {normalize_prop_name(name): name for name in properties}
    for candidate in candidates:
        name = normalized.get(normalize_prop_name(candidate))
        if not name:
            continue
        if prop_type and properties[name].get("type") != prop_type:
            continue
        return name

    if prop_type:
        for name, meta in properties.items():
            if meta.get("type") == prop_type:
                return name
    return None


def rich_text_value(text: str) -> dict:
    chunks = split_lines(text)
    return {"rich_text": [{"type": "text", "text": {"content": chunk}} for chunk in chunks[:100]]}


def title_value(text: str) -> dict:
    chunks = split_lines(text)
    return {"title": [{"type": "text", "text": {"content": chunk}} for chunk in chunks[:1]]}


def date_value(date_text: str) -> dict:
    return {"date": {"start": date_text}}


def url_value(url: str) -> dict:
    return {"url": url}


def select_value(name: str) -> dict:
    return {"select": {"name": name}}


def multi_select_value(values: list[str]) -> dict:
    return {"multi_select": [{"name": v} for v in values]}


def number_value(raw: str) -> dict:
    return {"number": float(raw) if "." in raw else int(raw)}


def coerce_property_value(prop_meta: dict, value: Any) -> dict | None:
    if value in (None, "", []):
        return None
    prop_type = prop_meta.get("type")
    if prop_type == "title":
        return title_value(str(value))
    if prop_type == "rich_text":
        return rich_text_value(str(value))
    if prop_type == "url":
        return url_value(str(value))
    if prop_type == "date":
        return date_value(str(value))
    if prop_type == "select":
        return select_value(str(value))
    if prop_type == "multi_select":
        items = value if isinstance(value, list) else parse_keywords(str(value))
        return multi_select_value(items)
    if prop_type == "number":
        return number_value(str(value))
    return None


def build_database_properties(args: argparse.Namespace, properties: dict[str, dict], summary_text: str, keypoints_text: str) -> dict:
    field_defs = [
        (args.title_property, ["Title", "Name"], "title", args.title),
        (args.url_property, ["URL", "Source URL", "Link"], None, args.source_url),
        (args.summary_property, ["Summary", "Abstract"], "rich_text", summary_text),
        (args.keypoints_property, ["KeyPoints", "Key Points", "Highlights"], None, keypoints_text),
        (args.keywords_property, ["Keywords", "Tags", "Topics"], "multi_select", parse_keywords(args.keywords)),
        (args.report_date_property, ["ReportDate", "Report Date", "ArchiveDate", "Archived At"], None, args.report_date),
        (args.published_date_property, ["PublishedDate", "Published Date", "Date"], None, args.published_date),
        (args.author_property, ["Author", "Authors"], None, args.author),
        (args.source_property, ["Source", "Channel"], None, args.source),
        (args.content_type_property, ["ContentType", "Content Type", "Type"], None, args.content_type),
        (args.score_property, ["Score", "Importance", "Priority"], None, args.score),
        (args.why_it_matters_property, ["WhyItMatters", "Why It Matters", "Takeaway"], None, args.why_it_matters),
    ]

    result = {}
    used_props: set[str] = set()
    for explicit, candidates, fallback_type, raw_value in field_defs:
        prop_name = resolve_property(properties, explicit, candidates, fallback_type)
        if not prop_name or prop_name in used_props:
            continue
        prop_meta = properties.get(prop_name)
        if not prop_meta:
            continue
        coerced = coerce_property_value(prop_meta, raw_value)
        if coerced is not None:
            result[prop_name] = coerced
            used_props.add(prop_name)
    return result


def create_page_under_parent(token: str, parent_page_id: str, title: str, children: list[dict]) -> dict:
    payload = {
        "parent": {"page_id": normalize_id(parent_page_id)},
        "properties": {
            "title": title_value(title)
        },
        "children": children,
    }
    return request_json("POST", "https://api.notion.com/v1/pages", token, payload)


def create_page_in_database(
    token: str,
    database_id: str,
    properties: dict,
    children: list[dict],
) -> dict:
    payload = {
        "parent": {"database_id": normalize_id(database_id)},
        "properties": properties,
        "children": children,
    }
    return request_json("POST", "https://api.notion.com/v1/pages", token, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync summary markdown to a Notion page or database.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--keypoints-file", default="")
    parser.add_argument("--keywords", default="")
    parser.add_argument("--report-date", default="")
    parser.add_argument("--published-date", default="")
    parser.add_argument("--author", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--content-type", default="")
    parser.add_argument("--score", default="")
    parser.add_argument("--why-it-matters", default="")
    parser.add_argument("--title-property", default="")
    parser.add_argument("--url-property", default="")
    parser.add_argument("--summary-property", default="")
    parser.add_argument("--keypoints-property", default="")
    parser.add_argument("--keywords-property", default="")
    parser.add_argument("--report-date-property", default="")
    parser.add_argument("--published-date-property", default="")
    parser.add_argument("--author-property", default="")
    parser.add_argument("--source-property", default="")
    parser.add_argument("--content-type-property", default="")
    parser.add_argument("--score-property", default="")
    parser.add_argument("--why-it-matters-property", default="")
    parser.add_argument("--print-schema", action="store_true")
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()
    database_id = os.getenv("NOTION_DATABASE_ID", "").strip()

    if not token:
        print("Missing NOTION_TOKEN or NOTION_API_KEY", file=sys.stderr)
        return 2
    if not parent_page_id and not database_id:
        print("Missing NOTION_PARENT_PAGE_ID or NOTION_DATABASE_ID", file=sys.stderr)
        return 2

    summary_text = read_file(args.summary_file).strip()
    keypoints_text = read_optional_file(args.keypoints_file)
    children = markdown_to_blocks(summary_text, args.source_url)

    try:
        properties_meta = get_data_source_properties(token, database_id) if database_id else {}

        if args.print_schema and properties_meta:
            simplified = {name: meta.get("type") for name, meta in properties_meta.items()}
            print(json.dumps(simplified, ensure_ascii=False, indent=2))
            return 0

        if database_id:
            try:
                properties = build_database_properties(args, properties_meta, summary_text, keypoints_text)
                result = create_page_in_database(token, database_id, properties, children)
                print(json.dumps({"mode": "database", "page_id": result.get("id"), "url": result.get("url"), "properties_written": list(properties.keys())}, ensure_ascii=False))
                return 0
            except urllib.error.HTTPError:
                if not parent_page_id:
                    raise
        result = create_page_under_parent(token, parent_page_id, args.title, children)
        print(json.dumps({"mode": "page", "page_id": result.get("id"), "url": result.get("url")}, ensure_ascii=False))
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
