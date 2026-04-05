---
name: daily-news
version: "2.0.0"
description: |
  每日资讯日报生成器 v2。三阶段工作流：获取元数据、生成摘要、输出日报。
  v2 新增：opencli 抓取 X/Twitter AI 热帖、WebSearch 搜索补充信源、数据库 V3 迁移。
  触发场景：每日新闻、资讯日报、信息监控、新闻聚合、daily news、生成日报、刷 X、抓推文。
  也用于添加新信源（自动分析网页并生成 method 文件）。
---

# Daily News v2

三阶段工作流：**获取元数据** → **生成摘要** → **输出日报**

---

## 工作目录

首次运行询问工作目录路径（如 `~/daily-news`），后续记住。

```
<workspace>/
├── profile.yaml          # 用户画像（关于我、关注什么）
├── settings.yaml         # 日报设置（语言、格式偏好）
├── methods/              # 信源获取方法
├── data/news.db          # SQLite 数据库
└── output/YYYY-MM-DD.md  # 日报输出
```

### 初始化

```bash
mkdir -p <workspace>/methods <workspace>/data <workspace>/output
cp references/examples/settings.example.yaml <workspace>/settings.yaml
cp references/examples/profile.example.yaml <workspace>/profile.yaml
python3 scripts/db.py init --db <workspace>/data/news.db
```

初始化完成后：
1. 将工作目录写入用户的 `~/.claude/CLAUDE.md`，追加：
   ```
   - daily-news skill 的项目目录在：<workspace>
   ```
2. 询问用户是否需要调整画像。

### 数据库升级（已有 v1/v2 用户）

如果是已有数据库，执行迁移脚本：

```bash
# 升级到 V2（增量抓取支持）
sqlite3 <workspace>/data/news.db < scripts/migrate_v2.sql

# 升级到 V3（Twitter 字段 + WebSearch domain 字段）
sqlite3 <workspace>/data/news.db < scripts/migrate_v3.sql
```

V3 新增字段（items 表）：`author`、`likes`、`views`、`full_text`、`source_domain`

---

## 阶段 0：选择抓取日期范围

在执行抓取前，询问用户：

```
请选择抓取时间范围：
1. 今天（默认）
2. 昨天
3. 最近3天
4. 最近7天
5. 从上次抓取至今（增量）
6. 自定义日期范围
```

每个信源独立追踪 `last_fetched_date`（记录在 method 文件 + `source_status` 表）。

```bash
python3 scripts/db.py source-status --db <db> --source <source_id>
```

---

## 阶段 1：获取元数据

遍历 `<workspace>/methods/` 目录，对每个 enabled method 执行抓取。

### Method 类型判断

读取 method 文件的 `extends` 字段：

| extends | 执行方式 | 说明 |
|---------|---------|------|
| `rss` | `python3 references/methods/rss.py` | 最快，有 RSS 时首选 |
| `webfetch-smart` | 见 `references/methods/webfetch-smart.md` | 大多数网站 |
| `browser-smart` | 见 `references/methods/browser-smart.md` | JS 渲染 / 需登录 |
| `opencli` | 见 `references/methods/opencli.md` | X/Twitter、Product Hunt、HN、36kr 等 |
| `github-trending-smart` | `python3 scripts/fetch_github_trending.py` | GitHub Trending 专属，opencli operate 抓取 |
| `websearch` | 见 `references/methods/websearch.md` | 搜索补充信源 |
| 无 extends | 直接执行脚本（.py）或按指引（.md） | 完全自定义 |

### opencli 信源执行（v2 新增）

检查 opencli 可用性：

```bash
/usr/local/bin/opencli doctor
```

**如果不可用：**
```
opencli 未安装或扩展未连接。请：
1. 安装：npm install -g @jackwener/opencli
2. 打开 Chrome → 点击 opencli 扩展 → Connect
3. 确保已登录 x.com
跳过此信源，继续其他信源？[Y/n]
```

**如果可用，执行抓取：**

