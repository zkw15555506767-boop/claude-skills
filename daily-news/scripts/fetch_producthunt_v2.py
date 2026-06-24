#!/usr/bin/env python3
"""
fetch_producthunt_v2.py — opencli 1.8+ browser extract 抓取 Product Hunt
"""
import json, re, subprocess, sys, time

def run_cmd(args, timeout=20):
    env_path = "/Users/wow/.local/share/fnm/node-versions/v20.20.0/installation/bin"
    env = {"PATH": f"{env_path}:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"}
    r = subprocess.run(["opencli", "browser", "default"] + args, capture_output=True, text=True, timeout=timeout, env=env)
    return r.stdout.strip(), r.stderr.strip()

def parse_extract(raw):
    """从 stdout 中提取 content JSON（支持多行 JSON）"""
    # 尝试整个 stdout 当 JSON
    try:
        d = json.loads(raw)
        if isinstance(d, dict) and d.get("content"):
            return d["content"]
    except:
        pass
    # fallback: 逐行找
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if isinstance(d, dict) and d.get("content"):
                return d["content"]
        except:
            continue
    return ""

def fetch():
    try:
        stdout, stderr = run_cmd(["open", "https://www.producthunt.com/"], timeout=15)
    except Exception as e:
        print(f"[fetch_ph] open 失败: {e}", file=sys.stderr)
        return []

    time.sleep(10)

    try:
        stdout, stderr = run_cmd(["extract"], timeout=15)
    except Exception as e:
        print(f"[fetch_ph] extract 失败: {e}", file=sys.stderr)
        return []

    content = parse_extract(stdout)
    if not content:
        print(f"[fetch_ph] 无 content", file=sys.stderr)
        return []

    items = []
    for m in re.finditer(r'\[([^\n\]]+)\]\(/products/([^)]+)\)([^\n]+)', content):
        name, slug, tagline = m.groups()
        tagline = tagline.strip()
        if not tagline or len(tagline) < 5 or tagline.startswith("Promoted") or tagline.startswith("["):
            continue
        # 去重
        if any(i["name"] == name.strip() for i in items):
            continue
        items.append({
            "rank": len(items) + 1,
            "name": name.strip(),
            "url": f"https://www.producthunt.com/products/{slug}",
            "tagline": tagline
        })

    return items

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
            "_name": p['name'],
            "_tagline": p['tagline']
        })
    print(json.dumps(out, ensure_ascii=False))
