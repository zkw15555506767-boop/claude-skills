# Method 文件规范（v2）

Method 文件定义如何从信源获取内容。存放在 `<workspace>/methods/` 目录。

## 文件类型

| 类型 | 后缀 | 适用场景 |
|------|------|---------|
| 配置 | `.yaml` | 使用 extends 引用通用方法（推荐） |
| 脚本 | `.py` | 完全自定义获取逻辑 |
| 指引 | `.md` | 需要 AI 按步骤操作 |

---

## 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `source_id` | 是 | 唯一标识，用于数据库关联 |
| `source_name` | 是 | 显示名称 |
| `source_url` | 是 | 信源首页 URL（websearch 填占位） |
| `enabled` | 是 | 是否启用（true/false） |
| `extends` | 否 | 引用通用方法（见下文） |
| `detail_method` | 否 | 详情页获取方式，默认 `fetch` |
| `date_range` | 否 | 日期范围过滤 |
| `opencli` | 否 | opencli 命令配置（`extends: opencli` 时必填）⭐v2 |
| `websearch` | 否 | WebSearch 查询配置（`extends: websearch` 时必填）⭐v2 |

---

## extends 字段（v2）

| 值 | 适用场景 | 参考文档 |
|----|---------|---------|
| `rss` | 有 RSS feed | `references/methods/rss.py` |
| `webfetch-smart` | 大多数网站 | `references/methods/webfetch-smart.md` |
| `browser-smart` | JS 渲染/反爬/需登录 | `references/methods/browser-smart.md` |
| `opencli` | X/Twitter 等社交平台 ⭐v2 | `references/methods/opencli.md` |
| `websearch` | 动态话题、跨站聚合 ⭐v2 | `references/methods/websearch.md` |

---

## detail_method 字段（v2）

控制**阶段 2**获取详情页正文的方式。

| 值 | 工具 | 速度 | 适用场景 |
|----|------|------|---------|
| `fetch` | WebFetch | 快 | 服务端渲染页面（默认） |
| `browser` | Browser MCP | 慢 | JS 渲染或需登录 |
| `none` | — | 最快 | 推文/snippet 已有正文，跳过详情页 ⭐v2 |

---

## date_range 字段

```yaml
date_range:
  type: relative   # relative / since / between
  days: 1
```

| type | 字段 | 说明 |
|------|------|------|
| `relative` | `days` | 最近 N 天 |
| `since` | `date` | 从指定日期至今 |
| `between` | `from` / `to` | 指定区间 |

---

## 示例

### RSS 信源

```yaml
source_id: anthropic-news
source_name: Anthropic News
source_url: https://anthropic.com/rss.xml
enabled: true
extends: rss
detail_method: fetch
```

### WebFetch 信源

```yaml
source_id: hacker-news
source_name: Hacker News
source_url: https://news.ycombinator.com/
enabled: true
extends: webfetch-smart
detail_method: fetch
date_range:
  type: relative
  days: 1
```

### opencli 信源（X/Twitter AI 搜索）⭐v2

```yaml
source_id: twitter-ai-search
source_name: X/Twitter AI 搜索
source_url: https://x.com/search?q=AI&f=top
enabled: true
extends: opencli
detail_method: none

opencli:
  cmd: twitter
  sub: search
  args:
    query: "AI agent OR LLM OR Claude OR GPT"
    limit: 30
    filter: top

date_range:
  type: relative
  days: 1
```

### opencli 信源（X AI 热帖多词扫描）⭐v2

```yaml
source_id: twitter-ai-trending
source_name: X/Twitter AI 热点
source_url: https://x.com/search?q=AI&f=top
enabled: true
extends: opencli
detail_method: none

opencli:
  cmd: twitter
  sub: ai-sweep
  args:
    limit_per_query: 15

date_range:
  type: relative
  days: 1
```

### WebSearch 信源⭐v2

```yaml
source_id: websearch-ai-news
source_name: WebSearch AI 资讯
source_url: https://www.google.com
enabled: true
extends: websearch
detail_method: fetch

websearch:
  queries:
    - "Claude GPT Gemini new release announcement"
    - "AI agent 最新进展 发布"
  days: 2
  limit: 10
```

---

## 输出格式

所有 method 输出必须是 JSON 数组：

```json
[
  {
    "title": "文章标题或推文内容",
    "url": "https://example.com/article/1",
    "published_at": "2026-04-03T10:00:00",
    "author": "可选，作者",
    "likes": 0,
    "views": "0",
    "text": "可选，推文完整原文",
    "source_domain": "可选，websearch 来源域名"
  }
]
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `title` | 是 | 标题或推文摘要（≤120字符） |
| `url` | 是 | 唯一链接 |
| `published_at` | 否 | ISO 8601 时间 |
| `author` | 否 | 推文作者（X 信源） |
| `likes` | 否 | 点赞数（X 信源） |
| `views` | 否 | 浏览数（X 信源） |
| `text` | 否 | 推文完整原文（detail_method: none 时用于摘要） |
| `source_domain` | 否 | 来源域名（websearch 信源） |
