"""依賴解決器"""

import os
from typing import List, Optional
from core.language_detector import LanguageDetector


class DependencySolver:
    """解決依賴安裝"""

    # 常見錯誤的修復方案
    FIX_STRATEGIES = {
        "pip": {
            "command": "pip install -r requirements.txt",
            "alternatives": [
                "pip3 install -r requirements.txt",
                "python -m pip install -r requirements.txt",
                "python3 -m pip install -r requirements.txt",
            ],
        },
        "npm": {
            "command": "npm install",
            "alternatives": ["yarn install", "pnpm install"],
        },
        "go": {
            "command": "go mod download",
            "alternatives": ["go mod tidy", "go get ./..."],
        },
        "cargo": {
            "command": "cargo build",
            "alternatives": ["cargo fetch", "cargo update"],
        },
        "maven": {
            "command": "mvn install",
            "alternatives": ["mvn compile", "mvn package"],
        },
        "gradle": {
            "command": "gradle build",
            "alternatives": ["gradle assemble", "gradle classes"],
        },
        "composer": {
            "command": "composer install",
            "alternatives": ["composer update"],
        },
        "dotnet": {
            "command": "dotnet restore",
            "alternatives": ["dotnet build"],
        },
    }

    async def install(
        self,
        project_path: str,
        language: str,
        timeout: int = 300,
    ) -> tuple[bool, str]:
        """安裝依賴"""
        from utils.common import run_command, log_step

        log_step("DEPENDENCY", f"開始安裝 {language} 依賴")

        strategy = self.FIX_STRATEGIES.get(language.lower())
        if not strategy:
            return False, f"不支持的語言: {language}"

        # 嘗試主命令
        success, output = await run_command(
            strategy["command"],
            cwd=project_path,
            timeout=timeout,
        )

        if success:
            return True, "依賴安裝成功"

        # 嘗試替代命令
        for alt_cmd in strategy.get("alternatives", []):
            log_step("DEPENDENCY", f"嘗試替代命令: {alt_cmd}")
            success, output = await run_command(
                alt_cmd,
                cwd=project_path,
                timeout=timeout,
            )
            if success:
                return True, f"使用替代命令成功: {alt_cmd}"

        return False, f"依賴安裝失敗: {output}"

    async def check_requirements(self, project_path: str) -> List[str]:
        """檢查需要的依賴文件"""
        import os

        requirements = []
        check_files = [
            "requirements.txt",
            "package.json",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "composer.json",
            "*.csproj",
        ]

        for pattern in check_files:
            path = os.path.join(project_path, pattern.replace("*", ""))
            if os.path.exists(path):
                requirements.append(path)

        return requirements
