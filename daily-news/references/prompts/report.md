# 日报生成提示词（v2）

## 生成前：确认日期范围

询问用户日期范围：

> 要生成哪个范围的日报？
> 1. 只要今天（默认）
> 2. 补上最近几天（自动检测上次日报日期）
> 3. 指定日期范围

```bash
# 今天
python3 scripts/db.py list-today --db <workspace>/data/news.db

# 指定范围
python3 scripts/db.py list-range --db <workspace>/data/news.db --from 2026-04-01 --to 2026-04-03
```

---

## 日报整体结构

按**信源分组**输出，顺序固定：

```
# Daily News · YYYY-MM-DD

## 导读

---

## Product Hunt               ← 固定第一
## GitHub Trending            ← 固定第二
## X / Twitter                ← 有数据时展示
## [其他信源...]              ← 按 source_id 字母序
```

---

## 一、导读

导读分**四个层次**，缺一不可。

---

### 1. 今日速览

5 条跨信源快讯，格式：

```markdown
## 导读

- **Product Hunt #1** · [产品名](url) — 一句话介绍
- **GitHub Trending** · 今日 N 个项目，[领跑项目](url) +N 星
- **X / Twitter** · 共 N 条精选，来自 ai-sweep 与 Zara Builder 精选；karpathy：...
- **Hacker News** · 今日 N 条技术讨论
- **OpenRouter 周冠军** · 模型名（提供商）N tokens
```

---

### 2. 今日洞察（3-5 条）

每条洞察必须包含三个子项，禁止只做新闻转述，必须有明确的方向性判断：

```markdown
#### 洞察标题（一句话点明核心信号）

- **信号**：今天哪些事件/数据触发了这条洞察（跨源交叉印证优先，附原始链接）
- **趋势**：这是偶发事件还是加速中的结构性趋势？处于趋势的哪个阶段？
- **PM 行动**：基于此洞察，产品经理现在应该关注 / 调整 / 布局什么？
```

**洞察选题优先级**：跨多个信源同时出现的主题 > 高互动推文反映的市场情绪 > 技术突破 > 产品发布

---

### 3. 今日一句话总结

用一句话高度概括今天 AI 行业的核心主题或最重要的转折点。要有画面感，不能是流水账。

```markdown
> 端侧跑模型、Agent 控工具链、中国免费模型横扫排行榜——AI 的重力中心正从「会不会」转向「谁的成本最低、离用户最近」。
```

---

### 4. 行业脉络与产品预判

分两层输出：

**① 本周/近期行业主线（2-3 条）**

每条包含：起点 → 当前位置 → 可能的下一步

```markdown
**主线 1：标题**
起点：... → 当前：... → 下一步：...
```

**② 产品与商业走向预判（3-5 条）**

要有具体的判断对象（哪家公司/哪类产品/哪个赛道），不能泛泛而谈：

```markdown
【预判1】判断内容
依据：来自今日哪些信号（附链接）

【预判2】...
```

---

## 二、Product Hunt 板块

展示今日 Top 30，**必须包含链接**。

### 格式

```markdown
## Product Hunt · Top 30

| 排名 | 产品 | 一句话 | 票数 |
|------|------|--------|------|
| 🥇 1 | [GPT-5.4](https://openai.com/gpt5) · [PH↗](https://www.producthunt.com/posts/gpt-5-4) | OpenAI 最强多模态模型 | 385 |
| 🥈 2 | [CoChat](https://cochat.ai) · [PH↗](https://www.producthunt.com/posts/cochat) | 团队版 AI Agent 工作台 | 255 |
| 🥉 3 | [SuperPowers AI](https://superpowers.ai) · [PH↗](https://...) | All-in-one AI 超级应用 | 250 |
| 4 | [Context Gateway](https://...) · [PH↗](https://...) | 跨 LLM 上下文管理层 | 202 |
...（到第 30 名）
```

### 链接规则

