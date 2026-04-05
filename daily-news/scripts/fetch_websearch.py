#!/usr/bin/env python3
"""
Daily News v2 — WebSearch 信源抓取脚本

通过 WebSearch 工具（Tavily）搜索最新 AI 资讯，
作为 RSS/WebFetch 信源的补充，捕捉更广泛的 AI 新闻。

用法：
  python3 fetch_websearch.py --query "AI agent 最新进展" --limit 10
  python3 fetch_websearch.py --query "GPT Claude Gemini 发布" --days 3
  python3 fetch_websearch.py --ai-sweep

输出：
  JSON 数组，格式：
  {"title": "...", "url": "...", "published_at": "...", "source_domain": "..."}

注意：
  此脚本供 AI agent（Claude Code / AirJelly）调用时作为参考。
  实际 WebSearch 调用由 agent 自己发起，本脚本提供查询策略和结果格式化逻辑。
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

# ============================================================
# AI 热点搜索策略配置
# 修改此处调整每日扫描的搜索词
# ============================================================

AI_SWEEP_QUERIES = [
    # 最新模型发布
    {"query": "Claude GPT Gemini Llama Qwen new model release 2025", "label": "最新模型"},
    # AI Agent
    {"query": "AI agent autonomous agentic workflow announcement 2025", "label": "AI Agent"},
    # AI 产品发布
    {"query": "AI product launch just shipped site:techcrunch.com OR site:venturebeat.com", "label": "AI 产品"},
    # 最佳实践 / 工程经验
    {"query": "LLM best practices prompt engineering production lessons learned", "label": "最佳实践"},
    # 开源模型
    {"query": "open source LLM model weights released huggingface github 2025", "label": "开源模型"},
    # MCP / 工具调用
    {"query": "model context protocol MCP tool use function calling 2025", "label": "MCP 工具"},
    # AI 编程
    {"query": "AI coding assistant Claude Code Cursor tips workflow 2025", "label": "AI 编程"},
    # 研究 / 技术突破
    {"query": "AI research breakthrough arxiv paper 2025", "label": "AI 研究"},
    # 融资 / 行业动态
    {"query": "AI startup funding raised Series A B C 2025", "label": "AI 融资"},
    # 中文 AI 资讯
    {"query": "AI 大模型 发布 实践 最新进展 site:36kr.com OR site:jiqizhixin.com", "label": "中文 AI"},
]


def format_item(raw: dict) -> dict:
    """将搜索结果格式化为 daily-news item 格式"""
    url = raw.get("url", "")
    title = raw.get("title", url)
    # 尝试解析发布时间
    published_at = raw.get("published_date") or raw.get("published_at")
    if not published_at:
        published_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    domain = ""
    if url:
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
        except Exception:
            pass

    return {
        "title": title,
        "url": url,
        "published_at": published_at,
        "source_domain": domain,
        "snippet": raw.get("content") or raw.get("snippet") or "",
    }


def print_search_plan():
    """打印 AI sweep 的搜索计划（供 agent 执行）"""
    plan = {
        "mode": "websearch_ai_sweep",
        "description": "按以下查询逐一执行 WebSearch，合并去重后入库",
        "queries": AI_SWEEP_QUERIES,
        "dedup_key": "url",
        "sort_by": "published_at desc",
        "instructions": [
            "1. 对 queries 中每条执行 WebSearch",
            "2. 用 format_item() 规范化每条结果",
            "3. 按 url 去重（seen_urls set）",
            "4. 过滤 published_at 不在目标日期范围内的条目",
            "5. 输出 JSON 数组，入库时用 add-items-incremental",
        ],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Daily News v2 — WebSearch 抓取工具")
    parser.add_argument("--query", help="自定义搜索词")
    parser.add_argument("--days", type=int, default=1, help="过滤最近 N 天的内容")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--ai-sweep", action="store_true", help="输出 AI 热点扫描计划")
    args = parser.parse_args()

    if args.ai_sweep or not args.query:
        print_search_plan()
        return

    # 如果有具体 query，输出格式化模板（agent 实际搜索后调用 format_item）
    template = {
        "query": args.query,
        "days_filter": args.days,
        "limit": args.limit,
        "since": (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d"),
        "format_function": "format_item(raw_result) → {title, url, published_at, source_domain, snippet}",
    }
    print(json.dumps(template, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
