#!/usr/bin/env python3
"""
fetch_openrouter_v2.py — opencli 1.8+ browser extract 抓取 OpenRouter LLM Leaderboard
"""
import json, re, subprocess, sys, time

def run_cmd(args, timeout=20):
    env_path = "/Users/wow/.local/share/fnm/node-versions/v20.20.0/installation/bin"
    env = {"PATH": f"{env_path}:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"}
    r = subprocess.run(["opencli", "browser", "default"] + args, capture_output=True, text=True, timeout=timeout, env=env)
    return r.stdout.strip(), r.stderr.strip()

def parse_extract(raw):
    try:
        d = json.loads(raw)
        if isinstance(d, dict) and d.get("content"):
            return d["content"]
    except:
        pass
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
        stdout, stderr = run_cmd(["open", "https://openrouter.ai/rankings"], timeout=20)
    except Exception as e:
        print(f"[fetch_or] open 失败: {e}", file=sys.stderr)
        return []

    time.sleep(12)

    try:
        stdout, stderr = run_cmd(["extract"], timeout=20)
    except Exception as e:
        print(f"[fetch_or] extract 失败: {e}", file=sys.stderr)
        return []

    content = parse_extract(stdout)
    if not content:
        print(f"[fetch_or] 无 content", file=sys.stderr)
        return []

    items = []
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    i = 0
    while i < len(lines):
        m = re.match(r'^(\d+)\.?$', lines[i])
        if not m:
            i += 1
            continue
        rank = int(m.group(1))
        i += 1
        if i >= len(lines):
            break
        if lines[i].startswith('!'):
            i += 1
            if i >= len(lines):
                break
        name_match = re.match(r'^\[([^\]]+)\]\(/[^)]+\)', lines[i])
        if not name_match:
            i += 1
            continue
        name = name_match.group(1)
        i += 1
        if i >= len(lines):
            break
        provider = ""
        pm = re.match(r'^by \[([^\]]+)\]', lines[i])
        if pm:
            provider = pm.group(1)
            i += 1
        if i >= len(lines):
            break
        tokens = ""
        tm = re.match(r'^([\d.]+[TBM]?\s+tokens)', lines[i])
        if tm:
            tokens = tm.group(1)
            i += 1
        else:
            break  # 没有 tokens 说明进入 Top Apps 区域，停止
        if i >= len(lines):
            break
        change = ""
        cm = re.match(r'^([\-]?\d+%)', lines[i])
        if cm:
            change = cm.group(1)
            i += 1

        items.append({
            "rank": rank,
            "name": name,
            "provider": provider,
            "tokens": tokens,
            "change": change
        })

    print(f"[fetch_or] 抓到 {len(items)} 个", file=sys.stderr)
    return items

if __name__ == "__main__":
    items = fetch()
    print(json.dumps(items, ensure_ascii=False))
