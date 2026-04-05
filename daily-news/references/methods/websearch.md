# WebSearch 方法

适用于通过搜索引擎发现最新资讯的信源。
弥补 RSS/WebFetch 信源的盲区，抓取更广泛的 AI 新闻。

## 使用场景

- 没有固定 URL 的动态话题（如"AI 最新进展"）
- 需要跨站聚合多个来源
- 作为其他信源的补充扫描

---

## 信源配置方式

```yaml
extends: websearch
websearch:
  queries:
    - "Claude GPT Gemini new release 2025"
    - "AI agent autonomous announcement"
  days: 2        # 只取最近 N 天的结果
  limit: 10      # 每个 query 最多返回 N 条
```

---

## 执行流程

对每个 `query` 执行 WebSearch，合并去重：

```
for query in websearch.queries:
    results = WebSearch(query)
    for r in results:
        if r.url not in seen and is_within_days(r.published_at, days):
            items.append(format_item(r))
            seen.add(r.url)
```

### 结果格式化

```json
{
  "title": "文章标题",
  "url": "https://example.com/article",
  "published_at": "2026-04-03T10:00:00",
  "source_domain": "example.com",
  "snippet": "文章摘要片段..."
}
```

### 去重规则

- 主键：`url`
- 跨 query 去重（seen_urls set）
- 跨信源去重（数据库 UNIQUE 约束）

---

## 查询策略建议

| 场景 | 查询示例 |
|------|---------|
| 大模型新闻 | `"Claude OR GPT OR Gemini release 2025"` |
| AI 产品发布 | `"AI product launch announcement site:techcrunch.com OR site:venturebeat.com"` |
| 中文 AI 资讯 | `"AI 大模型 最新 site:36kr.com OR site:jiqizhixin.com"` |
| 开源模型 | `"open source LLM released github"` |
| AI 融资 | `"AI startup funding million 2025"` |

---

## 注意事项

- WebSearch 有速率限制，单次 query 不宜超过 20 条
- 发布时间可能不准确（部分搜索结果无 `published_date`），会 fallback 到当前时间
- 对于高质量的固定来源，优先用 `rss` 或 `webfetch-smart`，websearch 作为补充
