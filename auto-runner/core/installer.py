"""
简单安装器 - 尝试通过简单方式安装项目

支持：pip, npm/npx, docker, brew, 二进制下载, 在线演示
"""

import asyncio
import os
import shutil
import subprocess
import urllib.request
from typing import Tuple, Optional
from dataclasses import dataclass

from utils.common import run_command, log_step, log_info


@dataclass
class InstallResult:
    """安装结果"""
    success: bool
    message: str
    install_path: str  # 安装位置（如 pip 包路径、容器名等）


class SimpleInstaller:
    """简单安装器"""

    def __init__(self):
        self.temp_dir = "/tmp/auto-runner-install"

    async def install(
        self, api_info: dict, simple_method, repo_info
    ) -> Tuple[bool, str, str]:
        """
        尝试安装项目

        Returns:
            (success, message, install_path)
        """
        method = simple_method.method
        command = simple_method.command
        description = simple_run.description

        log_step("INSTALL", f"尝试 {method} 安装")

        try:
            if method == "pip":
                return await self._install_pip(command, api_info)
            elif method == "npx":
                return await self._run_npx(command, api_info)
            elif method == "docker":
                return await self._run_docker(command, api_info)
            elif method == "brew":
                return await self._install_brew(command, api_info)
            elif method == "binary":
                return await self._download_binary(command, api_info, repo_info)
            elif method == "demo":
                return await self._open_demo(command, api_info)
            else:
                return False, f"不支持的安装方式: {method}", ""
        except Exception as e:
            return False, f"安装失败: {str(e)}", ""

    async def _install_pip(self, command: str, api_info: dict) -> Tuple[bool, str, str]:
        """pip 安装"""
        # 提取包名
        import re
        match = re.search(r"pip install\s+([a-zA-Z0-9_-]+)", command)
        package = match.group(1) if match else command.replace("pip install ", "").strip()

        log_info(f"安装 pip 包: {package}")

        # 检查是否已安装
        success, output = await run_command(f"pip show {package}", timeout=30)
        if success:
            return True, f"✅ pip 包 `{package}` 已安装\n\n运行命令: `{package}` 或 `python -m {package}`", package

        # 尝试安装
        success, output = await run_command(f"pip install {package}", timeout=120)
        if success:
            return True, f"""
## ✅ pip 安装成功！

**包名**: {package}

### 运行方式

```bash
# 方式1: 直接运行
{package}

# 方式2: Python 模块运行
python -m {package}
```

---

_由 Auto-Runner 自动安装_
""", package
        else:
            return False, f"pip 安装失败: {output}", ""

    async def _run_npx(self, command: str, api_info: dict) -> Tuple[bool, str, str]:
        """npx 运行（无需安装）"""
        log_info(f"通过 npx 运行: {command}")

        # npx 是直接运行，不需要安装
        return True, f"""
## ✅ 通过 npx 运行

**命令**: `{command}`

### 使用方式

直接在终端运行：

```bash
{command}
```

> npx 会自动下载并运行，无需提前安装

---

_由 Auto-Runner 提供_
""", command

    async def _run_docker(self, command: str, api_info: dict) -> Tuple[bool, str, str]:
        """Docker 运行"""
        log_info(f"通过 Docker 运行: {command}")

        # 检查 Docker 是否可用
        success, _ = await run_command("docker --version", timeout=10)
        if not success:
            return False, "Docker 未安装或不可用", ""

        # 检查镜像是否存在
        image = command.replace("docker run ", "").split()[0] if "docker run" in command else command
        success, output = await run_command(f"docker images -q {image.split(':')[0] if ':' in image else image}", timeout=10)

        if not success:
            # 尝试拉取镜像
            log_step("DOCKER", "拉取镜像中...")
            success, output = await run_command(f"docker pull {image}", timeout=300)

        if success:
            return True, f"""
## ✅ Docker 镜像已就绪

**镜像**: {image}

### 运行方式

```bash
{command}
```

### 常用命令

```bash
# 查看运行中的容器
docker ps

# 停止容器
docker stop <container_id>
```

---

_由 Auto-Runner 提供_
""", image
        else:
            return False, f"Docker 操作失败: {output}", ""

    async def _install_brew(self, command: str, api_info: dict) -> Tuple[bool, str, str]:
        """Homebrew 安装"""
        import re
        match = re.search(r"brew install\s+([a-zA-Z0-9_-]+)", command)
        formula = match.group(1) if match else command.replace("brew install ", "").strip()

        log_info(f"安装 Homebrew 包: {formula}")

        # 检查是否已安装
        success, output = await run_command(f"brew list {formula}", timeout=30)
        if success:
            return True, f"✅ Homebrew 包 `{formula}` 已安装\n\n运行命令: `{formula}`", formula

        # 尝试安装
        success, output = await run_command(f"brew install {formula}", timeout=300)
        if success:
            return True, f"""
## ✅ Homebrew 安装成功！

**包名**: {formula}

### 运行方式

```bash
{formula}
```

---

_由 Auto-Runner 自动安装_
""", formula
        else:
            return False, f"Homebrew 安装失败: {output}", ""

    async def _download_binary(
        self, command: str, api_info: dict, repo_info
    ) -> Tuple[bool, str, str]:
        """二进制下载"""
        log_info(f"下载二进制: {command}")

        # 创建下载目录
        download_dir = os.path.join(self.temp_dir, "binary", repo_info.repo)
        os.makedirs(download_dir, exist_ok=True)

        # 判断操作系统
        import platform
        system = platform.system().lower()
        if "darwin" in system:
            suffix = "macos" if "arm" in platform.machine().lower() else "x64"
        elif "linux" in system:
            suffix = "linux"
        elif "windows" in system:
            suffix = "windows"
        else:
            suffix = ""

        # 提取下载 URL
        download_url = command.strip()
        if not download_url.startswith("http"):
            # 尝试从 README 中提取
            download_url = ""

        if download_url:
            filename = download_url.split("/")[-1].split("?")[0]
            filepath = os.path.join(download_dir, filename)

            try:
                log_step("DOWNLOAD", f"下载 {filename}...")
                req = urllib.request.Request(download_url, headers={"User-Agent": "curl"})
                with urllib.request.urlopen(req, timeout=120) as resp, open(filepath, 'wb') as f:
                    f.write(resp.read())

                # 添加执行权限
                os.chmod(filepath, 0o755)

                return True, f"""
## ✅ 二进制已下载

**文件**: {filename}
**位置**: {filepath}

### 运行方式

```bash
# 添加执行权限（如果需要）
chmod +x {filepath}

# 运行
{filepath}
```

---

_由 Auto-Runner 自动下载_
""", filepath
            except Exception as e:
                return False, f"下载失败: {str(e)}", ""
        else:
            return False, "无法提取下载链接", ""

    async def _open_demo(self, command: str, api_info: dict) -> Tuple[bool, str, str]:
        """在线演示"""
        log_info(f"在线演示: {command}")

        return True, f"""
## 🌐 在线演示

**链接**: {command}

### 使用方式

直接在浏览器中打开上述链接即可使用，无需安装任何东西。

---

_由 Auto-Runner 提供_
""", command


# 简化的 simple_run 变量（兼容）
simple_run = None
