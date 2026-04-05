# opencli 方法（Twitter/X）

适用于需要从 X/Twitter 抓取内容的信源。
依赖 opencli 工具复用 Chrome 浏览器登录态，**无需 API key**。

## 前置条件

1. **opencli 已安装**
   ```bash
   npm install -g @jackwener/opencli
   opencli doctor   # 检查状态
   ```

2. **Chrome 已安装 opencli 扩展并连接**
   - 打开 Chrome，点击工具栏的 opencli 扩展图标
   - 点击 Connect，确保状态为已连接
   - 确保已登录 X（x.com）

3. **验证可用性**
   ```bash
   /usr/local/bin/opencli twitter search "AI" --limit 3 --format json
   ```
   返回推文数组则正常。

---

## 信源配置方式

Method 文件设置 `extends: opencli`，并在 `opencli` 字段指定命令：

```yaml
extends: opencli
opencli:
  cmd: twitter
  sub: search         # 子命令：search / trending / ai-sweep
  args:
    query: "AI agent"
    limit: 20
    filter: top       # top（热门）或 live（最新）
```

---

## 支持的子命令

### `search` — 按关键词搜索推文

```yaml
opencli:
  cmd: twitter
  sub: search
  args:
    query: "AI agent 2025"
    limit: 20
    filter: top
```

实际执行：
```bash
opencli twitter search "AI agent 2025" --filter top --limit 20 --format json
```

### `trending` — 获取热门话题

```yaml
opencli:
  cmd: twitter
  sub: trending
  args:
    limit: 10
```

实际执行：
```bash
opencli twitter trending --limit 10 --format json
```

### `ai-sweep` — AI 热点多词扫描（推荐）

不指定单一关键词，而是用 `scripts/fetch_twitter.py ai-sweep` 执行预设的多组搜索词，合并去重后返回：

```yaml
opencli:
  cmd: twitter
  sub: ai-sweep
  args:
    limit_per_query: 15
```

实际执行：
```bash
python3 scripts/fetch_twitter.py ai-sweep --limit-per-query 15
```

---

## 执行流程

```
1. 检查 opencli 可用性
   /usr/local/bin/opencli doctor

2. 根据 sub 执行命令
   python3 scripts/fetch_twitter.py <sub> [args]

3. 结果已是标准 JSON 数组，直接入库
   python3 scripts/db.py add-items-incremental \
     --db <db> --source <source_id> --items '<json>' --since <date>
```

---

## 输出格式

```json
[
  {
    "title": "@sama: OpenAI just shipped...",
    "url": "https://x.com/i/status/123456789",
    "published_at": "2026-04-03T08:00:00",
    "author": "sama",
    "likes": 3200,
    "views": "450000",
    "text": "OpenAI just shipped..."
  }
]
```

---

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| `opencli not found` | 未安装或不在 PATH | `npm install -g @jackwener/opencli` |
| `No connection to browser` | Chrome 扩展未连接 | 点击扩展图标 → Connect |
| 返回空数组 | X 登录态失效 | 在 Chrome 里重新登录 x.com |
| `env: node: No such file or directory` | Node.js 不在 PATH | 修复 PATH 或用完整路径调用 |
