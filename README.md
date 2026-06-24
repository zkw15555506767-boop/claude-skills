# Claude Code Skills Collection

本仓库包含 Claude Code 的自定义 skills 集合，用于扩展 Claude 的能力。

## 目录

### 开发相关

| Skill | 描述 |
|-------|------|
| [auto-runner](./auto-runner) | 一键运行 GitHub 项目，自动安装并生成代码说明文档 |
| [backend-patterns](./backend-patterns) | 后端架构模式、API 设计、数据库优化（Node.js/Express/Next.js） |
| [chrome-automation](./chrome-automation) | 通过 CDP 控制 Google Chrome 浏览器，实现自动化操作 |
| [clickhouse-io](./clickhouse-io) | ClickHouse 数据库模式、查询优化、数据工程最佳实践 |
| [coding-standards](./coding-standards) | 通用编码标准、最佳实践（TypeScript/JavaScript/React/Node.js） |
| [frontend-design](./frontend-design) | 创建高质量、独特的前端界面，避免通用 AI 美学 |
| [frontend-patterns](./frontend-patterns) | 前端开发模式（React、Next.js、状态管理、性能优化） |
| [frontend-slides](./frontend-slides) | 从零创建或将 PPT 转换为动画丰富的 HTML 演示文稿，无需外部依赖 |
| [golang-patterns](./golang-patterns) | Go 语言惯用模式、最佳实践 |
| [golang-testing](./golang-testing) | Go 测试模式（表驱动测试、基准测试、模糊测试） |
| [postgres-patterns](./postgres-patterns) | PostgreSQL 数据库模式、查询优化、索引设计、安全 |
| [security-review](./security-review) | 安全审查，检查认证、用户输入、密钥管理等问题 |
| [tdd-workflow](./tdd-workflow) | 测试驱动开发工作流，强制 80%+ 覆盖率 |
| [verification-loop](./verification-loop) | 代码验证系统，构建/类型检查/测试验证 |

### Skills 管理

| Skill | 描述 |
|-------|------|
| [skill-creator](./skill-creator) | 创建有效 skills 的指南 |
| [skill-manager](./skill-manager) | GitHub-based skills 的生命周期管理器，检查更新和升级 |
| [skill-evolution-manager](./skill-evolution-manager) | 对话结束时根据反馈优化迭代 Skills |
| [skill-from-masters](./skill-from-masters) | 基于领域专家方法论创建 AI skills |
| [github-to-skills](./github-to-skills) | 将 GitHub 仓库自动转换为 AI skills |
| [find-skills](./find-skills) | 发现和安装社区 skills |
| [uploadgithub](./uploadgithub) | 上传文件或目录到 GitHub，支持自动初始化 git 和创建仓库 |

### AI Agent 与工具

| Skill | 描述 |
|-------|------|
| [agent-reach](./agent-reach) | 为 AI agent 提供互联网浏览能力，路由到合适的信息源 |
| [web-access](./web-access) | 联网操作：搜索、网页抓取、浏览器自动化，支持动态渲染页面 |
| [claude-to-im](./claude-to-im) | 将 Claude Code 接入 IM 平台（Telegram、Discord、飞书） |
| [defuddle](./defuddle) | 用 Defuddle CLI 从网页提取干净的 Markdown，去除导航和广告 |
| [brainstorming](./brainstorming) | 创意工作前必用：探索用户意图、需求和设计，再进入实现 |
| [planning-with-files](./planning-with-files) | 基于文件的 Manus 式任务规划，适合多步骤复杂项目 |
| [follow-builders](./follow-builders) | 追踪 AI builder 社区动态，抓取推文/博客/播客生成摘要 |

### 学习与工作流

| Skill | 描述 |
|-------|------|
| [china-stock-analysis](./china-stock-analysis) | A 股价值投资分析工具，股票筛选、个股深度分析、估值计算 |
| [homework-assistant](./homework-assistant) | 智能作业助手，分析课程作业、拆解任务、自动化完成编程和写作任务 |
| [humanizer](./humanizer) | 去除 AI 写作痕迹，使文本更自然 |
| [continuous-learning](./continuous-learning) | 自动从会话中提取可复用模式并保存为 skills |
| [continuous-learning-v2](./continuous-learning-v2) | 基于本能的学习系统，观察会话创建原子本能 |
| [daily-news](./daily-news) | 每日资讯日报生成器（三阶段工作流） |
| [eval-harness](./eval-harness) | Claude Code 正式评估框架，实现 eval 驱动开发 |
| [iterative-retrieval](./iterative-retrieval) | 渐进式上下文检索模式，解决子代理上下文问题 |
| [strategic-compact](./strategic-compact) | 建议在逻辑间隔手动压缩上下文 |
| [tushare-finance](./tushare-finance) | 获取中国金融市场数据，支持 220+ 个 Tushare Pro 接口 |

