{
  "name": "auto-runner",
  "description": "一键运行 GitHub 项目，自动安装并生成代码说明文档",
  "version": "2.0.0",
  "author": "Claude",
  "instructions": "## Auto-Runner Skill - 一键运行 GitHub 项目\n\n### 工作流程\n\n1. **获取项目信息**\n   - 通过 GitHub API 获取项目 README 和基本信息\n   - 解析 README 提取安装/运行方式\n\n2. **智能安装**\n   - 优先使用简单安装方式（pip/npx/docker/brew/二进制/在线演示）\n   - 如果没有简单方式，创建本地整合包（克隆 + 依赖 + 启动脚本）\n\n3. **一键启动**\n   - 生成启动脚本\n   - 自动运行项目\n\n4. **生成文档**\n   - 代码文件说明文档（每个文件的作用，便于理解和修改）\n   - 使用说明文档\n\n### 输入格式\n\n```\n请帮我运行这个项目: https://github.com/owner/repo\n```\n\n或直接提供链接：\n```\nhttps://github.com/owner/repo\n```\n\n### 输出内容\n\n- 项目概览和简单安装方式（如果有）\n- 如果需要完整安装，会生成整合包和启动脚本\n- 代码文件说明文档（帮助你理解每个代码文件的作用）\n\n### 支持的语言和安装方式\n\n| 类型 | 安装方式 |\n|------|----------|\n| Python | pip install / pipx / 源码安装 |\n| Node.js | npm / npx / pnpm |\n| Go | go install / go run |\n| Rust | cargo install |\n| Docker | docker run / docker-compose |\n| Homebrew | brew install |\n| 二进制 | 直接下载运行 |\n| 在线演示 | 浏览器打开即可 |\n\n### 代码说明文档\n\n运行后会生成 `PROJECT_CODE_GUIDE.md` 文件，包含：\n- 项目整体架构说明\n- 每个代码文件的作用和功能\n- 如何修改和扩展项目的指南",
  "tools": [
    "Bash",
    "Read",
    "Write",
    "Edit",
    "WebFetch",
    "Grep",
    "Glob"
  ],
  "requirements": {
    "python": ">=3.10"
  },
  "tags": [
    "github",
    "automation",
    "installation",
    "documentation",
    "development"
  ]
}
