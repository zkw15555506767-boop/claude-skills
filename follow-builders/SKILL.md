---
name: follow-builders
description: "AI Builder 动态追踪：抓取 AI 领域知名 builder 的 X/Twitter 推文、播客更新、技术博客，整合成摘要。当用户想了解 AI builder 社区动态、生成 builder 周报/日报时使用。"
github_url: https://github.com/zarazhangrui/follow-builders
version: 0.1.0
entry_point: scripts/prepare-digest.js
---

# follow-builders

追踪 25+ AI builder 的 X 推文、Latent Space 等播客、Anthropic 技术博客，输出结构化 JSON 供 AI 编辑使用。

## 核心流程

```bash
# 获取所有 feeds（输出 JSON 到 stdout）
node ~/.claude/skills/follow-builders/scripts/prepare-digest.js
```

JSON 输出结构：`{ x: [...], podcasts: [...], blogs: [...], prompts: {...}, config: {...} }`

## 用户配置

配置文件：`~/.follow-builders/config.json`

```json
{
  "language": "zh",
  "delivery": { "method": "stdout" }
}
```

## 与 daily-news 联动（自动化日报）

参见 `~/daily-news/generate-digest.sh` — 每天 10:00 自动运行完整管道。
