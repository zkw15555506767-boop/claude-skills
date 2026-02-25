"""
Auto-Runner Skill v2.0 - 一键运行 GitHub 项目

工作流程：
1. 获取项目 README，分析简单安装方式
2. 有简单方式 → 直接安装运行
3. 没有简单方式 → 创建本地整合包（克隆 + 依赖 + 启动脚本）
4. 生成代码文件说明文档
"""

import asyncio
import json
import os
import shutil
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path

from core.github_parser import GitHubParser
from core.simple_runner import SimpleRunnerDetector, suggest_run_way
from core.installer import SimpleInstaller
from core.bundler import ProjectBundler
from core.code_analyzer import CodeAnalyzer
from utils.common import run_command, log_step, log_info


@dataclass
class RunResult:
    """运行结果"""
    success: bool
    message: str
    project_path: Optional[str] = None  # 项目路径（整合包路径）
    install_method: str = ""  # 安装方式
    docs: Dict[str, str] = None  # 生成的文档
    code_guide: str = ""  # 代码说明文件路径

    def __post_init__(self):
        if self.docs is None:
            self.docs = {}


class AutoRunner:
    """自动运行器 v2.0"""

    MAX_RETRY = 2
    TEMP_DIR = "/tmp/auto-runner-v2"
    BUNDLE_DIR = "/tmp/auto-runner-bundles"  # 整合包保存目录

    def __init__(self):
        self.temp_dir = ""
        self.bundle_path = ""
        self.errors: List[str] = []

    async def run(self, github_url: str) -> RunResult:
        """主入口：自动判断并运行"""
        self.errors = []
        log_step("🚀", "开始处理 GitHub 项目")
        log_info(f"URL: {github_url}")

        try:
            # 1. 解析 URL
            log_step("STEP 1", "解析 GitHub URL")
            parser = GitHubParser(github_url)
            repo_info = parser.parse()

            if not repo_info:
                return RunResult(
                    success=False,
                    message=f"❌ 无法解析 GitHub URL: {github_url}"
                )

            log_info(f"项目: {repo_info.owner}/{repo_info.repo}")

            # 2. 获取项目信息（API + README）
            log_step("STEP 2", "获取项目信息")
            api_info = await self._fetch_project_info(repo_info.owner, repo_info.repo)

            if not api_info or not api_info.get("readme"):
                # 无法获取 README，转为完整克隆
                log_step("WARN", "无法获取 API 信息，转为完整克隆模式")
                return await self._create_bundle_and_run(repo_info)

            # 3. 分析 README，检测简单安装方式
            log_step("STEP 3", "分析安装方式")
            readme = api_info["readme"]
            language = api_info.get("language", "")

            # 检测简单运行方式
            detector = SimpleRunnerDetector()
            simple_methods = await detector.detect(readme, language, api_info)

            if simple_methods:
                # 有简单方式，尝试安装运行
                log_step("INFO", f"发现 {len(simple_methods)} 种简单安装方式")
                install_result = await self._try_simple_install(
                    api_info, simple_methods[0], repo_info
                )
                if install_result:
                    return install_result

            # 4. 没有简单方式或安装失败，创建整合包
            log_step("INFO", "无简单安装方式，创建本地整合包")
            return await self._create_bundle_and_run(repo_info, api_info)

        except Exception as e:
            log_step("ERROR", f"处理出错: {e}")
            return RunResult(
                success=False,
                message=f"❌ 处理过程中出错: {str(e)}"
            )

    async def _fetch_project_info(self, owner: str, repo: str) -> Optional[dict]:
        """获取项目信息"""
        try:
            import urllib.request
            import json as json_module

            # 获取仓库信息
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(repo_url, headers={"User-Agent": "Claude-Code"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                repo_data = json_module.loads(resp.read().decode())

            # 获取 README
            readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            req = urllib.request.Request(readme_url, headers={
                "User-Agent": "Claude-Code",
                "Accept": "application/vnd.github.v3.raw"
            })
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    readme = resp.read().decode("utf-8")
            except:
                readme = ""

            return {
                "owner": owner,
                "repo": repo,
                "name": repo_data.get("name", repo),
                "description": repo_data.get("description", ""),
                "language": repo_data.get("language", ""),
                "stars": repo_data.get("stargazers_count", 0),
                "readme": readme,
                "topics": repo_data.get("topics", []),
                "homepage": repo_data.get("homepage", ""),
            }
        except Exception as e:
            log_step("WARN", f"API 获取失败: {e}")
            return None

    async def _try_simple_install(
        self, api_info: dict, simple_method, repo_info
    ) -> Optional[RunResult]:
        """尝试简单安装方式"""
        installer = SimpleInstaller()

        success, message, install_path = await installer.install(
            api_info, simple_method, repo_info
        )

        if success and install_path:
            # 安装成功，生成代码说明文档
            code_guide = await self._generate_code_guide(install_path, api_info)

            return RunResult(
                success=True,
                message=message,
                project_path=install_path,
                install_method=simple_method.method,
                code_guide=code_guide
            )
        else:
            log_step("WARN", f"简单安装失败: {message}")
            return None

    async def _create_bundle_and_run(
        self, repo_info, api_info=None
    ) -> RunResult:
        """创建整合包并运行"""
        # 创建整合包
        bundler = ProjectBundler(self.BUNDLE_DIR)
        bundle_path, clone_success = await bundler.create_bundle(repo_info, api_info)

        if not clone_success:
            return RunResult(
                success=False,
                message="❌ 克隆失败，无法创建整合包"
            )

        # 安装依赖并运行
        run_result = await bundler.install_and_run(bundle_path)

        # 生成代码说明文档
        code_guide = await self._generate_code_guide(bundle_path, api_info)

        message = f"""
## ✅ 项目已就绪！

**{repo_info.owner}/{repo_info.repo}**

---

### 📦 整合包位置
```
{bundle_path}
```

### 🚀 启动项目

```bash
cd {bundle_path}
```

### 📝 启动命令
```bash
{run_result.get('run_command', '请查看项目 README')}
```

---

### 📄 代码说明文档
代码说明已生成: `{code_guide}`

这个文档详细说明了项目中每个代码文件的作用，帮助你理解和修改项目。
"""

        return RunResult(
            success=run_result.get("success", False),
            message=message,
            project_path=bundle_path,
            install_method="bundle",
            code_guide=code_guide
        )

    async def _generate_code_guide(
        self, project_path: str, api_info: Optional[dict]
    ) -> str:
        """生成代码说明文档"""
        try:
            analyzer = CodeAnalyzer(project_path)
            guide_path = await analyzer.generate_guide(api_info)
            log_step("DOC", f"代码说明文档: {guide_path}")
            return guide_path
        except Exception as e:
            log_step("WARN", f"生成代码说明失败: {e}")
            return ""


async def main(github_url: str):
    """CLI 主入口"""
    print("=" * 60)
    print("Auto-Runner Skill v2.0")
    print("一键运行 GitHub 项目，自动安装并生成代码说明")
    print("=" * 60)
    print()

    runner = AutoRunner()
    result = await runner.run(github_url)

    print()
    print("=" * 60)
    print("运行结果")
    print("=" * 60)
    print(result.message)

    if result.success:
        print()
        print("✅ 安装/运行成功！")
        if result.code_guide:
            print(f"📄 代码说明文档: {result.code_guide}")
    else:
        print()
        print("❌ 遇到问题，请查看上方错误信息")

    print("=" * 60)

    return result


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("GitHub URL: ").strip()
    result = asyncio.run(main(url))
