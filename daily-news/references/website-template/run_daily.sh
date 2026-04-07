#!/bin/bash
# ============================================================
# Daily News v2 · 每日自动运行脚本
# 路径: ~/daily-news/run_daily.sh
# 由 launchd 每天 11:00 / 14:00 / 22:00 触发
# ============================================================

# 不用 set -e，改为逐步容错，单个信源失败不中断整体
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh" 2>/dev/null || true

WS="$HOME/daily-news"
SKILL="$HOME/Library/Application Support/AirJelly/skills/daily-news"
DB="$WS/data/news.db"
LOG="$WS/logs/run_$(date +%Y-%m-%d).log"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$WS/logs" "$WS/output"

exec >> "$LOG" 2>&1
echo "=========================================="
echo "Daily News run: $TODAY $(date +%H:%M:%S)"
echo "=========================================="

# 工具函数：检查 JSON 是否非空数组
is_valid_json_array() {
  echo "$1" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if isinstance(d,list) and len(d)>0 else 1)" 2>/dev/null
}

# ── 阶段 1：抓取各信源 ──────────────────────────────────────

echo ""
echo "▶ [1/5] Product Hunt..."
PH_ITEMS=$(python3 "$SKILL/scripts/fetch_producthunt.py" 2>/tmp/dn_ph_err.log | python3 -c "
import json,sys
try:
    items=json.load(sys.stdin)
    for it in items: it['published_at']='${TODAY}T00:00:00'
    print(json.dumps(items,ensure_ascii=False))
except Exception as e:
    print('[]'); print(f'PH parse error: {e}', file=sys.stderr)
" 2>/tmp/dn_ph_parse_err.log) || true
cat /tmp/dn_ph_err.log >&2
cat /tmp/dn_ph_parse_err.log >&2

if is_valid_json_array "$PH_ITEMS"; then
  echo "$PH_ITEMS" | python3 -c "
import json, sys, sqlite3
from datetime import datetime
items = json.load(sys.stdin)
db = '$DB'
today = '$TODAY'
conn = sqlite3.connect(db)
now = datetime.now().isoformat()
# 先删除今天的旧数据，保证每次都是最新一次抓取的完整 30 条
deleted = conn.execute(\"DELETE FROM items WHERE source_id='product-hunt' AND DATE(published_at)=?\", (today,)).rowcount
seen_urls = set()
inserted = 0
for item in items:
    if item['url'] in seen_urls: continue  # 跳过重复 URL
    seen_urls.add(item['url'])
    conn.execute('INSERT INTO items (source_id, url, title, published_at, discovered_at) VALUES (?,?,?,?,?)',
                 ('product-hunt', item['url'], item['title'], today + 'T00:00:00', now))
    inserted += 1
conn.commit(); conn.close()
print(f'  PH: 清除旧数据 {deleted} 条，写入 {inserted} 条')
" || echo "  PH: 入库失败"
else
  echo "  PH: 抓取结果为空或解析失败，跳过"
fi

echo ""
echo "▶ [2/5] GitHub Trending..."
python3 "$SKILL/scripts/fetch_github_trending.py" > /tmp/dn_gh.json 2>/tmp/dn_gh_err.log || true
cat /tmp/dn_gh_err.log >&2
GH_ITEMS=$(cat /tmp/dn_gh.json 2>/dev/null || echo "[]")

if is_valid_json_array "$GH_ITEMS"; then
  python3 "$SKILL/scripts/db.py" add-items-incremental \
    --db "$DB" --source github-trending \
    --items "$GH_ITEMS" --since "$TODAY" 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  GH: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')" || echo "  GH: 入库失败"
else
  echo "  GH: 抓取结果为空，跳过"
fi

echo ""
echo "▶ [3/5] X/Twitter ai-sweep..."
TW_ITEMS=$(python3 "$SKILL/scripts/fetch_twitter.py" ai-sweep --limit-per-query 15 2>/tmp/dn_tw_err.log) || true
cat /tmp/dn_tw_err.log >&2

if is_valid_json_array "$TW_ITEMS"; then
  python3 "$SKILL/scripts/db.py" add-items-incremental \
    --db "$DB" --source twitter-ai-trending \
    --items "$TW_ITEMS" --since "$(date -v-1d +%Y-%m-%d)" 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  TW: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')" || echo "  TW: 入库失败"
else
  echo "  TW: 抓取结果为空，跳过"
fi

echo ""
echo "▶ [4/5] Hacker News..."
HN_RAW=$(/usr/local/bin/node /usr/local/bin/opencli hackernews top --limit 30 --format json 2>/tmp/dn_hn_err.log) || true
cat /tmp/dn_hn_err.log >&2
HN_ITEMS=$(echo "$HN_RAW" | python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
    items=[{'title':f'{p[\"rank\"]}. {p[\"title\"]}','url':p.get('url','https://news.ycombinator.com'),'published_at':'${TODAY}T00:00:00'} for p in data if p.get('url')]
    print(json.dumps(items,ensure_ascii=False))
except Exception as e:
    print('[]'); print(f'HN parse error: {e}', file=sys.stderr)
" 2>/tmp/dn_hn_parse_err.log) || true
cat /tmp/dn_hn_parse_err.log >&2

if is_valid_json_array "$HN_ITEMS"; then
  python3 "$SKILL/scripts/db.py" add-items-incremental \
    --db "$DB" --source hacker-news \
    --items "$HN_ITEMS" --since "$TODAY" 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  HN: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')" || echo "  HN: 入库失败"
else
  echo "  HN: 抓取结果为空，跳过"
fi

echo ""
echo "▶ [5/5] 跳过（Zara/OpenRouter 在 build.py 实时抓取）"

# ── 阶段 2：构建网站 ────────────────────────────────────────

echo ""
echo "▶ 构建网站..."
python3 "$WS/website/build.py" --date "$TODAY" 2>&1 || echo "  ⚠ build.py 失败"

# ── 阶段 3：推送 GitHub Pages ────────────────────────────────

echo ""
echo "▶ 推送 GitHub Pages..."
cd "$WS/website/dist"
TOKEN=$(gh auth token 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
  echo "  ⚠ gh auth token 失败，跳过推送"
else
  git add -A
  git commit -m "daily: $TODAY $(date +%H:%M) auto update" --allow-empty
  git remote set-url origin "https://zkw15555506767-boop:${TOKEN}@github.com/zkw15555506767-boop/zkevin-AI-dailynews.git"
  git push origin gh-pages && echo "  ✓ 推送完成" || echo "  ⚠ 推送失败"
fi

echo ""
echo "✅ 全部完成: $(date +%H:%M:%S)"