### 工具集

| Skill | 描述 |
|-------|------|
| [pdf](./pdf) | PDF 处理工具包，提取文本/表格、创建、合并、拆分、处理表单 |
| [ui-ux-pro-max](./ui-ux-pro-max) | UI/UX 设计智能，50 种风格、21 种配色方案、50 种字体搭配 |
| [json-canvas](./json-canvas) | 创建和编辑 JSON Canvas 文件，支持节点、边、分组和连接 |

### Obsidian

| Skill | 描述 |
|-------|------|
| [obsidian-cli](./obsidian-cli) | 通过 CLI 与 Obsidian vault 交互，管理笔记、任务、搜索、插件开发 |
| [obsidian-markdown](./obsidian-markdown) | 创建和编辑 Obsidian Flavored Markdown（wikilinks、callouts、properties 等） |
| [obsidian-bases](./obsidian-bases) | 创建和编辑 Obsidian Bases 文件，构建数据库视图、过滤器和公式 |

### 飞书/Lark

| Skill | 描述 |
|-------|------|
| [lark-shared](./lark-shared) | 飞书 CLI 共享基础：应用配置、认证登录、身份切换、权限管理 |
| [lark-im](./lark-im) | 飞书即时通讯：收发消息、搜索聊天记录、管理群聊 |
| [lark-doc](./lark-doc) | 飞书云文档：创建/编辑文档、上传下载文件、搜索云空间 |
| [lark-sheets](./lark-sheets) | 飞书电子表格：创建表格、读写数据、追加行、导出文件 |
| [lark-base](./lark-base) | 飞书多维表格：建表、字段管理、记录读写、视图配置 |
| [lark-drive](./lark-drive) | 飞书云空间：上传下载文件、管理目录、权限、评论 |
| [lark-calendar](./lark-calendar) | 飞书日历：查看/创建日程、管理参会人、查询忙闲状态 |
| [lark-task](./lark-task) | 飞书任务：创建待办、跟踪进度、拆分子任务、分配协作成员 |
| [lark-wiki](./lark-wiki) | 飞书知识库：管理知识空间、节点层级、文档组织 |
| [lark-mail](./lark-mail) | 飞书邮箱：起草、发送、回复、转发邮件，管理附件和标签 |
| [lark-contact](./lark-contact) | 飞书通讯录：查询组织架构、搜索员工、获取 open_id |
| [lark-minutes](./lark-minutes) | 飞书妙记：获取妙记基础信息和 AI 产物（总结、待办、章节） |
| [lark-vc](./lark-vc) | 飞书视频会议：查询会议记录、获取会议纪要和逐字稿 |
| [lark-event](./lark-event) | 飞书事件订阅：WebSocket 长连接实时监听飞书事件 |
| [lark-whiteboard](./lark-whiteboard) | 飞书白板操作 |
| [lark-openapi-explorer](./lark-openapi-explorer) | 探索飞书原生 OpenAPI，满足 lark-cli 未封装的接口需求 |
| [lark-skill-maker](./lark-skill-maker) | 创建 lark-cli 自定义 Skill，封装飞书 API 操作 |
| [lark-workflow-meeting-summary](./lark-workflow-meeting-summary) | 汇总指定时间范围内的会议纪要，生成结构化报告 |
| [lark-workflow-standup-report](./lark-workflow-standup-report) | 生成指定日期的日程与未完成任务摘要 |

### 项目示例

| Skill | 描述 |
|-------|------|
| [project-guidelines-example](./project-guidelines-example) | 项目特定 skills 模板示例 |

---

## 使用方法

这些 skills 放在 `~/.claude/skills/` 目录下使用。更多信息请参考各 skill 的 `SKILL.md` 文件。
