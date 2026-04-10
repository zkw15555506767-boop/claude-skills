# Daily News v2 · 踩坑记录

> 记录开发和运行过程中遇到的所有问题、根本原因和解决方案。

---

## 坑 1：`set -e` 导致定时任务静默失败

**现象**：launchd 日志为空，脚本 exit code = 1，什么都没执行。

**根因**：`run_daily.sh` 开头有 `set -e`，任何一步报错（比如 GitHub Trending 返回空 JSON）就立即中断，连日志重定向都没来得及执行。

**解决**：去掉 `set -e`，改为每个信源单独加 `|| true`，用 `is_valid_json_array()` 检查结果，空则跳过，不影响后续步骤。

---

## 坑 2：`opencli producthunt posts` 数据与首页不一致

**现象**：PH 展示的产品和 producthunt.com 首页排行完全对不上。

**根因**：
- `posts` 命令返回的是"最新发布"，不按票数排序
- `today` 命令按 PST 时区，中国时间下午才切换，上午拿到的是昨天数据
- `hot` 命令需要浏览器已打开 PH 页面才能捕获网络请求，无 Chrome 时报 `No network capture within 5s`

**解决**：新建 `fetch_producthunt.py`，通过 `opencli operate open` 打开 PH 首页，等待渲染后用 `operate eval` 读 `[data-test^="post-item-"]` DOM 节点，直接解析排名、名称、tagline、票数。与首页完全一致。

---

## 坑 3：PH 数据库 URL 全局唯一约束导致跨日期冲突

**现象**：PH 入库报 `UNIQUE constraint failed: items.url`，或者 upsert 后旧日期产品混入今天，导致排序混乱、每个排名出现两条。

**根因**：`items.url` 是全局唯一索引。同一个 PH 产品（如 AppSignal）今天和昨天 URL 相同，只能存一条。先 `DELETE WHERE DATE=today` 再 INSERT 不行——昨天的记录还在，INSERT 会冲突。用 UPSERT（ON CONFLICT DO UPDATE）会更新旧记录的 published_at，导致昨天产品也出现在今天。

**解决**：每次抓取前 `DELETE FROM items WHERE source_id='product-hunt'`（全量删除），再按 rank 排序插入今日最新 30 条。PH 数据不需要历史积累，每天完整替换即可。

---

## 坑 4：PH tagline 全部显示 "ALPHA"

**现象**：某次抓取 PH 所有产品的 tagline 都是 "ALPHA"。

**根因**：Product Hunt 有时会开 "Alpha Day" 活动，首页每个产品卡片的 tagline 位置被活动标签 "ALPHA" 覆盖。这是 PH 的时效性问题，不是代码 bug。

**解决**：该时间段内数据不准确，等活动结束后下次定时任务重新抓即可。无需代码修改。

---

## 坑 5：PH 展示顺序乱（排名 1、2、4、3、6）

**现象**：网站上 PH 不是按 1→30 顺序展示，排名跳跃。

**根因**：`render_ph()` 里缺少排序，直接遍历数据库返回顺序（INSERT 顺序不保证）。

**解决**：在 `render_ph()` 里加一行：
```python
items = sorted(items, key=lambda p: int(re.match(r'^(\d+)\.', p.get('title','')).group(1)) if re.match(r'^(\d+)\.', p.get('title','')) else 999)
```
同时入库时也按 `_rank` 排序插入，双重保证。

---

## 坑 6：GitHub Trending 信息抓取为空

**现象**：某次抓取 GitHub Trending 返回 0 条或 7 条（应为 20+ 条）。

**根因**：
- 最初用 Jina Reader 抓 `github.com/trending`，Jina 对 GitHub 的解析不稳定，部分项目丢失
- 后来改用 `opencli operate eval` 读 DOM，但 DOM 加载时机不稳定，有时页面未渲染完就执行了 JS

**解决**：`fetch_github_trending.py` 中打开页面后 `sleep 5` 等待渲染，再执行 eval。GitHub Trending 数据在 `build.py` 实时抓取（不入库），每次 build 时重新拉取，不依赖数据库历史。

---

## 坑 7：Google Translate SSL 超时导致 build 卡死

**现象**：`build.py` 跑到翻译环节卡住，SSL EOF 报错，整个 build 超时崩掉，push 没执行。

**根因**：`deep_translator` 调用 `translate.google.com`，在某些网络状态下 SSL 握手超时，且没有设置超时时间，会一直等。

**现状**：翻译失败时 fallback 显示英文原文，不影响整体流程。但 build 时间会拉长。

**待优化**：给 `translate.py` 加请求超时（`timeout=5s`），超时直接返回原文，不阻塞整个 build。

---

## 坑 8：launchd 旧任务残留

**现象**：系统里同时存在 5 个 daily-news 相关的 launchd 任务（`com.dailynews.update-02/10/14/20` + `com.zkevin.dailynews`），重复执行。

**根因**：v1 时创建了 4 个旧任务，v2 时新建了 1 个，没有清理旧的。

**解决**：`launchctl unload` + `rm` 清除旧的 4 个 plist，只保留 `com.zkevin.dailynews`（11:00 / 14:00 / 21:00）。

---

## 坑 9：GitHub 推送 SSL 报错

**现象**：`git push` 报 `LibreSSL SSL_connect: SSL_ERROR_SYSCALL`。

**根因**：网络波动，GitHub 连接不稳定（非代码问题）。

**解决**：重试即可。`run_daily.sh` 里已加 `|| echo "推送失败"` 容错，不会中断整体流程。

---

## 坑 10：浏览器缓存导致看到旧数据

**现象**：明明已经推送新数据到 GitHub Pages，网站上显示的还是昨天的内容。

**根因**：浏览器/GitHub Pages CDN 缓存，不是数据本身的问题。

**解决**：`Cmd + Shift + R` 强制刷新即可。

---

## 当前已知待优化项

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 翻译超时 | 中 | `translate.py` 加 5s 超时，避免 build 卡死 |
| opencli 版本过旧 | 低 | 当前 v1.6.1，最新 v1.7.0，运行时一直提示更新 |
| git commit 无 user.name | 低 | 每次 commit 有警告，可 `git config --global user.name/email` 配置 |
| HN 偶发 fetch failed | 低 | `opencli hackernews` 偶尔报网络错误，已容错跳过 |
