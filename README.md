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
| [skill-from-masters](./skill-from-masters | 基于领域专家方法论创建 AI skills |
| [github-to-skills](./github-to-skills) | 将 GitHub 仓库自动转换为 AI skills |
| [find-skills](./find-skills) | 发现和安装社区 skills |

### 学习与工作流

| Skill | 描述 |
|-------|------|
| [brainstorming](./brainstorming) | 头脑风暴 skill，在创意工作前探索用户意图、需求和设计 |
| [china-stock-analysis](./china-stock-analysis) | A股价值投资分析工具，提供股票筛选、个股深度分析、行业对比和估值计算 |
| [homework-assistant](./homework-assistant) | 智能作业助手，帮助分析课程作业、拆解任务、自动化完成编程和写作任务 |
| [humanizer](./humanizer) | 去除 AI 写作痕迹的工具，使文本更自然、更像人写的 |
| [continuous-learning](./continuous-learning) | 自动从会话中提取可复用模式并保存为 skills |
| [continuous-learning-v2](./continuous-learning-v2) | 基于本能的学习系统，观察会话创建原子本能 |
| [daily-news](./daily-news) | 每日资讯日报生成器（三阶段工作流） |
| [eval-harness](./eval-harness) | Claude Code 正式评估框架 |
| [iterative-retrieval](./iterative-retrieval) | 渐进式上下文检索模式，解决子代理上下文问题 |
| [planning-with-files](./planning-with-files) | 基于文件的规划 skill，实现 Manus 风格的任务规划 |
| [strategic-compact](./strategic-compact) | 建议在逻辑间隔手动上下文压缩 |
| [tushare-finance](./tushare-finance) | 获取中国金融市场数据，支持220+个Tushare Pro接口 |

### 工具与工具

| Skill | 描述 |
|-------|------|
| [pdf](./pdf) | PDF 处理工具包，提取文本/表格、创建、合并、拆分、处理表单 |
| [ui-ux-pro-max](./ui-ux-pro-max) | UI/UX 设计智能，50+ 风格、161 配色方案、57 字体搭配、161 产品类型 |

### 项目示例

| Skill | 描述 |
|-------|------|
| [project-guidelines-example](./project-guidelines-example) | 项目特定 skills 模板示例 |

---

## 使用方法

这些 skills 放在 `~/.claude/skills/` 目录下使用。更多信息请参考各 skill 的 `SKILL.md` 文件。
