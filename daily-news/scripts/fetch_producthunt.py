#!/usr/bin/env python3
"""
fetch_producthunt.py — 通过 opencli operate eval 抓取 Product Hunt 今日实时排行
按票数降序，即首页展示顺序
"""
import json, subprocess, sys, time, re

OPENCLI = ["/usr/local/bin/node", "/usr/local/bin/opencli"]

# 新版 DOM 结构（2026-04）：vote-button 在 homepage-section-today 内
JS_NEW = r"""
(function(){
var section = document.querySelector('[data-test="homepage-section-today"]');
if (!section) return JSON.stringify([]);
var voteButtons = section.querySelectorAll('[data-test="vote-button"]');
var results = [];
Array.from(voteButtons).forEach(function(btn, i) {
  var container = btn.closest('li') || btn.closest('section') || btn.closest('article') || btn.parentElement.parentElement;
  if (!container) return;
  var lines = container.innerText.trim().split('\n').map(function(l){return l.trim();}).filter(function(l){return l.length>0;});
  var name = lines[0] || '';
  var tagline = lines[1] || '';
  var votesRaw = btn.innerText.trim().replace(/[^0-9]/g,'');
  var votes = votesRaw ? parseInt(votesRaw) : 0;
  var linkEl = container.querySelector('a[href*="/products/"]') || container.querySelector('a');
  var url = linkEl ? linkEl.href : '';
  results.push({rank: i+1, name: name, tagline: tagline, url: url, votes: votes});
});
return JSON.stringify(results);
})();
"""

# 旧版 DOM 结构（fallback）
JS_OLD = r"""
(function(){
var results = [];
document.querySelectorAll('[data-test^="post-item-"]').forEach(function(el, i) {
  var lines = el.innerText.trim().split('\n').map(function(l){return l.trim();}).filter(function(l){return l.length>0;});
  var nameRaw = lines[0] || '';
  var name = nameRaw.replace(/^\d+\.\s*/,'').trim();
  var tagline = lines[1] || '';
  var linkEl = el.querySelector('a[href*="/products/"]') || el.querySelector('a');
  var url = linkEl ? linkEl.href : '';
  var votes = '';
  for (var j=lines.length-1; j>=0; j--) {
    if (/^\d+$/.test(lines[j].trim())) { votes = lines[j].trim(); break; }
  }
  results.push({rank: i+1, name: name, tagline: tagline, url: url, votes: parseInt(votes)||0});
});
return JSON.stringify(results);
})();
"""

def run_opencli(args, timeout=30):
    result = subprocess.run(
        OPENCLI + args,
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip()

def parse_result(raw):
    for line in raw.split('\n'):
        line = line.strip()
        if line.startswith('['):
            try:
                data = json.loads(line)
                if isinstance(data, list):
                    return data
            except:
                pass
    return []

def fetch():
    # 打开 PH 首页
    try:
        run_opencli(["operate", "open", "https://www.producthunt.com/"], timeout=20)
    except Exception as e:
        print(f"[fetch_ph] open 失败: {e}", file=sys.stderr)
        return []

    time.sleep(12)  # 等页面渲染

    # 先尝试新版结构
    try:
        js = JS_NEW.replace('\n', ' ').strip()
        stdout, stderr = run_opencli(["operate", "eval", js], timeout=15)
        data = parse_result(stdout)
        if data:
            print(f"[fetch_ph] 新版结构，抓到 {len(data)} 个", file=sys.stderr)
            return data
    except Exception as e:
        print(f"[fetch_ph] 新版结构失败: {e}", file=sys.stderr)

    # fallback 旧版结构
    try:
        js = JS_OLD.replace('\n', ' ').strip()
        stdout, stderr = run_opencli(["operate", "eval", js], timeout=15)
        data = parse_result(stdout)
        if data:
            print(f"[fetch_ph] 旧版结构，抓到 {len(data)} 个", file=sys.stderr)
            return data
    except Exception as e:
        print(f"[fetch_ph] 旧版结构失败: {e}", file=sys.stderr)

    print(f"[fetch_ph] 解析失败: {stdout[:100]}", file=sys.stderr)
    return []

if __name__ == "__main__":
    items = fetch()
    print(f"[fetch_ph] 抓到 {len(items)} 个", file=sys.stderr)
    out = []
    for p in items:
        out.append({
            "title": f"{p['rank']}. {p['name']} — {p['tagline']}",
            "url": p['url'],
            "published_at": "",
            "_rank": p['rank'],
            "_votes": p['votes'],
            "_name": p['name'],
            "_tagline": p['tagline']
        })
    print(json.dumps(out, ensure_ascii=False))