- 产品名链接到**官网**（`url` 字段）；若无官网则直接链到 PH 页面
- `[PH↗]` 始终链到 PH 产品页（`ph_url` 字段）
- Top 3 用 🥇🥈🥉 标注

### 无票数数据时的降级

如果票数未抓到，去掉票数列，仅保留排名、产品、一句话。

---

## 三、GitHub Trending 板块

展示当日**所有**上榜项目（通常 20-25 个），每个项目单独卡片式展示。

### 格式

```markdown
## GitHub Trending · 2026-04-03

**[owner/repo-name](https://github.com/owner/repo-name)**
`语言` · ⭐ 46,355 · +2,841 today

一句话介绍项目做什么。

- **亮点**：核心技术优势或独特功能
- **优势**：为什么值得关注，跟同类项目的差异
- **背景**：项目背后的故事/趋势/团队背景

---

**[owner/repo2](https://github.com/owner/repo2)**
...
```

### 字段说明

- 标题：`owner/repo` 格式，加粗，链接到 GitHub 仓库页
- 元信息行：语言 + 总星数 + 今日新增（格式 `+N today`）
- 亮点/优势/背景：各一条，简洁有信息量，不堆砌废话
- 条目间用 `---` 分隔

---

## 四、X / Twitter 板块（有数据时）

按搜索词的 label 分类展示，每类取 likes 最高的 3-5 条，全部合并去重后总计展示 **20-30 条**。

```markdown
## X / Twitter · AI 热帖

### 最新模型

**[@karpathy](https://x.com/karpathy)** · ❤ 8,241 · 👁 1.2M · [原文↗](https://x.com/i/status/xxx)

> The shift from "AI as a tool" to "AI as an agent" is not incremental. When the model can plan, retry, and remember — you're not using software anymore.

---

**[@sama](https://x.com/sama)** · ❤ 12,500 · 👁 2.8M · [原文↗](https://x.com/i/status/xxx)

> We underestimated how fast the ecosystem would move...

---

### AI Agent

**[@DrJimFan](https://x.com/DrJimFan)** · ❤ 3,870 · 👁 620K · [原文↗](https://x.com/i/status/xxx)

> Robotics + LLM is now a real combo...

---

### 最佳实践

...

### AI 编程

...
```

### 规则

- 分类顺序：最新模型 → AI Agent → AI 产品发布 → 最佳实践 → 开源模型 → MCP 工具 → AI 编程 → AI 研究 → AI 融资 → 中文 AI
- 每类最多 **3 条**，取该类 likes 最高的
- 类内按 likes 降序，类间按顺序固定
- 无数据的类别跳过
- 作者名链接到 `https://x.com/<author>`，末尾附 `[原文↗]` 链接到推文 url
- 推文原文用 `>` blockquote，保留完整原文不截断
- 条目间用 `---` 分隔

---

## 五、其他信源通用格式

适用于 36氪、机器之心、Hacker News 等文章类信源：

```markdown
## 36氪

**[文章标题](https://url)**
摘要内容（来自数据库 summary 字段，100-150 字）。
`2026-04-03` · ⭐⭐⭐⭐⭐

**[文章标题2](https://url)**
摘要内容。
`2026-04-03` · ⭐⭐⭐⭐
```

- 标题加粗带链接
- 摘要直接使用数据库 summary，不二次改写
- 末尾显示日期和星级（⭐ 对应 relevance_score）
- 按 relevance_score 降序排列，score=1 的条目放到该信源末尾折叠显示（Markdown 用 `<details>` 标签）

---

## 六、页脚

```markdown
---
*共收录 84 条 · 12 个信源 · daily-news v2*
```

---

## 注意事项

1. **链接必须完整**：所有标题、产品名、作者名都必须是可点击的 Markdown 链接 `[文字](url)`
2. **PH 和 GitHub 不做 relevance 过滤**：这两个信源展示所有条目，不按 relevance_score 截断
3. **推文不访问详情页**：detail_method=none 的条目直接用 title/full_text，不做 WebFetch
4. **空信源跳过**：当日无数据的信源板块整体不输出
