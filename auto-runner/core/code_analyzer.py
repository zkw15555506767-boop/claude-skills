"""
代码分析器 - 生成项目代码说明文档

功能：
1. 分析项目文件结构
2. 识别代码文件类型和用途
3. 生成详细的代码说明文档（PROJECT_CODE_GUIDE.md）
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    name: str
    extension: str
    file_type: str  # source, test, config, docs, etc.
    description: str = ""
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class CodeAnalyzer:
    """代码分析器"""

    # 文件类型映射
    FILE_TYPES = {
        # 源代码文件
        ".py": {"type": "python", "category": "source", "name": "Python 源代码"},
        ".js": {"type": "javascript", "category": "source", "name": "JavaScript 源代码"},
        ".ts": {"type": "typescript", "category": "source", "name": "TypeScript 源代码"},
        ".jsx": {"type": "react", "category": "source", "name": "React 组件"},
        ".tsx": {"type": "react", "category": "source", "name": "React TypeScript 组件"},
        ".go": {"type": "go", "category": "source", "name": "Go 源代码"},
        ".rs": {"type": "rust", "category": "source", "name": "Rust 源代码"},
        ".java": {"type": "java", "category": "source", "name": "Java 源代码"},
        ".c": {"type": "c", "category": "source", "name": "C 源代码"},
        ".cpp": {"type": "cpp", "category": "source", "name": "C++ 源代码"},
        ".cs": {"type": "csharp", "category": "source", "name": "C# 源代码"},
        ".php": {"type": "php", "category": "source", "name": "PHP 源代码"},
        # 测试文件
        "_test.py": {"type": "python", "category": "test", "name": "Python 测试"},
        ".test.js": {"type": "javascript", "category": "test", "name": "JavaScript 测试"},
        ".spec.js": {"type": "javascript", "category": "test", "name": "JavaScript 测试"},
        ".test.ts": {"type": "typescript", "category": "test", "name": "TypeScript 测试"},
        ".spec.ts": {"type": "typescript", "category": "test", "name": "TypeScript 测试"},
        "_test.go": {"type": "go", "category": "test", "name": "Go 测试"},
        # 配置文件
        ".json": {"type": "config", "category": "config", "name": "JSON 配置"},
        ".yaml": {"type": "config", "category": "config", "name": "YAML 配置"},
        ".yml": {"type": "config", "category": "config", "name": "YAML 配置"},
        ".toml": {"type": "config", "category": "config", "name": "TOML 配置"},
        ".ini": {"type": "config", "category": "config", "name": "INI 配置"},
        ".env": {"type": "config", "category": "config", "name": "环境变量"},
        # 标记文件
        "Dockerfile": {"type": "docker", "category": "config", "name": "Docker 配置"},
        ".dockerignore": {"type": "docker", "category": "config", "name": "Docker 忽略配置"},
        ".gitignore": {"type": "git", "category": "config", "name": "Git 忽略配置"},
        # 文档
        ".md": {"type": "docs", "category": "docs", "name": "Markdown 文档"},
        ".txt": {"type": "text", "category": "docs", "name": "文本文件"},
        # 其他
        ".sh": {"type": "script", "category": "script", "name": "Shell 脚本"},
        ".bat": {"type": "script", "category": "script", "name": "Batch 脚本"},
    }

    # 特殊目录说明
    DIRECTORY_DESC = {
        "src": "源代码目录，包含项目的主要代码",
        "lib": "库目录，包含可复用的模块",
        "utils": "工具函数目录，包含辅助函数",
        "helpers": "帮助函数目录",
        "tests": "测试目录，包含单元测试和集成测试",
        "test": "测试目录",
        "__tests__": "测试目录（Jest 风格）",
        "docs": "文档目录，包含项目文档",
        "documentation": "文档目录",
        "examples": "示例代码目录",
        "example": "示例代码目录",
        "scripts": "脚本目录，包含构建和部署脚本",
        "tools": "工具目录",
        "bin": "可执行文件目录",
        "config": "配置目录",
        "configs": "配置目录",
        "resources": "资源目录，包含静态资源",
        "assets": "静态资源目录（图片、字体等）",
        "public": "公开资源目录（前端项目）",
        "static": "静态文件目录",
        "models": "数据模型目录",
        "services": "服务层目录",
        "controllers": "控制器目录（MVC 模式）",
        "views": "视图目录（MVC 模式）",
        "routes": "路由目录",
        "api": "API 目录",
        "middleware": "中间件目录",
        "hooks": "React Hooks 目录",
        "components": "组件目录（UI 组件）",
        "pages": "页面目录（前端路由页面）",
        "layouts": "布局组件目录",
        "styles": "样式目录",
        "css": "CSS 样式目录",
        "scss": "SCSS 样式目录",
        "types": "类型定义目录（TypeScript）",
        "interfaces": "接口定义目录",
    }

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.files: List[FileInfo] = []
        self.structure: Dict[str, List[str]] = {}

    async def generate_guide(self, api_info: Optional[dict] = None) -> str:
        """生成代码说明文档"""
        # 分析项目
        await self.analyze()

        # 生成文档
        guide_path = os.path.join(self.project_path, "PROJECT_CODE_GUIDE.md")
        content = self._generate_content(api_info)

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(content)

        return guide_path

    async def analyze(self):
        """分析项目文件"""
        self.files = []
        self.structure = {}

        # 遍历项目目录
        for root, dirs, files in os.walk(self.project_path):
            # 跳过隐藏目录和常见忽略目录
            dirs[:] = [d for d in dirs if not d.startswith(".")
                       and d not in ["node_modules", "__pycache__", "venv", ".venv",
                                     "dist", "build", ".git", "coverage"]]

            # 计算相对路径
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == ".":
                rel_path = "/"

            # 记录目录结构
            if rel_path not in self.structure:
                self.structure[rel_path] = []
            self.structure[rel_path].extend(dirs)

            # 分析每个文件
            for file in files:
                file_path = os.path.join(root, file)
                file_info = await self._analyze_file(file_path, rel_path)
                if file_info:
                    self.files.append(file_info)

    async def _analyze_file(self, file_path: str, rel_dir: str) -> Optional[FileInfo]:
        """分析单个文件"""
        name = os.path.basename(file_path)
        ext = os.path.splitext(name)[1]
        full_ext = os.path.splitext(name)[0] if name.startswith("_") or name.endswith("_test") else ext

        # 获取文件类型信息
        file_type_info = self.FILE_TYPES.get(
            ext,
            self.FILE_TYPES.get(name, {"type": "unknown", "category": "other", "name": "其他文件"})
        )

        # 对于 Python 文件，进行 AST 分析
        functions = []
        classes = []
        imports = []

        if ext == ".py":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module.split(".")[0])
            except:
                pass

        # 生成描述
        description = self._generate_file_description(name, ext, rel_dir, functions, classes)

        return FileInfo(
            path=file_path,
            name=name,
            extension=ext,
            file_type=file_type_info["name"],
            description=description,
            functions=functions,
            classes=classes,
            imports=list(set(imports))[:5]  # 最多5个导入
        )

    def _generate_file_description(
        self, name: str, ext: str, rel_dir: str, functions: List[str], classes: List[str]
    ) -> str:
        """生成文件描述"""
        # 特殊文件
        if name == "main.py":
            return "项目主入口文件，通常包含程序启动逻辑"
        elif name == "app.py":
            return "Flask/FastAPI 应用主文件"
        elif name == "server.py":
            return "服务器启动文件"
        elif name == "index.js":
            return "Node.js 入口文件"
        elif name == "index.html":
            return "HTML 首页"
        elif name == "README.md":
            return "项目说明文档"
        elif name == "requirements.txt":
            return "Python 依赖列表"
        elif name == "package.json":
            return "Node.js 项目配置和依赖管理"
        elif name == "Dockerfile":
            return "Docker 镜像构建配置"
        elif name == "docker-compose.yml":
            return "Docker Compose 多容器编排配置"
        elif name == ".env.example":
            return "环境变量示例配置"

        # 目录相关的描述
        dir_name = os.path.basename(rel_dir)
        if dir_name in self.DIRECTORY_DESC:
            return self.DIRECTORY_DESC[dir_name]

        # 测试文件
        if "_test.py" in name or ".test." in name or ".spec." in name:
            test_type = "单元测试" if "unit" in name.lower() else "测试"
            return f"{test_type}文件，包含自动化测试用例"

        # 配置类
        if ext in [".json", ".yaml", ".yml", ".toml"]:
            return f"{file_type_info['name']}，项目配置信息"

        # 脚本文件
        if ext == ".sh":
            return "Shell 脚本，用于自动化任务"

        # 源代码
        if file_type_info["category"] == "source":
            parts = []
            if classes:
                parts.append(f"包含类: {', '.join(classes[:2])}")
            if functions:
                parts.append(f"包含函数: {', '.join(functions[:3])}")
            if parts:
                return "源代码文件，" + "，".join(parts)
            return "项目源代码文件"

        return file_type_info["name"]

    def _generate_content(self, api_info: Optional[dict]) -> str:
        """生成文档内容"""
        name = api_info.get("name", os.path.basename(self.project_path)) if api_info else os.path.basename(self.project_path)
        description = api_info.get("description", "") if api_info else ""

        lines = []
        lines.append(f"# {name} - 代码说明文档\n")
        lines.append(f">{description}\n" if description else "\n")
        lines.append("---\n")
        lines.append("## 📁 项目结构概览\n")
        lines.append("```\n")

        # 生成树形结构
        lines.append(self._generate_tree_structure())

        lines.append("```\n")
        lines.append("\n## 📄 核心文件说明\n")

        # 按类型分组
        source_files = [f for f in self.files if f.file_type in self._get_source_types()]
        config_files = [f for f in self.files if f.file_type in self._get_config_types()]
        test_files = [f for f in self.files if f.file_type in self._get_test_types()]
        other_files = [f for f in self.files if f not in source_files + config_files + test_files]

        # 源代码文件
        if source_files:
            lines.append("### 源代码文件\n")
            for f in sorted(source_files, key=lambda x: x.path):
                rel_path = os.path.relpath(f.path, self.project_path)
                lines.append(f"#### `{rel_path}`\n")
                lines.append(f"- **类型**: {f.file_type}\n")
                if f.description:
                    lines.append(f"- **说明**: {f.description}\n")
                if f.classes:
                    lines.append(f"- **类**: `{', '.join(f.classes)}`\n")
                if f.functions:
                    lines.append(f"- **函数**: `{', '.join(f.functions[:5])}`\n")
                lines.append("\n")

        # 配置文件
        if config_files:
            lines.append("### 配置文件\n")
            for f in sorted(config_files, key=lambda x: x.path):
                rel_path = os.path.relpath(f.path, self.project_path)
                lines.append(f"#### `{rel_path}`\n")
                lines.append(f"- **说明**: {f.description}\n")
                lines.append("\n")

        # 测试文件
        if test_files:
            lines.append("### 测试文件\n")
            for f in sorted(test_files, key=lambda x: x.path):
                rel_path = os.path.relpath(f.path, self.project_path)
                lines.append(f"#### `{rel_path}`\n")
                lines.append(f"- **说明**: {f.description}\n")
                lines.append("\n")

        lines.append("\n## 🏗️ 项目架构说明\n")
        lines.append(self._generate_architecture_guide())

        lines.append("\n## 🔧 如何修改项目\n")
        lines.append(self._generate_modification_guide())

        lines.append("\n---\n")
        lines.append(f"*本文档由 Auto-Runner 自动生成*\n")

        return "\n".join(lines)

    def _generate_tree_structure(self, prefix: str = "", is_last: bool = True) -> str:
        """生成树形结构"""
        lines = []
        items = []

        # 获取顶层文件和目录
        root_files = []
        root_dirs = []

        for f in self.files:
            rel_path = os.path.relpath(f.path, self.project_path)
            if "/" not in rel_path:
                if f.extension == "" and not any(f.name.endswith("." + e) for e in self.FILE_TYPES):
                    root_dirs.append(f)
                else:
                    root_files.append(f)

        # 合并目录
        all_root = root_dirs + root_files

        for i, item in enumerate(all_root):
            is_last_item = (i == len(all_root) - 1)
            connector = "└── " if is_last_item else "├── "

            if hasattr(item, 'extension'):  # FileInfo
                lines.append(f"{prefix}{connector}{item.name}")
            else:  # Directory
                lines.append(f"{prefix}{connector}{item}/")

            if hasattr(item, 'extension') and item.extension == ".py":
                # 递归显示 Python 内部结构
                if item.classes or item.functions:
                    new_prefix = prefix + ("    " if is_last_item else "│   ")
                    for j, cls in enumerate(item.classes[:2]):
                        cls_last = (j == len(item.classes[:2]) - 1 and not item.functions)
                        cls_conn = "└── " if cls_last else "├── "
                        lines.append(f"{new_prefix}{cls_conn}class {cls}")

                    for j, func in enumerate(item.functions[:3]):
                        func_last = (j == len(item.functions[:3]) - 1)
                        func_conn = "└── " if func_last else "├── "
                        lines.append(f"{new_prefix}{func_conn}def {func}()")

        return "\n".join(lines)

    def _get_source_types(self) -> List[str]:
        return ["Python 源代码", "JavaScript 源代码", "TypeScript 源代码",
                "React 组件", "React TypeScript 组件", "Go 源代码",
                "Rust 源代码", "Java 源代码", "C 源代码", "C++ 源代码",
                "C# 源代码", "PHP 源代码"]

    def _get_config_types(self) -> List[str]:
        return ["JSON 配置", "YAML 配置", "TOML 配置", "INI 配置",
                "环境变量", "Docker 配置", "Git 忽略配置"]

    def _get_test_types(self) -> List[str]:
        return ["Python 测试", "JavaScript 测试", "TypeScript 测试", "Go 测试"]

    def _generate_architecture_guide(self) -> str:
        """生成架构说明"""
        guide = []

        # 检测项目类型
        has_package_json = any("package.json" in f.name for f in self.files)
        has_requirements = any("requirements.txt" in f.name for f in self.files)
        has_go_mod = any("go.mod" in f.name for f in self.files)
        has_cargo = any("Cargo.toml" in f.name for f in self.files)

        if has_package_json:
            guide.append("### 前端/Node.js 项目架构\n")
            guide.append("- **src/**: 源代码目录")
            guide.append("  - **components/**: React/Vue 组件")
            guide.append("  - **pages/**: 页面组件")
            guide.append("  - **utils/**: 工具函数")
            guide.append("  - **api/**: API 接口封装")
            guide.append("- **public/**: 静态资源")
            guide.append("- **node_modules/**: 依赖包（自动生成）\n")
        elif has_requirements:
            guide.append("### Python 项目架构\n")
            guide.append("- **src/**: 源代码目录（如有）")
            guide.append("- **tests/**: 测试目录")
            guide.append("- **main.py/app.py**: 程序入口")
            guide.append("- **requirements.txt**: 依赖列表\n")
        elif has_go_mod:
            guide.append("### Go 项目架构\n")
            guide.append("- **main.go**: 主程序入口")
            guide.append("- **internal/**: 内部包（不可被外部导入）")
            guide.append("- **pkg/**: 公共包（可被外部导入）")
            guide.append("- **cmd/**: 命令行工具入口\n")
        elif has_cargo:
            guide.append("### Rust 项目架构\n")
            guide.append("- **src/**: 源代码")
            guide.append("  - **main.rs**: 二进制 crate 入口")
            guide.append("  - **lib.rs**: 库 crate 入口")
            guide.append("- **tests/**: 集成测试")
            guide.append("- **examples/**: 示例代码\n")

        return "\n".join(guide)

    def _generate_modification_guide(self) -> str:
        """生成修改指南"""
        guide = []
        guide.append("### 修改代码\n")
        guide.append("1. 在编辑器中打开项目")
        guide.append("2. 修改对应的源代码文件")
        guide.append("3. 保存文件后重新运行项目\n")

        guide.append("### 添加新功能\n")
        guide.append("1. 在对应目录创建新文件")
        guide.append("2. 在入口文件或调用处导入新模块")
        guide.append("3. 测试新功能\n")

        guide.append("### 配置修改\n")
        guide.append("1. 复制 `.env.example` 为 `.env`")
        guide.append("2. 修改环境变量值")
        guide.append("3. 重启项目使配置生效\n")

        return "\n".join(guide)
