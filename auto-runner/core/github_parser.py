"""GitHub 链接解析器"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitHubRepoInfo:
    """仓库信息"""
    owner: str
    repo: str
    branch: str = "main"
    path: str = ""
    raw_url: str = ""


class GitHubParser:
    """解析 GitHub URL"""

    # 支持的 URL 格式
    PATTERNS = [
        # https://github.com/owner/repo
        r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        # https://github.com/owner/repo/tree/branch
        r"github\.com/([^/]+)/([^/]+)/tree/([^/]+)(?:/(.*))?$",
        # https://github.com/owner/repo/tree/branch/path
        r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)$",
    ]

    def __init__(self, url: str):
        self.url = url.strip()

    def parse(self) -> Optional[GitHubRepoInfo]:
        """解析 URL"""
        # 移除 .git 後綴
        clean_url = self.url.rstrip("/").replace(".git", "")

        for pattern in self.PATTERNS:
            match = re.search(pattern, clean_url)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return GitHubRepoInfo(
                        owner=groups[0],
                        repo=groups[1].rstrip("/"),
                        branch="main",
                        raw_url=f"https://raw.githubusercontent.com/{groups[0]}/{groups[1].rstrip('/')}/main",
                    )
                elif len(groups) >= 4:
                    path = groups[3] if len(groups) > 3 else ""
                    return GitHubRepoInfo(
                        owner=groups[0],
                        repo=groups[1],
                        branch=groups[2],
                        path=path,
                        raw_url=f"https://raw.githubusercontent.com/{groups[0]}/{groups[1]}/{groups[2]}/{path}",
                    )

        return None

    def get_clone_url(self) -> str:
        """獲取克隆 URL"""
        info = self.parse()
        if info:
            return f"https://github.com/{info.owner}/{info.repo}.git"
        return ""

    def get_api_url(self) -> str:
        """獲取 API URL"""
        info = self.parse()
        if info:
            return f"https://api.github.com/repos/{info.owner}/{info.repo}"
        return ""
