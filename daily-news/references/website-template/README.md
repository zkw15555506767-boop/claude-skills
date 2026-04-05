# Daily News v2 · 换设备部署指南

> **信源配置**：所有启用的信源 yaml 文件统一存放在 [`daily-news/AI-source/`](../AI-source/)，包含 Product Hunt、GitHub Trending、X/Twitter（ai-sweep + Zara Builder精选）、Hacker News、OpenRouter LLM 排行共 7 个信源。换设备时复制到工作区 `methods/` 目录即可使用。

从零开始，在新 Mac 上把 daily-news 完整跑起来。

---

## 前置条件

```bash
# 确认已安装
node --version        # >= 18
python3 --version     # >= 3.9
brew --version        # Homebrew

# 安装 opencli
npm install -g @jackwener/opencli

# 安装 Python 翻译库
pip3 install deep-translator

# 安装 GitHub CLI（用于推送 Pages）
brew install gh
gh auth login
```

---

## 第一步：克隆 skill

```bash
# Claude Code 用
git clone https://github.com/zkw15555506767-boop/claude-skills.git ~/.claude/skills

# AirJelly 用（手动复制）
cp -r ~/.claude/skills/daily-news \
  ~/Library/Application\ Support/AirJelly/skills/daily-news
```

---

## 第二步：创建工作区

```bash
mkdir -p ~/daily-news/{data,methods,output,logs,website/dist}
```

**复制配置文件：**

```bash
SKILL=~/.claude/skills/daily-news

# settings.yaml（可按需修改）
cp $SKILL/references/examples/settings.example.yaml ~/daily-news/settings.yaml

# profile.yaml（可按需修改）
cp $SKILL/references/examples/profile.example.yaml ~/daily-news/profile.yaml

# methods 目录
cp $SKILL/references/examples/methods/*.yaml ~/daily-news/methods/

# 网站构建脚本
cp $SKILL/references/website-template/build.py ~/daily-news/website/build.py
cp $SKILL/references/website-template/translate.py ~/daily-news/website/translate.py
```

---

## 第三步：初始化数据库

```bash
python3 ~/.claude/skills/daily-news/scripts/db.py init \
  --db ~/daily-news/data/news.db

python3 ~/.claude/skills/daily-news/scripts/db.py migrate \
  --db ~/daily-news/data/news.db \
  --sql ~/.claude/skills/daily-news/scripts/migrate_v2.sql

python3 ~/.claude/skills/daily-news/scripts/db.py migrate \
  --db ~/daily-news/data/news.db \
  --sql ~/.claude/skills/daily-news/scripts/migrate_v3.sql
```

---

## 第四步：配置 GitHub Pages 网站

```bash
# 创建 GitHub repo（替换为你自己的用户名）
gh repo create YOUR_USERNAME-AI-dailynews --public

# 初始化 dist 目录
cd ~/daily-news/website/dist
git init -b gh-pages
git remote add origin https://github.com/YOUR_USERNAME/YOUR_USERNAME-AI-dailynews.git

# 开启 GitHub Pages（在 GitHub 网页上手动设置，或用 API）
gh api --method POST \
  /repos/YOUR_USERNAME/YOUR_USERNAME-AI-dailynews/pages \
  -f source.branch=gh-pages -f source.path=/
```

---

## 第五步：设置定时任务

```bash
SKILL=~/.claude/skills/daily-news

# 复制 run_daily.sh
cp $SKILL/references/website-template/run_daily.sh ~/daily-news/run_daily.sh
chmod +x ~/daily-news/run_daily.sh

# 按需修改脚本里的 GitHub 用户名和 token
# vim ~/daily-news/run_daily.sh

# 复制 launchd plist（每天 11:00 / 14:00 / 22:00 自动运行）
cp $SKILL/references/website-template/com.zkevin.dailynews.plist \
  ~/Library/LaunchAgents/com.zkevin.dailynews.plist

# 注意：把 plist 里的用户名路径改成你自己的
# Label 和 plist 文件名可以改成 com.YOUR_NAME.dailynews

# 加载定时任务
launchctl load ~/Library/LaunchAgents/com.zkevin.dailynews.plist

# 验证
launchctl list | grep dailynews
```

---

## 第六步：手动跑一次验证

```bash
cd ~/daily-news
bash run_daily.sh

# 或者单独跑 build
python3 ~/daily-news/website/build.py --skip-live
```

---

## 目录结构说明

```
~/daily-news/
├── data/
│   ├── news.db              # SQLite 数据库（不入 git）
│   └── translate_cache.json # 翻译缓存（不入 git）
├── methods/                 # 信源配置（从 references/examples/methods/ 复制）
├── output/                  # Markdown 日报（可选）
├── logs/                    # 运行日志
├── website/
│   ├── build.py             # 网站构建脚本
│   ├── translate.py         # 翻译模块（带缓存）
│   └── dist/                # 生成的静态 HTML（推送到 GitHub Pages）
├── profile.yaml             # 用户画像（影响 AI 摘要风格）
├── settings.yaml            # 全局配置
└── run_daily.sh             # 每日运行入口
```

---

## 常见问题

**opencli 找不到？**
```bash
# 检查 node 路径
which node
# 如果在 /usr/local/bin 以外，修改 run_daily.sh 里的 PATH
```

**GitHub Pages 推送失败？**
```bash
# 刷新 token
gh auth token
# run_daily.sh 里的 token 通过 $(gh auth token) 动态获取，无需手动更新
```

**翻译报错？**
```bash
pip3 install --upgrade deep-translator
```
