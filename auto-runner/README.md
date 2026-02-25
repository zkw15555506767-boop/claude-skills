# Auto-Runner Skill v2.0

一键运行 GitHub 项目，自动安装并生成代码说明文档。

## 核心特性

### 🎯 智能安装

**自动判断最佳安装方式：**

| 优先级 | 安装方式 | 说明 |
|--------|----------|------|
| 1 | pip/npm/npx | Python/Node.js 包管理器 |
| 2 | docker | 容器化运行 |
| 3 | brew | Homebrew 安装 |
| 4 | binary | 二进制直接下载 |
| 5 | demo | 在线演示链接 |
| 6 | 整合包 | 完整克隆 + 一键启动脚本 |

### 📄 代码说明文档

运行后自动生成 `PROJECT_CODE_GUIDE.md`，包含：

- 项目结构树形图
- 每个代码文件的作用说明
- 主要函数和类列表
- 项目架构说明
- 如何修改和扩展项目

## 工作流程

```
输入 GitHub URL
    ↓
获取 README，分析简单安装方式
    ↓
┌─────────────────────────────────────┐
│ 有简单方式 → 直接安装运行           │
│ 无简单方式 → 创建本地整合包         │
└─────────────────────────────────────┘
    ↓
生成启动脚本 + 代码说明文档
```

## 使用方式

```text
请帮我运行这个项目: https://github.com/owner/repo
```

## 输出示例

### 有简单安装方式时

```
## ✅ pip 安装成功！

**包名**: some-package

### 运行方式

some-package
```

### 无简单方式时

```
## ✅ 项目已就绪！

**owner/repo**

### 📦 整合包位置
/tmp/auto-runner-bundles/repo/

### 📝 启动命令
./start.sh

### 📄 代码说明文档
PROJECT_CODE_GUIDE.md
```

## 支持的语言和安装方式

| 语言 | 简单安装 | 整合包安装 |
|------|----------|------------|
| Python | pip install | pip install -r requirements.txt |
| Node.js | npx / npm | npm install |
| Go | go install | go mod download && go run |
| Rust | cargo install | cargo run |
| Docker | docker run | docker-compose up |
| Homebrew | brew install | brew install |
| 二进制 | 直接下载 | - |
| 在线演示 | 浏览器打开 | - |

## 文件结构

```
auto-runner/
├── skill.json              # Skill 配置
├── main.py                 # 主入口 v2.0
├── core/
│   ├── github_parser.py    # GitHub 链接解析
│   ├── simple_runner.py    # 简单运行方式检测
│   ├── installer.py        # 简单安装器 (新增)
│   ├── bundler.py          # 整合包打包器 (新增)
│   └── code_analyzer.py    # 代码分析器 (新增)
└── utils/
    └── common.py           # 通用工具
```

## 代码说明文档示例

```markdown
# repo - 代码说明文档

## 📁 项目结构概览

```
repo/
├── src/
│   ├── main.py            class Main, def run()
│   ├── config.py          def load_config()
│   └── utils.py           class Utils
├── tests/
│   └── test_main.py       测试文件
└── requirements.txt
```

## 📄 核心文件说明

### 源代码文件

#### `src/main.py`
- **类型**: Python 源代码
- **说明**: 项目主入口文件，包含程序启动逻辑
- **类**: `Main`
- **函数**: `run()`, `init()`

## 🔧 如何修改项目

1. 在编辑器中打开项目
2. 修改对应的源代码文件
3. 保存文件后重新运行项目
```
