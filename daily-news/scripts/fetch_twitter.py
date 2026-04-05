#!/usr/bin/env python3
"""
Daily News v2 — Twitter/X 信源抓取脚本

通过 opencli 抓取 X 上的 AI 相关热门推文/话题。
opencli 会复用 Chrome 浏览器的已登录 session，无需额外配置。

用法：
  python3 fetch_twitter.py search --query "AI agent 2025" --limit 20
  python3 fetch_twitter.py trending --limit 10
  python3 fetch_twitter.py timeline --limit 20
  python3 fetch_twitter.py bookmarks --limit 20

输出：
  JSON 数组，每条格式：
  {"title": "...", "url": "...", "published_at": "...", "author": "...", "likes": 0, "views": "0"}

依赖：
  - opencli 已安装（/usr/local/bin/opencli 或 PATH 中）
  - Chrome 已安装 opencli 扩展并连接
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


OPENCLI_PATH = "/usr/local/bin/opencli"

# 刷 X AI 热点的搜索词组
# 每个 query 独立搜索，结果合并去重后按 likes 降序
DEFAULT_AI_QUERIES = [
    # 最新模型发布
    "Claude OR GPT OR Gemini OR Llama OR Qwen new model release",
    # AI Agent / 自主智能体
    "AI agent autonomous agentic workflow 2025",
    # AI 产品发布
    "AI product launch just shipped announcement",
    # 最佳实践 / 工程经验
    "LLM best practices prompt engineering lessons production",
    # 开源模型
    "open source LLM model released weights huggingface",
    # MCP / 工具调用
    "MCP model context protocol tool use",
    # AI 编程
    "AI coding Claude Code Cursor tips workflow",
    # 研究 / 技术突破
    "AI research paper arxiv breakthrough 2025",
    # 融资 / 行业动态
    "AI startup funding raised billion 2025",
    # 中文 AI 圈
    "AI 大模型 发布 实践 最新",
]


def run_opencli(args: list) -> list:
    """执行 opencli 命令并返回解析后的 JSON 结果"""
    # 确保 /usr/local/bin 在 PATH 中（node 在此路径，部分环境默认不包含）
    env = os.environ.copy()
    if "/usr/local/bin" not in env.get("PATH", ""):
        env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")

    cmd = [OPENCLI_PATH] + args + ["--format", "json"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        if result.returncode != 0:
            print(f"[fetch_twitter] opencli error: {result.stderr}", file=sys.stderr)
            return []
        output = result.stdout.strip()
        if not output:
            return []
        return json.loads(output)
    except subprocess.TimeoutExpired:
        print("[fetch_twitter] opencli timed out", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[fetch_twitter] JSON parse error: {e}", file=sys.stderr)
        print(f"[fetch_twitter] raw output: {result.stdout[:200]}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print(f"[fetch_twitter] opencli not found at {OPENCLI_PATH}", file=sys.stderr)
        print("[fetch_twitter] install: npm install -g @jackwener/opencli", file=sys.stderr)
        return []


def normalize_tweet(raw: dict) -> dict:
    """将 opencli 返回的推文格式规范化为 daily-news item 格式"""
    tweet_id = raw.get("id", "")
    author = raw.get("author", "unknown")
    text = raw.get("text", "").strip()
    created_at = raw.get("created_at", "")
    url = raw.get("url") or (f"https://x.com/i/status/{tweet_id}" if tweet_id else "")

    # 尝试解析发布时间
    published_at = None
    if created_at:
        try:
            # Twitter 格式: "Thu Jan 01 00:00:00 +0000 2026"
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
            published_at = dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            published_at = created_at  # 保留原始格式

    # 用推文正文作为标题（截断）
    title = text[:120] + "…" if len(text) > 120 else text
    if author and author != "unknown":
        title = f"@{author}: {title}"

    return {
        "title": title,
        "url": url,
        "published_at": published_at,
        "author": author,
        "likes": raw.get("likes", 0),
        "views": str(raw.get("views", "0")),
        "text": text,
    }


def cmd_search(query: str, limit: int, filter_: str = "top") -> list:
    """搜索推文"""
    raw_items = run_opencli(["twitter", "search", query, "--filter", filter_, "--limit", str(limit)])
    return [normalize_tweet(r) for r in raw_items if r.get("url") or r.get("id")]


def cmd_trending(limit: int) -> list:
    """获取热门话题（trending）"""
    raw_items = run_opencli(["twitter", "trending", "--limit", str(limit)])
    # trending 返回话题，格式可能不同
    results = []
    for r in raw_items:
        topic = r.get("topic") or r.get("name") or r.get("title") or str(r)
        url = r.get("url") or f"https://x.com/search?q={topic.replace(' ', '%20')}"
        results.append({
            "title": f"[X热门话题] {topic}",
            "url": url,
            "published_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "tweet_count": r.get("tweet_count"),
        })
    return results[:limit]


def cmd_ai_sweep(limit_per_query: int = 15) -> list:
    """扫描多个 AI 搜索词，合并去重"""
    seen_urls = set()
    all_items = []
    for query in DEFAULT_AI_QUERIES:
        items = cmd_search(query, limit_per_query)
        for item in items:
            if item["url"] and item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                all_items.append(item)
    # 按 likes 降序
    all_items.sort(key=lambda x: int(x.get("likes", 0) or 0), reverse=True)
    return all_items


def main():
    parser = argparse.ArgumentParser(
        description="Daily News v2 — Twitter/X 抓取工具"
    )
    subparsers = parser.add_subparsers(dest="cmd")

    # search
    sp = subparsers.add_parser("search", help="搜索推文")
    sp.add_argument("--query", "-q", required=True, help="搜索关键词")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--filter", dest="filter_", default="top", choices=["top", "live"])

    # trending
    tp = subparsers.add_parser("trending", help="获取热门话题")
    tp.add_argument("--limit", type=int, default=10)

    # ai-sweep：刷 AI 相关热帖（默认模式）
    ap = subparsers.add_parser("ai-sweep", help="扫描 AI 热帖（多关键词合并）")
    ap.add_argument("--limit-per-query", type=int, default=15)

    args = parser.parse_args()

    if args.cmd == "search":
        results = cmd_search(args.query, args.limit, args.filter_)
    elif args.cmd == "trending":
        results = cmd_trending(args.limit)
    elif args.cmd == "ai-sweep":
        results = cmd_ai_sweep(args.limit_per_query)
    else:
        parser.print_help()
        return

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