```bash
# ai-sweep 模式（推荐）
python3 scripts/fetch_twitter.py ai-sweep --limit-per-query 15

# 或 search 模式
python3 scripts/fetch_twitter.py search \
  --query "<opencli.args.query>" \
  --limit <opencli.args.limit> \
  --filter <opencli.args.filter>

# 或 trending 模式
python3 scripts/fetch_twitter.py trending --limit <opencli.args.limit>
```

结果已是标准 JSON 数组，直接入库。推文 `detail_method: none`，跳过阶段 2 的详情抓取。

### websearch 信源执行（v2 新增）

读取 method 文件的 `websearch.queries` 列表，逐一执行 WebSearch：

```
for query in method.websearch.queries:
    results = WebSearch(query)
    for r in results:
        if r.url not in seen_urls and is_within_days(r, method.websearch.days):
            items.append({
                "title": r.title,
                "url": r.url,
                "published_at": r.published_date or now,
                "source_domain": urlparse(r.url).netloc
            })
            seen_urls.add(r.url)
```

`detail_method` 默认为 `fetch`，阶段 2 会抓取详情页全文。

### 去重与入库

```bash
# 增量入库（自动去重 + 记录同步日志）
python3 scripts/db.py add-items-incremental \
  --db <workspace>/data/news.db \
  --source <source_id> \
  --items '<json>' \
  --since "<date>"
```

### browser-smart 检查（同 v1）

如有信源 `extends: browser-smart`，执行前检查 Browser MCP 配置，见 `references/methods/browser-smart.md`。

---

## 阶段 2：生成摘要

```bash
python3 scripts/db.py list-pending --db <workspace>/data/news.db
```

对每条内容，根据 method 的 `detail_method` 获取正文：

| detail_method | 获取方式 |
|---------------|---------|
| `fetch` | WebFetch（快） |
| `browser` | Browser MCP（慢） |
| `none` | 跳过（推文直接用 `full_text` / title） |
| 未指定 | 默认 `fetch` |

**推文的摘要生成**：`detail_method: none` 的条目跳过正文抓取，直接用 `full_text`（即推文原文）生成摘要，评分参考用户画像的 AI 关注点。

按 `references/prompts/summary.md` 生成摘要，更新数据库：

```bash
python3 scripts/db.py update-summary \
  --db <workspace>/data/news.db \
  --id <item_id> \
  --data '<摘要JSON>'
```

---

## 阶段 3：生成日报

```bash
python3 scripts/db.py list-today --db <workspace>/data/news.db
```

读取 `<workspace>/profile.yaml`，按 `references/prompts/report.md` 生成日报。
输出到 `<workspace>/output/YYYY-MM-DD.md`。

日报中 X/Twitter 推文条目额外展示互动数据（likes / views），格式：
```markdown
**[@sama: OpenAI just shipped...](https://x.com/i/status/xxx)**
OpenAI 宣布...摘要内容...
`twitter-ai-trending` · `2026-04-03` · ❤️ 3.2k · 👁 450k
```

---

## 添加信源

### v2 新增信源类型

**添加 X/Twitter 信源：**

1. 从 `references/examples/twitter-ai-trending.example.yaml` 复制模板
2. 修改 `source_id`、`opencli.args.query`
3. 保存到 `<workspace>/methods/`

**添加 WebSearch 信源：**

1. 从 `references/examples/websearch-ai-news.example.yaml` 复制模板
2. 修改 `websearch.queries`
3. 保存到 `<workspace>/methods/`

### 原有信源添加流程（v1 保留）

按优先级依次尝试：RSS → WebFetch → 浏览器。
详见 `references/schemas/method.md`。

---

## settings.yaml 配置项说明

工作区的 `settings.yaml` 控制日报的完整行为：

