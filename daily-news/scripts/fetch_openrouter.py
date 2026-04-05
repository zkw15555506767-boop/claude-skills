#!/usr/bin/env python3
"""
Daily News v2 — OpenRouter Rankings 抓取脚本
通过 opencli operate eval 抓取 LLM Leaderboard（使用量排名）
"""

import json, os, subprocess, sys, time
from datetime import datetime

OPENCLI = "/usr/local/bin/opencli"

def run_opencli(args):
    env = os.environ.copy()
    env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")
    r = subprocess.run([OPENCLI] + args, capture_output=True, text=True, timeout=30, env=env)
    return r.stdout.strip()

JS = """
(function(){
  const text = document.body.innerText;
  const lines = text.split('\\n').map(l=>l.trim()).filter(l=>l);

  // 找 LLM Leaderboard 区域
  const start = lines.findIndex(l => l.includes('LLM Leaderboard'));
  if (start === -1) return JSON.stringify({error: 'no leaderboard found'});

  const chunk = lines.slice(start + 2, start + 80); // 跳过标题和副标题
  const items = [];
  let i = 0;

  while (i < chunk.length) {
    // 格式: "1." -> 模型名 -> "by" -> 提供商 -> "Xt tokens" -> 涨跌%
    const rankLine = chunk[i];
    if (!/^\\d+\\.$/.test(rankLine)) { i++; continue; }

    const rank = parseInt(rankLine);
    const name = chunk[i+1] || '';
    const by   = chunk[i+2] || ''; // "by"
    const provider = chunk[i+3] || '';
    const tokens = chunk[i+4] || '';
    const change = chunk[i+5] || '';

    if (by === 'by' && name) {
      items.push({ rank, name, provider, tokens, change });
      i += 6;
    } else {
      i++;
    }
    if (items.length >= 15) break;
  }
  return JSON.stringify(items);
})()
"""

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    run_opencli(["operate", "open", "https://openrouter.ai/rankings"])
    time.sleep(5)

    raw = run_opencli(["operate", "eval", JS])
    if not raw:
        print("[]"); return

    try:
        items = json.loads(raw)
    except Exception as e:
        print(f"[fetch_openrouter] parse error: {e}", file=sys.stderr)
        print("[]"); return

    if isinstance(items, dict) and items.get("error"):
        print(f"[fetch_openrouter] {items['error']}", file=sys.stderr)
        print("[]"); return

    # 标准化为 DB item 格式
    result = []
    for it in items:
        name = it.get("name", "")
        provider = it.get("provider", "")
        rank = it.get("rank", 0)
        tokens = it.get("tokens", "")
        change = it.get("change", "")
        result.append({
            "title": f"#{rank} {name} ({provider}) — {tokens} {change}",
            "url": f"https://openrouter.ai/models?q={name.replace(' ', '+')}",
            "published_at": f"{today}T00:00:00",
            "rank": rank,
            "model_name": name,
            "provider": provider,
            "tokens": tokens,
            "change": change,
        })

    print(f"[fetch_openrouter] 抓到 {len(result)} 个模型", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
