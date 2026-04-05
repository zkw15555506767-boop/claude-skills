# Product Hunt Top 30 抓取指引（Browser MCP）

Product Hunt 是重度 JS 渲染站点，webfetch 只能拿到空壳，必须使用 Browser MCP。
本指引告诉 agent 如何用 Browser MCP 抓取今日 Top 30，包含票数、官网链接。

---

## 前置检查

```
调用 mcp__browsermcp__browser_snapshot 测试 Browser MCP 连接
```

- 正常 → 继续
- 无响应 → 提示用户点击 Chrome 工具栏的 Browser MCP 扩展 → Connect

---

## 步骤一：打开今日榜单

```
调用 mcp__browsermcp__browser_navigate
参数: {"url": "https://www.producthunt.com/leaderboard/daily/2026/4/3"}
```

> 日期参数格式：`/leaderboard/daily/YYYY/M/D`（月份和日期不补零）
> 当前日期由 agent 动态计算。

等待页面加载：
```
调用 mcp__browsermcp__browser_wait
参数: {"time": 3}
```

---

## 步骤二：滚动加载更多产品

Product Hunt 列表懒加载，默认只显示约 10 条，需要滚动触发加载：

```
调用 mcp__browsermcp__browser_evaluate
参数: {"script": "window.scrollTo(0, document.body.scrollHeight)"}
```

重复滚动 3-4 次，每次等待 1.5 秒：
```
调用 mcp__browsermcp__browser_wait
参数: {"time": 2}
```

---

## 步骤三：提取产品数据

```
调用 mcp__browsermcp__browser_evaluate
参数:
{
  "script": "
    const items = [];
    // Product Hunt 产品卡片选择器
    const cards = document.querySelectorAll('[data-test=\"homepage-section-item\"], [class*=\"item_\"]');
    
    cards.forEach((card, i) => {
      if (i >= 30) return;
      
      // 产品名
      const nameEl = card.querySelector('h3, [class*=\"name\"], [data-test*=\"name\"]');
      // tagline
      const tagEl = card.querySelector('[class*=\"tagline\"], p');
      // PH 页面链接
      const linkEl = card.querySelector('a[href*=\"/posts/\"], a[href*=\"/products/\"]');
      // 票数
      const voteEl = card.querySelector('[class*=\"vote\"], button[class*=\"voteButton\"]');
      // 话题标签
      const topicEls = card.querySelectorAll('[class*=\"topic\"], [data-test*=\"topic\"]');
      
      const name = nameEl?.innerText?.trim();
      const tagline = tagEl?.innerText?.trim();
      const ph_url = linkEl ? 'https://www.producthunt.com' + linkEl.getAttribute('href') : '';
      const votes = voteEl?.innerText?.trim()?.replace(/[^0-9]/g, '') || '0';
      const topics = Array.from(topicEls).map(t => t.innerText.trim()).filter(Boolean).slice(0, 3);
      
      if (name) {
        items.push({ rank: i + 1, name, tagline, ph_url, votes: parseInt(votes) || 0, topics });
      }
    });
    
    return JSON.stringify(items);
  "
}
```

---

## 步骤四：获取每个产品的官网链接

对 Top 30 中每个产品，访问其 PH 页面提取官网 URL：

```
调用 mcp__browsermcp__browser_navigate
参数: {"url": "<ph_url>"}

调用 mcp__browsermcp__browser_evaluate
参数:
{
  "script": "
    // PH 产品页上的官网跳转按钮
    const visitBtn = document.querySelector('a[data-test=\"visit-button\"], a[href*=\"ref=producthunt\"], [class*=\"visitButton\"] a');
    return visitBtn ? visitBtn.href : '';
  "
}
```

> 为节省时间，官网链接可以只获取 Top 10，其余仅提供 PH 链接。

---

## 步骤五：组装输出 JSON

```json
[
  {
    "title": "1. GPT-5.4",
    "url": "https://gpt5.openai.com",
    "ph_url": "https://www.producthunt.com/posts/gpt-5-4",
    "tagline": "OpenAI 最强多模态模型，推理全面升级",
    "votes": 385,
    "topics": ["AI", "Productivity"],
    "rank": 1,
    "published_at": "2026-04-03"
  }
]
```

`url` 优先填官网，没有则填 `ph_url`。

---

## 备用方案：GraphQL API

如果 Browser MCP 抓取失败，可尝试 PH GraphQL API（需 token）：

```bash
# 需要在 https://www.producthunt.com/v2/oauth/applications 申请 access token
curl -s "https://api.producthunt.com/v2/api/graphql" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ posts(order: VOTES, postedAfter: \"2026-04-03T00:00:00Z\") { edges { node { name tagline votesCount website url } } } }"}'
```

---

## 注意事项

- PH 每天 00:01 PT（太平洋时间）重置榜单，注意日期换算
- `browser_snapshot` 比 `evaluate` 慢，优先用 evaluate 提取数据
- 票数排序有时不准确（榜单顺序 ≠ 票数降序），以页面显示顺序为准
