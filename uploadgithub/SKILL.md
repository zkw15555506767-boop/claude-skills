---
name: uploadgithub
description: 上传文件或目录到 GitHub，支持自动初始化 git 和创建仓库。如果是 skill 目录，会自动更新 README 文件。
version: 1.0.0
author: Claude
tags:
  - github
  - git
  - upload
  - deployment
---

# Upload to GitHub

将本地文件或目录上传到 GitHub，支持自动初始化 git、创建仓库和推送代码。

## 触发方式

- `/uploadgithub` - 上传当前目录
- `/uploadgithub <路径>` - 上传指定路径
- "帮我上传到 GitHub"
- "上传这个项目到 GitHub"

## 工作流程

### 1. 检查登录状态

首先检查 gh CLI 是否已登录：

```bash
gh auth status
```

如果未登录，引导用户运行：

```bash
gh auth login
```

并等待用户完成浏览器验证。

### 信息

向用户询问以下信息：
2. 获取上传- **仓库名称**：默认使用目录名
- **公开/私有**：默认公开
- **上传路径**：用户指定的本地目录

### 3. 创建仓库并上传

根据不同场景选择工作流：

#### 场景 A：目录已是 git 仓库

```bash
# 直接创建远程仓库并推送
gh repo create <repo-name> --public --source=<path> --push
```

#### 场景 B：目录不是 git 仓库

```bash
cd <path>

# 初始化 git
git init

# 创建 .gitignore（如果不存在）
cat > .gitignore << 'EOF'
.DS_Store
*.swp
*.swo
*~
EOF

# 添加所有文件
git add -A

# 提交
git commit -m "Initial commit"

# 创建远程仓库并推送
gh repo create <repo-name> --public --source=. --push
```

### 4. 自动更新 README（仅限 Skill）

如果上传的目录包含 `SKILL.md` 文件，视为 skill 目录，需要自动更新仓库的 README：

#### 4.1 读取 SKILL.md 获取描述

```bash
head -20 SKILL.md
```

提取 description 字段或前几行描述。

#### 4.2 更新 README

创建或更新仓库根目录的 README.md：

```markdown
# <仓库名>

<从 SKILL.md 提取的描述>

## 目录结构

<!-- 可选：列出主要文件 -->

## 使用方法

<!-- 可选：使用说明 -->
```

#### 4.3 提交并推送 README 更新

```bash
git add README.md
git commit -m "Add README"
git push
```

## 输出信息

完成后告诉用户：
- 仓库地址：`https://github.com/<username>/<repo-name>`
- 上传的文件数量

## 注意事项

- 如果目录已包含 .git 目录，跳过初始化步骤
- 如果远程仓库已存在，使用 `gh repo create --source=. --push` 会失败，此时提示用户
- 确保在推送前添加有意义的 commit message
