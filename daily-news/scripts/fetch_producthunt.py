#!/usr/bin/env python3
"""
fetch_producthunt.py — 通过 opencli operate eval 抓取 Product Hunt 今日实时排行
按票数降序，即首页展示顺序
"""
import json, subprocess, sys, time

OPENCLI = "/usr/local/bin/node /usr/local/bin/opencli"

JS = r"""
var r=[];
var els=document.querySelectorAll('[data-test^="post-item-"]');
for(var i=0;i<Math.min(30,els.length);i++){
  var el=els[i];
  var lines=el.innerText.trim().split('\n').filter(function(t){return t.trim();});
  var nameRaw=lines[0]||'';
  var name=nameRaw.replace(/^\d+\.\s*/,'').trim();
  var tagline=lines[1]||'';
  var linkEl=el.querySelector('a[href*="/products/"]')||el.querySelector('a');
  var url=linkEl?linkEl.href:'';
  var votes='';
  for(var j=lines.length-1;j>=0;j--){
    if(/^\d+$/.test(lines[j].trim())){votes=lines[j].trim();break;}
  }
  r.push({rank:i+1,name:name,tagline:tagline,url:url,votes:parseInt(votes)||0});
}
JSON.stringify(r);
"""

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip()

def fetch():
    # 打开 PH 首页
    run(f"{OPENCLI} operate open 'https://www.producthunt.com/'")
    time.sleep(10)  # 等页面渲染

    # 抓取
    js_oneline = JS.replace('\n', ' ').replace('"', '\\"').strip()
    stdout, stderr = run(f'{OPENCLI} operate eval "{js_oneline}"')

    # 解析（过滤 opencli 的 update 提示）
    for line in stdout.split('\n'):
        line = line.strip()
        if line.startswith('['):
            try:
                data = json.loads(line)
                if data:
                    return data
            except:
                pass

    print(f"[fetch_ph] 解析失败: {stdout[:200]}", file=sys.stderr)
    return []

if __name__ == "__main__":
    items = fetch()
    print(f"[fetch_ph] 抓到 {len(items)} 个", file=sys.stderr)
    # 输出标准格式，title 包含排名+名称+tagline 供入库用
    out = []
    for p in items:
        out.append({
            "title": f"{p['rank']}. {p['name']} — {p['tagline']}",
            "url": p['url'],
            "published_at": "",  # 由调用方填入当天日期
            "_rank": p['rank'],
            "_votes": p['votes'],
            "_name": p['name'],
            "_tagline": p['tagline']
        })
    print(json.dumps(out, ensure_ascii=False))