```yaml
# 基础
language: zh-CN                    # 输出语言
show_low_priority: false           # 是否展示低相关度内容

# 自动更新
auto_update:
  enabled: false                   # 开启后按计划自动抓取
  frequency: daily                 # daily / weekly
  hour: 8                          # 每天几点运行（本地时间）
  auto_report: true                # 抓完自动生成日报

# 输出方式
output:
  format: markdown                 # markdown / html / both
  deploy_website: false            # 是否部署到网站
  auto_git_push: false             # 生成后自动 git push

# 信源控制
sources:
  default_date_range: today        # today / yesterday / last-3-days / incremental
  twitter:
    limit_per_query: 15            # 每个关键词抓取条数
    min_likes: 50                  # 过滤低质量推文
  github:
    since: daily                   # daily / weekly / monthly
  producthunt:
    limit: 30                      # 抓取前 N 名

# 日报生成
report:
  twitter_max_per_category: 3      # X 每个话题最多展示几条
  hackernews_max: 20
  kr36_max: 15
```

修改 `settings.yaml` 后，下次运行日报自动生效。

```yaml
about: |
  （关于我：身份、工作）
focus: |
  （当前关注）
low_priority: |
  （不太关心）
```

首次初始化时询问，可随时通过"更新画像"更新。

---

## 参考资料

| 资料 | 路径 | 加载时机 |
|------|------|---------|
| Method 规范 | `references/schemas/method.md` | 添加信源时 |
| 摘要提示词 | `references/prompts/summary.md` | 阶段 2 |
| 日报提示词 | `references/prompts/report.md` | 阶段 3 |
| RSS 方法 | `references/methods/rss.py` | extends: rss |
| WebFetch 方法 | `references/methods/webfetch-smart.md` | extends: webfetch-smart |
| 浏览器方法 | `references/methods/browser-smart.md` | extends: browser-smart |
| **opencli 方法** | **`references/methods/opencli.md`** | **extends: opencli（v2 新增）** |
| **WebSearch 方法** | **`references/methods/websearch.md`** | **extends: websearch（v2 新增）** |
| Twitter 信源示例 | `references/examples/twitter-ai-trending.example.yaml` | 添加 X 信源时 |
| Twitter 搜索示例 | `references/examples/twitter-ai-search.example.yaml` | 添加 X 信源时 |
| WebSearch 信源示例 | `references/examples/websearch-ai-news.example.yaml` | 添加 WebSearch 信源时 |
| 设置示例 | `references/examples/settings.example.yaml` | 初始化 |
| 画像示例 | `references/examples/profile.example.yaml` | 初始化 |
| Method 元数据示例 | `references/examples/method-with-metadata.example.yaml` | 增量抓取配置 |

---

## 数据库命令参考

```bash
# 初始化
python3 scripts/db.py init --db <db>

# 增量添加条目
python3 scripts/db.py add-items-incremental --db <db> --source <id> --items '<json>' --since "2026-04-01"

# 检查 URL 是否已存在
python3 scripts/db.py check-existing --db <db> --urls '["url1","url2"]'

# 查看信源同步状态
python3 scripts/db.py source-status --db <db> --source <id>

# 查看同步日志
python3 scripts/db.py sync-log --db <db> --source <id> --limit 10

# 列出待处理条目（阶段 2）
python3 scripts/db.py list-pending --db <db>

# 列出今日内容（阶段 3）
python3 scripts/db.py list-today --db <db>

# 数据库迁移
sqlite3 <db> < scripts/migrate_v2.sql   # v1 → v2
sqlite3 <db> < scripts/migrate_v3.sql   # v2 → v3（v2 新增）
```

---

## 依赖

```bash
# Python
pip install pyyaml feedparser requests beautifulsoup4

# opencli（X/Twitter 信源）
npm install -g @jackwener/opencli

# Browser MCP（browser-smart 信源，可选）
# 安装 Chrome 扩展：https://chromewebstore.google.com/detail/bjfgambnhccakkhmkepdoekmckoijdlc
```

---

## 网站部署（可选）

日报生成后可部署为静态网站，使用内置模板：

```bash
cp -r references/website-template <workspace>/website
cd <workspace>/website && python3 build.py
```

支持 Cloudflare Pages、GitHub Pages、Vercel 等平台。
详见 `<workspace>/website/README.md`。
