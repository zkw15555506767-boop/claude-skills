#!/usr/bin/env python3
"""
Daily News v2 — GitHub Trending 抓取脚本

通过 opencli operate 控制浏览器获取 GitHub Trending 全量数据。
比 Jina Reader 更稳定，能拿到完整描述和准确数据。

用法：
  python3 fetch_github_trending.py
  python3 fetch_github_trending.py --since weekly
"""

import json
import os
import subprocess
import sys
from datetime import datetime

OPENCLI_PATH = "/usr/local/bin/opencli"

JS_EXTRACT = """
(function(){
  const rows = document.querySelectorAll('article.Box-row');
  const result = [];
  rows.forEach((el, i) => {
    const nameEl = el.querySelector('h2 a');
    if (!nameEl) return;
    const descEl = el.querySelector('p.col-9, p[class*="color-fg-muted my-1"]');
    const starsEl = el.querySelector('a[href*="/stargazers"]');
    const todayEl = el.querySelector('span.d-inline-block.float-sm-right');
    const langEl = el.querySelector('[itemprop="programmingLanguage"]');
    result.push({
      rank: i + 1,
      name: nameEl.getAttribute('href').slice(1),
      url: 'https://github.com' + nameEl.getAttribute('href'),
      description: descEl ? descEl.textContent.trim() : '',
      total_stars: starsEl ? parseInt(starsEl.textContent.replace(/[^0-9]/g,'')) || 0 : 0,
      stars_today: todayEl ? parseInt(todayEl.textContent.replace(/[^0-9]/g,'')) || 0 : 0,
      language: langEl ? langEl.textContent.trim() : ''
    });
  });
  return JSON.stringify(result);
})()
"""


def run_opencli(args: list) -> str:
    env = os.environ.copy()
    if "/usr/local/bin" not in env.get("PATH", ""):
        env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")
    result = subprocess.run(
        [OPENCLI_PATH] + args,
        capture_output=True, text=True, timeout=30, env=env
    )
    return result.stdout.strip()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default="daily", choices=["daily", "weekly", "monthly"])
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://github.com/trending?since={args.since}"

    # 打开页面
    run_opencli(["operate", "open", url])

    import time
    time.sleep(3)

    # 提取数据
    raw = run_opencli(["operate", "eval", JS_EXTRACT])

    if not raw:
        print("[]")
        return

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[fetch_github] parse error: {raw[:200]}", file=sys.stderr)
        print("[]")
        return

    # 补充 published_at
    for it in items:
        it["title"] = it.pop("name")
        it["published_at"] = f"{today}T00:00:00"

    items.sort(key=lambda x: x.get("stars_today", 0), reverse=True)
    print(f"[fetch_github] 抓到 {len(items)} 个项目", file=sys.stderr)
    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
