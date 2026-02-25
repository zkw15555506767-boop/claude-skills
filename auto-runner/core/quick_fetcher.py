"""项目信息获取器 - 轻量级获取项目信息"""

import asyncio
import json
from typing import Optional, Dict, List
from dataclasses import dataclass
from urllib.request import urlopen
from urllib.error import URLError


@dataclass
class ProjectInfo:
    """项目信息"""
    name: str
    description: str
    language: str
    stars: int
    forks: int
    owner: str
    repo: str
    readme: str
    install_cmd: str
    run_cmd: str
    topics: List[str]


class LightweightProjectInfo:
    """轻量级项目信息获取"""

    GITHUB_API = "https://api.github.com"

    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    async def fetch(self) -> Optional[ProjectInfo]:
        """获取项目信息"""
        try:
            # 获取仓库信息
            repo_url = f"{self.GITHUB_API}/repos/{self.owner}/{self.repo}"
            repo_data = await self._fetch_url(repo_url)
            if not repo_data:
                return None

            # 获取 README
            readme_url = f"{self.GITHUB_API}/readme/{self.owner}/{self.repo}"
            readme_data = await self._fetch_url(readme_url, accept="application/vnd.github.v3.raw")

            # 解析 README
            readme_content = ""
            if readme_data:
                readme_content = self._parse_readme(readme_data)

            # 生成安装和运行命令
            install_cmd, run_cmd = self._guess_commands(readme_content, repo_data.get("language", ""))

            return ProjectInfo(
                name=repo_data.get("name", ""),
                description=repo_data.get("description", ""),
                language=repo_data.get("language", ""),
                stars=repo_data.get("stargazers_count", 0),
                forks=repo_data.get("forks_count", 0),
                owner=self.owner,
                repo=self.repo,
                readme=readme_content,
                install_cmd=install_cmd,
                run_cmd=run_cmd,
                topics=repo_data.get("topics", []),
            )
        except Exception as e:
            print(f"获取项目信息失败: {e}")
            return None

    async def _fetch_url(self, url: str, accept: str = "application/vnd.github.v3+json") -> Optional[dict]:
        """获取 URL 内容"""
        try:
            import urllib.request
            import urllib.parse

            req = urllib.request.Request(url, headers={
                "Accept": accept,
                "User-Agent": "Claude-Code",
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        except Exception as e:
            print(f"请求失败: {url} - {e}")
            return None

    def _parse_readme(self, readme: str) -> str:
        """解析 README"""
        if not readme:
            return ""

        # 截取主要内容（前3000字符）
        lines = readme.split("\n")[:100]
        content = "\n".join(lines)

        # 提取安装和运行命令
        install_hints = []
        run_hints = []

        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["pip install", "npm install", "cargo", "go get", "maven", "gradle"]):
                install_hints.append(line.strip().strip("`").strip())
            if any(kw in line_lower for kw in ["python", "npm start", "cargo run", "go run", "./", "python3"]):
                if "install" not in line_lower:
                    run_hints.append(line.strip().strip("`").strip())

        return content

    def _guess_commands(self, readme: str, language: str) -> tuple[str, str]:
        """猜测安装和运行命令"""
        install_cmd = ""
        run_cmd = ""

        readme_lower = readme.lower() if readme else ""

        if "python" in readme_lower or language == "Python":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = "python main.py 或 python app.py"
        elif "node" in readme_lower or language == "JavaScript" or language == "TypeScript":
            install_cmd = "npm install 或 yarn install"
            run_cmd = "npm start 或 npm run dev"
        elif "cargo" in readme_lower or language == "Rust":
            install_cmd = "cargo build"
            run_cmd = "cargo run"
        elif "go " in readme_lower or language == "Go":
            install_cmd = "go mod download"
            run_cmd = "go run main.go"
        elif "maven" in readme_lower or "gradle" in readme_lower or language == "Java":
            install_cmd = "mvn install 或 ./gradlew build"
            run_cmd = "mvn spring-boot:run 或 java -jar target/*.jar"
        elif "composer" in readme_lower or language == "PHP":
            install_cmd = "composer install"
            run_cmd = "php index.php"

        return install_cmd, run_cmd


async def quick_check_github(url: str) -> str:
    """快速检查 GitHub 项目"""
    # 解析 URL
    owner, repo = "", ""
    if "github.com/" in url:
        parts = url.split("github.com/")[-1].rstrip("/").split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1].replace(".git", "")

    if not owner or not repo:
        return f"❌ 无法解析 URL: {url}"

    # 获取信息
    fetcher = LightweightProjectInfo(owner, repo)
    info = await fetcher.fetch()

    if not info:
        return f"❌ 无法获取项目信息: {owner}/{repo}"

    # 生成报告
    report = f"""
## 📦 项目概览

**{info.owner}/{info.name}**

{info.description or "暂无描述"}

⭐ {info.stars} | 🍴 {info.forks} | 🐍 {info.language}

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/{info.owner}/{info.repo}.git
cd {info.repo}
```

**安装依赖:**
```
{info.install_cmd or "根据项目类型安装"}
```

**运行项目:**
```
{info.run_cmd or "查看项目文档"}
```

---

## 📝 项目 README 摘要

{info.readme[:1500]}...

---

## 💡 下一步

1. 查看完整 README
2. 根据上面的命令安装和运行
3. 如需完整调试，请告诉我

需要我帮你：
- A. 完整克隆并运行
- B. 查看更多技术细节
- C. 生成使用文档
"""
    return report


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("GitHub URL: ")
    result = asyncio.run(quick_check_github(url))
    print(result)
