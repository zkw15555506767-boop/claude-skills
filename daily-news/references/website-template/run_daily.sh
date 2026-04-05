#!/bin/bash
# ============================================================
# Daily News v2 · 每日自动运行脚本
# 路径: ~/daily-news/run_daily.sh
# 由 launchd 每天早上 8:00 触发
# ============================================================

set -e

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

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

# ── 阶段 1：抓取各信源 ──────────────────────────────────────

echo ""
echo "▶ [1/5] Product Hunt..."
PH_RAW=$(opencli producthunt posts --limit 30 --format json 2>&1)
PH_ITEMS=$(echo "$PH_RAW" | python3 -c "
import json,sys
decoder = json.JSONDecoder()
raw = sys.stdin.read().strip()
data, _ = decoder.raw_decode(raw)
items=[{'title':f'{i+1}. {p[\"name\"]} — {p[\"tagline\"]}','url':p['url'],'published_at':'${TODAY}T00:00:00'} for i,p in enumerate(data)]
print(json.dumps(items,ensure_ascii=False))
")
python3 "$SKILL/scripts/db.py" add-items-incremental \
  --db "$DB" --source product-hunt \
  --items "$PH_ITEMS" --since "$TODAY" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  PH: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')"

echo ""
echo "▶ [2/5] GitHub Trending..."
python3 "$SKILL/scripts/fetch_github_trending.py" > /tmp/dn_gh.json 2>&1
GH_ITEMS=$(cat /tmp/dn_gh.json)
python3 "$SKILL/scripts/db.py" add-items-incremental \
  --db "$DB" --source github-trending \
  --items "$GH_ITEMS" --since "$TODAY" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  GH: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')"

echo ""
echo "▶ [3/5] X/Twitter ai-sweep..."
TW_ITEMS=$(python3 "$SKILL/scripts/fetch_twitter.py" ai-sweep --limit-per-query 15 2>&1 | grep -v '^\[')
python3 "$SKILL/scripts/db.py" add-items-incremental \
  --db "$DB" --source twitter-ai-trending \
  --items "$TW_ITEMS" --since "$(date -v-1d +%Y-%m-%d)" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  TW: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')"

echo ""
echo "▶ [4/5] Hacker News..."
HN_RAW=$(opencli hackernews top --limit 30 --format json 2>&1)
HN_ITEMS=$(echo "$HN_RAW" | python3 -c "
import json,sys
data=json.load(sys.stdin)
items=[{'title':f'{p[\"rank\"]}. {p[\"title\"]}','url':p.get('url','https://news.ycombinator.com'),'published_at':'${TODAY}T00:00:00'} for p in data if p.get('url')]
print(json.dumps(items,ensure_ascii=False))
")
python3 "$SKILL/scripts/db.py" add-items-incremental \
  --db "$DB" --source hacker-news \
  --items "$HN_ITEMS" --since "$TODAY" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  HN: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')"

echo ""
echo "▶ [5/5] Hacker News..."
HN_RAW=$(opencli hackernews top --limit 30 --format json 2>&1)
HN_ITEMS=$(echo "$HN_RAW" | python3 -c "
import json,sys
data=json.load(sys.stdin)
items=[{'title':f'{p[\"rank\"]}. {p[\"title\"]}','url':p.get('url','https://news.ycombinator.com'),'published_at':'${TODAY}T00:00:00'} for p in data if p.get('url')]
print(json.dumps(items,ensure_ascii=False))
")
python3 "$SKILL/scripts/db.py" add-items-incremental \
  --db "$DB" --source hacker-news \
  --items "$HN_ITEMS" --since "$TODAY" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'  HN: 抓 {d[\"fetched\"]} 条，新增 {d[\"added\"]} 条')"

# ── 阶段 2：构建网站 ────────────────────────────────────────

echo ""
echo "▶ 构建网站..."
python3 "$WS/website/build.py" --date "$TODAY" 2>&1

# ── 阶段 3：推送 GitHub Pages ────────────────────────────────

echo ""
echo "▶ 推送 GitHub Pages..."
cd "$WS/website/dist"
TOKEN=$(gh auth token 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
  echo "  ⚠ gh auth token 失败，跳过推送"
else
  git add -A
  git commit -m "daily: $TODAY auto update" --allow-empty
  git remote set-url origin "https://zkw15555506767-boop:${TOKEN}@github.com/zkw15555506767-boop/zkevin-AI-dailynews.git"
  git push origin gh-pages
  echo "  ✓ 推送完成"
fi

echo ""
echo "✅ 全部完成: $(date +%H:%M:%S)"
