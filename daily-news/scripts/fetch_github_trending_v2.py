#!/usr/bin/env python3
"""
fetch_github_trending_v2.py — 用 GitHub Search API 获取热门项目（opencli 1.8+ 替代方案）
"""
import json, urllib.request, datetime, sys

def fetch():
    since = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    url = f"https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page=20"
    req = urllib.request.Request(url, headers={"User-Agent": "daily-news-bot"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
    except Exception as e:
        print(f"[fetch_github] Search API 失败: {e}", file=sys.stderr)
        return []

    items = []
    for i, r in enumerate(data.get("items", [])[:20]):
        items.append({
            "title": r["full_name"],
            "url": r["html_url"],
            "description": r.get("description") or "",
            "language": r.get("language") or "",
            "total_stars": r.get("stargazers_count", 0),
            "stars_today": 0  # Search API 不提供今日新增
        })

    print(f"[fetch_github] 抓到 {len(items)} 个", file=sys.stderr)
    return items

if __name__ == "__main__":
    items = fetch()
    print(json.dumps(items, ensure_ascii=False))
