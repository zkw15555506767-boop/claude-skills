"""
项目整合包打包器 - 为没有简单安装方式的项目创建本地整合包

功能：
1. 克隆项目
2. 安装依赖
3. 生成一键启动脚本
4. 生成使用说明
"""

import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from utils.common import run_command, log_step, log_info


class ProjectBundler:
    """项目整合包打包器"""

    def __init__(self, bundle_dir: str = "/tmp/auto-runner-bundles"):
        self.bundle_dir = bundle_dir
        os.makedirs(bundle_dir, exist_ok=True)

    async def create_bundle(
        self, repo_info, api_info: Optional[dict] = None
    ) -> tuple[str, bool]:
        """
        创建项目整合包

        Args:
            repo_info: GitHubRepoInfo 对象或包含 owner/repo 的字典
            api_info: 可选的项目 API 信息

        Returns:
            (bundle_path, success)
        """
        # 获取 repo 名称
        if hasattr(repo_info, 'repo'):
            owner = repo_info.owner
            repo_name = repo_info.repo
        else:
            owner = repo_info.get('owner', '')
            repo_name = repo_info.get('repo', '')

        bundle_path = os.path.join(self.bundle_dir, repo_name)

        # 如果已存在，先清理
        if os.path.exists(bundle_path):
            shutil.rmtree(bundle_path)

        log_step("CLONE", f"克隆 {owner}/{repo_name}")

        # 克隆项目
        clone_url = f"https://github.com/{owner}/{repo_name}.git"
        success, output = await run_command(
            f"git clone {clone_url} {bundle_path}",
            timeout=300
        )

        if not success:
            log_step("ERROR", f"克隆失败: {output[:200]}")
            return bundle_path, False

        log_step("SUCCESS", f"克隆到 {bundle_path}")

        # 克隆成功后，创建整合包结构
        await self._setup_bundle(bundle_path, owner, repo_name, api_info)

        return bundle_path, True

    async def _setup_bundle(
        self, bundle_path: str, owner: str, repo_name: str, api_info: Optional[dict]
    ):
        """设置整合包结构"""
        # 1. 检测项目类型
        language = await self._detect_language(bundle_path)

        # 2. 生成启动脚本
        await self._generate_launcher(bundle_path, language, owner, repo_name)

        # 3. 生成使用说明
        await self._generate_readme(bundle_path, owner, repo_name, api_info)

        # 4. 生成 .env.example（如果需要）
        await self._generate_env_example(bundle_path)

    async def _detect_language(self, project_path: str) -> str:
        """检测项目语言"""
        # 检测常见的配置文件
        config_files = {
            "Python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "Node.js": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
            "Go": ["go.mod", "go.sum"],
            "Rust": ["Cargo.toml", "Cargo.lock"],
            "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "PHP": ["composer.json", "composer.lock"],
            "C#": ["*.csproj", "*.sln"],
        }

        for lang, files in config_files.items():
            for f in files:
                if "*" in f:
                    import glob
                    if glob.glob(os.path.join(project_path, f.replace("*", ""))):
                        return lang
                elif os.path.exists(os.path.join(project_path, f)):
                    return lang

        # 默认检测文件扩展名
        import glob
        extensions = {
            "Python": ["*.py"],
            "JavaScript": ["*.js"],
            "TypeScript": ["*.ts"],
            "Go": ["*.go"],
            "Rust": ["*.rs"],
        }

        for lang, patterns in extensions.items():
            for p in patterns:
                if glob.glob(os.path.join(project_path, p)):
                    return lang

        return "Unknown"

    async def _generate_launcher(
        self, bundle_path: str, language: str, owner: str, repo_name: str
    ):
        """生成启动脚本"""
        launcher_path = os.path.join(bundle_path, "start.sh")
        launcher_content = f'''#!/bin/bash

# Auto-Runner 启动脚本
# 项目: {owner}/{repo_name}
# 生成时间: {self._get_timestamp()}

set -e

echo "🚀 启动 {repo_name}..."

# 颜色定义
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# 检测操作系统
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="macos";;
    CYGWIN*|MINGW*|MSYS*) PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

echo -e "${GREEN}检测到平台: $PLATFORM${NC}"

'''

        # 根据语言添加特定逻辑
        if language == "Python":
            launcher_content += '''
# Python 项目
echo "📦 安装 Python 依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
    pip install -e .
elif [ -f "setup.py" ]; then
    pip install -e .
fi

echo "🐍 启动 Python 项目..."
# 查找主入口文件
if [ -f "main.py" ]; then
    python main.py
elif [ -f "app.py" ]; then
    python app.py
else
    python -m $(ls *.py | head -1 | cut -d. -f1)
fi
'''
        elif language == "Node.js":
            launcher_content += '''
# Node.js 项目
echo "📦 安装 Node.js 依赖..."
if [ -f "package.json" ]; then
    npm install 2>/dev/null || yarn install 2>/dev/null || pnpm install 2>/dev/null
fi

echo "📦 启动 Node.js 项目..."
if grep -q '"start"' package.json 2>/dev/null; then
    npm start
elif grep -q '"dev"' package.json 2>/dev/null; then
    npm run dev
else
    node index.js 2>/dev/null || node app.js 2>/dev/null || node server.js
fi
'''
        elif language == "Go":
            launcher_content += '''
# Go 项目
echo "📦 下载 Go 依赖..."
go mod download 2>/dev/null || go get -d ./...

echo "🏃 运行 Go 项目..."
if [ -f "main.go" ]; then
    go run main.go
else
    go run .
fi
'''
        elif language == "Rust":
            launcher_content += '''
# Rust 项目
echo "📦 编译 Rust 项目..."
cargo build --release 2>/dev/null

echo "🏃 运行 Rust 项目..."
cargo run
'''
        else:
            launcher_content += '''
# 通用启动方式
echo "📄 检测项目文件..."
if [ -f "Makefile" ]; then
    make
elif [ -f "CMakeLists.txt" ]; then
    mkdir -p build && cd build && cmake .. && make
else
    echo "请查看项目 README 获取启动方式"
    ls -la
fi
'''

        launcher_content += f'''

echo -e "${{GREEN}}✅ 项目启动完成!{NC}"
'''

        with open(launcher_path, "w") as f:
            f.write(launcher_content)

        os.chmod(launcher_path, 0o755)
        log_step("LAUNCHER", f"生成启动脚本: start.sh")

    async def _generate_readme(
        self, bundle_path: str, owner: str, repo_name: str, api_info: Optional[dict]
    ):
        """生成使用说明"""
        readme_path = os.path.join(bundle_path, "AUTO_RUNNER_README.md")
        description = api_info.get("description", "暂无描述") if api_info else ""

        content = f'''# {repo_name}

{description}

---

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

```bash
chmod +x start.sh
./start.sh
```

### 方式二：手动运行

```bash
# 进入项目目录
cd {bundle_path}

# 安装依赖
# （请查看项目 README 获取具体命令）

# 运行项目
# （请查看项目 README 获取具体命令）
```

---

## 📁 项目结构

```
{repo_name}/
├── start.sh              # 一键启动脚本（Auto-Runner 生成）
├── AUTO_RUNNER_README.md # 本说明文件
├── README.md             # 原始项目说明
├── src/                  # 源代码目录
├── tests/                # 测试目录
└── ...                   # 其他项目文件
```

---

## 📖 更多信息

- 原始 README: [README.md](README.md)
- 项目主页: https://github.com/{owner}/{repo_name}

---

*本整合包由 Auto-Runner 自动生成*
'''

        with open(readme_path, "w") as f:
            f.write(content)

        log_step("README", f"生成说明文件: AUTO_RUNNER_README.md")

    async def _generate_env_example(self, bundle_path: str):
        """生成环境变量示例"""
        env_example_path = os.path.join(bundle_path, ".env.example")

        # 检查项目是否需要环境变量
        env_files = [".env.example", ".env.template", ".env.sample"]
        if any(os.path.exists(os.path.join(bundle_path, f)) for f in env_files):
            return

        # 生成通用示例
        content = '''# 环境变量配置示例
# 复制本文件为 .env 并填写实际值

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API 密钥
API_KEY=your_api_key_here

# 其他配置
DEBUG=false
PORT=8080
'''

        with open(env_example_path, "w") as f:
            f.write(content)

    async def install_and_run(self, bundle_path: str) -> Dict:
        """安装依赖并尝试运行"""
        log_step("INSTALL", "安装项目依赖")

        # 检测语言
        language = await self._detect_language(bundle_path)
        log_info(f"项目语言: {language}")

        success = False
        error_msg = ""

        # 根据语言安装依赖
        if language == "Python":
            success, output = await self._install_python_deps(bundle_path)
        elif language == "Node.js":
            success, output = await self._install_node_deps(bundle_path)
        elif language == "Go":
            success, output = await self._install_go_deps(bundle_path)
        elif language == "Rust":
            success, output = await self._install_rust_deps(bundle_path)
        else:
            # 尝试通用安装
            success, output = await self._install_generic_deps(bundle_path)

        if success:
            # 返回运行信息
            run_command = self._get_run_command(language, bundle_path)
            return {
                "success": True,
                "language": language,
                "run_command": run_command,
                "bundle_path": bundle_path
            }
        else:
            return {
                "success": False,
                "language": language,
                "run_command": self._get_run_command(language, bundle_path),
                "error": error_msg
            }

    async def _install_python_deps(self, bundle_path: str) -> tuple[bool, str]:
        """安装 Python 依赖"""
        if os.path.exists(os.path.join(bundle_path, "requirements.txt")):
            success, output = await run_command(
                f"cd {bundle_path} && pip install -r requirements.txt",
                timeout=300
            )
            if success:
                log_step("DONE", "Python 依赖安装完成")
            return success, output

        if os.path.exists(os.path.join(bundle_path, "pyproject.toml")):
            success, output = await run_command(
                f"cd {bundle_path} && pip install -e .",
                timeout=300
            )
            return success, output

        return True, "无依赖文件"

    async def _install_node_deps(self, bundle_path: str) -> tuple[bool, str]:
        """安装 Node.js 依赖"""
        if os.path.exists(os.path.join(bundle_path, "package.json")):
            # 尝试 npm
            success, output = await run_command(
                f"cd {bundle_path} && npm install",
                timeout=300
            )
            if success:
                log_step("DONE", "Node.js 依赖安装完成")
                return True, output

            # 尝试 yarn
            success, output = await run_command(
                f"cd {bundle_path} && yarn install",
                timeout=300
            )
            if success:
                return True, output

            # 尝试 pnpm
            success, output = await run_command(
                f"cd {bundle_path} && pnpm install",
                timeout=300
            )
            return success, output

        return True, "无 package.json"

    async def _install_go_deps(self, bundle_path: str) -> tuple[bool, str]:
        """安装 Go 依赖"""
        success, output = await run_command(
            f"cd {bundle_path} && go mod download",
            timeout=300
        )
        if success:
            log_step("DONE", "Go 依赖下载完成")
        return success, output

    async def _install_rust_deps(self, bundle_path: str) -> tuple[bool, str]:
        """安装 Rust 依赖"""
        success, output = await run_command(
            f"cd {bundle_path} && cargo fetch",
            timeout=300
        )
        if success:
            log_step("DONE", "Rust 依赖下载完成")
        return success, output

    async def _install_generic_deps(self, bundle_path: str) -> tuple[bool, str]:
        """通用依赖安装"""
        # 检查 Makefile
        if os.path.exists(os.path.join(bundle_path, "Makefile")):
            success, output = await run_command(
                f"cd {bundle_path} && make install 2>/dev/null || make deps 2>/dev/null || true",
                timeout=120
            )
            return True, output

        return True, "无依赖需要安装"

    def _get_run_command(self, language: str, bundle_path: str) -> str:
        """获取运行命令"""
        if language == "Python":
            if os.path.exists(os.path.join(bundle_path, "main.py")):
                return "python main.py"
            elif os.path.exists(os.path.join(bundle_path, "app.py")):
                return "python app.py"
            return "python <主入口文件>"
        elif language == "Node.js":
            if os.path.exists(os.path.join(bundle_path, "package.json")):
                with open(os.path.join(bundle_path, "package.json")) as f:
                    import json
                    pkg = json.load(f)
                    if "scripts" in pkg and "start" in pkg["scripts"]:
                        return "npm start"
                    elif "scripts" in pkg and "dev" in pkg["scripts"]:
                        return "npm run dev"
            return "npm start"
        elif language == "Go":
            return "go run main.go"
        elif language == "Rust":
            return "cargo run"
        else:
            return "./start.sh"

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
