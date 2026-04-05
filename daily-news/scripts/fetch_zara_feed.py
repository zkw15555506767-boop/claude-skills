#!/usr/bin/env python3
"""
Daily News v2 — Zara Builder Feed 抓取脚本
从 Zara 的 follow-builders GitHub 实时拉 feed-x.json
包含 25+ 个优质 builder 的精选推文（有完整 likes/retweets/text）
"""

import json, sys, urllib.request
from datetime import datetime

FEED_X_URL = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json"

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        req = urllib.request.Request(FEED_X_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[fetch_zara_feed] fetch error: {e}", file=sys.stderr)
        print("[]"); return

    generated_at = data.get("generatedAt", "")
    accounts = data.get("x", [])
    print(f"[fetch_zara_feed] feed 生成时间: {generated_at}, {len(accounts)} 个账号", file=sys.stderr)

    result = []
    for account in accounts:
        handle  = account.get("handle", "")
        name    = account.get("name", "")
        bio     = account.get("bio", "")
        tweets  = account.get("tweets", [])

        for tw in tweets:
            tw_id   = tw.get("id", "")
            text    = tw.get("text", "").strip()
            likes   = tw.get("likes", 0)
            retweets= tw.get("retweets", 0)
            replies = tw.get("replies", 0)
            url     = tw.get("url", f"https://x.com/{handle}/status/{tw_id}")
            created = tw.get("createdAt", f"{today}T00:00:00")
            # ISO 格式转为 DB 格式
            pub_at  = created[:19].replace("T", "T") if created else f"{today}T00:00:00"

            if not text or not tw_id:
                continue

            result.append({
                "title":        f"@{handle}: {text[:120]}",
                "url":          url,
                "published_at": pub_at,
                "author":       handle,
                "author_name":  name,
                "likes":        likes,
                "retweets":     retweets,
                "replies":      replies,
                "full_text":    text,
                "source":       "zara-feed",  # 区分来源
            })

    # 按 likes 排序
    result.sort(key=lambda x: x.get("likes", 0), reverse=True)
    print(f"[fetch_zara_feed] 共 {len(result)} 条推文", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
