# AI-source · 信源配置目录

daily-news v2 当前启用的所有信源配置。

## 信源列表

| 文件 | 信源 | 获取方式 | 说明 |
|------|------|---------|------|
| `product-hunt.yaml` | Product Hunt | `opencli producthunt posts` | 今日热榜 Top 30 |
| `github-trending.yaml` | GitHub Trending | `scripts/fetch_github_trending.py` | opencli operate 读 DOM |
| `twitter-ai-trending.yaml` | X/Twitter AI 热帖 | `scripts/fetch_twitter.py ai-sweep` | 10 组关键词并发抓取 |
| `twitter-ai-search.yaml` | X/Twitter 搜索 | `scripts/fetch_twitter.py search` | 单关键词搜索 |
| `zara-feed.yaml` | Zara Builder Feed | `scripts/fetch_zara_feed.py` | karpathy 等 25 位 builder 精选 |
| `hacker-news.yaml` | Hacker News | `opencli hackernews top` | Top 30 |
| `openrouter.yaml` | OpenRouter | `scripts/fetch_openrouter.py` | LLM 周使用量排行 |

## 使用方式

将需要的 yaml 文件复制到工作区的 `methods/` 目录：

```bash
cp AI-source/*.yaml ~/daily-news/methods/
```

## 禁用某个信源

将对应 yaml 文件中的 `enabled: true` 改为 `enabled: false` 即可。
