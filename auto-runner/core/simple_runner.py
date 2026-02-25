"""简单运行方式检测器"""

import re
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class SimpleRunInfo:
    """简单运行方式信息"""
    method: str  # pip/npm/docker/binary/demo/brew
    command: str
    description: str
    confidence: float  # 0-1 置信度


class SimpleRunnerDetector:
    """检测是否有简单运行方式"""

    def __init__(self):
        self.simple_methods: List[SimpleRunInfo] = []

    async def detect(self, readme: str, language: str, repo_data: dict) -> List[SimpleRunInfo]:
        """检测简单运行方式"""
        self.simple_methods = []

        if not readme:
            return []

        readme_lower = readme.lower()

        # 1. 检测 npx (最高优先级 - 直接运行)
        await self._detect_npx(readme, language)

        # 2. 检测 pip 包
        await self._detect_pip(readme, language)

        # 3. 检测 Docker
        await self._detect_docker(readme)

        # 4. 检测 Homebrew
        await self._detect_brew(readme)

        # 5. 检测二进制下载
        await self._detect_binary(readme)

        # 6. 检测在线演示
        await self._detect_demo(readme)

        # 按置信度排序
        self.simple_methods.sort(key=lambda x: x.confidence, reverse=True)

        return self.simple_methods

    async def _detect_npx(self, readme: str, language: str):
        """检测 npx 直接运行方式"""
        if language not in ["JavaScript", "TypeScript", ""]:
            return

        # 查找 npx <command> 模式
        matches = re.findall(r"npx\s+([a-zA-Z0-9_-]+)", readme)
        for pkg in matches[:3]:
            # 跳过常见的工具名
            if pkg.lower() in ["npm", "node", "create-react-app", "vue", "ng"]:
                continue
            self.simple_methods.append(SimpleRunInfo(
                method="npx",
                command=f"npx {pkg}",
                description=f"通过 npx 直接运行，无需安装",
                confidence=0.95,
            ))

    async def _detect_pip(self, readme: str, language: str):
        """检测 pip 安装方式"""
        if language not in ["Python", ""]:
            return

        readme_lower = readme.lower()

        # 查找 pip install <package>
        matches = re.findall(r"pip install\s+([a-zA-Z0-9_-]+)", readme, re.IGNORECASE)
        for pkg in matches[:3]:
            self.simple_methods.append(SimpleRunInfo(
                method="pip",
                command=f"pip install {pkg}",
                description=f"pip 安装 {pkg}",
                confidence=0.9,
            ))

        # 查找 pipx
        if "pipx" in readme_lower:
            self.simple_methods.append(SimpleRunInfo(
                method="pipx",
                command="pipx install <package>",
                description="通过 pipx 安装并运行",
                confidence=0.85,
            ))

    async def _detect_docker(self, readme: str):
        """检测 Docker 运行方式"""
        readme_lower = readme.lower()

        # 查找 docker run <image>
        matches = re.findall(r"docker run\s+(?:--[\w-]+\s+)*([a-zA-Z0-9_/-]+)", readme)
        for img in matches[:2]:
            img_lower = img.lower()
            # 跳过 docker 官方镜像
            if img_lower in ["docker", "docker/cli", "docker/compose"]:
                continue
            self.simple_methods.append(SimpleRunInfo(
                method="docker",
                command=f"docker run {img}",
                description=f"通过 Docker 运行 {img}",
                confidence=0.85,
            ))

        # 查找 docker-compose
        if "docker-compose" in readme_lower:
            self.simple_methods.append(SimpleRunInfo(
                method="docker",
                command="docker-compose up",
                description="通过 docker-compose 启动",
                confidence=0.8,
            ))

    async def _detect_brew(self, readme: str):
        """检测 Homebrew 安装方式"""
        # 查找 brew install <formula>
        matches = re.findall(r"brew install\s+([a-zA-Z0-9_-]+)", readme, re.IGNORECASE)
        for pkg in matches[:2]:
            self.simple_methods.append(SimpleRunInfo(
                method="brew",
                command=f"brew install {pkg}",
                description=f"通过 Homebrew 安装 {pkg}",
                confidence=0.9,
            ))

        # 查找 brew cask
        matches = re.findall(r"brew install --cask\s+([a-zA-Z0-9_-]+)", readme, re.IGNORECASE)
        for pkg in matches[:2]:
            self.simple_methods.append(SimpleRunInfo(
                method="brew",
                command=f"brew install --cask {pkg}",
                description=f"通过 Homebrew Cask 安装 {pkg} (桌面应用)",
                confidence=0.9,
            ))

    async def _detect_binary(self, readme: str):
        """检测二进制下载"""
        # 查找下载链接
        download_patterns = [
            (r"\[Download.*?\]\(([^)]+linux[^)]+\))", "Linux 下载"),
            (r"\[Download.*?\]([^)]+macos[^)]+\))", "macOS 下载"),
            (r"\[Download.*?\]([^)]+windows[^)]+\))", "Windows 下载"),
            (r"https://github\.com/[^)]+releases/tag/[^)]+", "GitHub Releases"),
        ]

        for pattern, desc in download_patterns:
            matches = re.findall(pattern, readme, re.IGNORECASE)
            if matches:
                self.simple_methods.append(SimpleRunInfo(
                    method="binary",
                    command=matches[0][:80] + "...",
                    description=f"下载预编译二进制 ({desc})",
                    confidence=0.75,
                ))

    async def _detect_demo(self, readme: str):
        """检测在线演示"""
        demo_patterns = [
            (r"https?://[^\s]*\.stackblitz\.[^\s]*", "StackBlitz 在线演示"),
            (r"https?://[^\s]*codesandbox\.io[^\s]*", "CodeSandbox 在线演示"),
            (r"https?://[^\s]*replit\.com[^\s]*", "Replit 在线演示"),
            (r"https?://[^\s]*demo[^\s]*", "在线演示"),
            (r"https?://[^\s]*playground[^\s]*", "Playground"),
        ]

        for pattern, desc in demo_patterns:
            match = re.search(pattern, readme)
            if match:
                self.simple_methods.append(SimpleRunInfo(
                    method="demo",
                    command=match.group(0),
                    description=desc,
                    confidence=0.6,
                ))

    def get_best_method(self) -> Optional[SimpleRunInfo]:
        """获取最佳简单运行方式"""
        if self.simple_methods:
            return self.simple_methods[0]
        return None


async def suggest_run_way(readme: str, language: str, repo_data: dict) -> str:
    """建议运行方式"""
    detector = SimpleRunnerDetector()
    methods = await detector.detect(readme, language, repo_data)

    if not methods:
        return ""

    best = methods[0]

    suggestions = ["\n## 🎯 简单运行方式（推荐）\n"]

    for i, method in enumerate(methods[:3], 1):
        suggestions.append(f"### 方式{i}: {method.method.upper()}")
        suggestions.append(f"```bash")
        suggestions.append(method.command)
        suggestions.append("```")
        suggestions.append(f"*{method.description}*\n")

    return "\n".join(suggestions)


if __name__ == "__main__":
    import asyncio

    # 测试
    readme = """
    # My CLI Tool

    ## Install
    pip install my-cli-tool
    npx my-cli-tool
    brew install mytool

    ## Docker
    docker run myimage

    ## Download
    Download from [releases](https://github.com/user/repo/releases)
    """

    async def test():
        detector = SimpleRunnerDetector()
        methods = await detector.detect(readme, "Python", {})
        print(f"检测到 {len(methods)} 种简单运行方式:")
        for m in methods:
            print(f"  [{m.confidence:.2f}] {m.method}: {m.command}")

    asyncio.run(test())
