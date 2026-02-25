"""語言檢測器"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class LanguageInfo:
    """語言信息"""
    name: str
    extension: str
    run_command: str
    install_command: str
    config_files: List[str]
    detector_files: List[str]


class LanguageDetector:
    """檢測項目語言"""

    LANGUAGES: Dict[str, LanguageInfo] = {
        "python": LanguageInfo(
            name="Python",
            extension=".py",
            run_command="python {entry}",
            install_command="pip install -r requirements.txt",
            config_files=["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            detector_files=["__init__.py", "main.py", "app.py", "index.py"],
        ),
        "node": LanguageInfo(
            name="Node.js",
            extension=".js",
            run_command="node {entry}",
            install_command="npm install",
            config_files=["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            detector_files=["index.js", "main.js", "app.js", "server.js"],
        ),
        "typescript": LanguageInfo(
            name="TypeScript",
            extension=".ts",
            run_command="npx ts-node {entry}",
            install_command="npm install && npm install -D typescript ts-node @types/node",
            config_files=["tsconfig.json", "package.json"],
            detector_files=["index.ts", "main.ts", "app.ts"],
        ),
        "go": LanguageInfo(
            name="Go",
            extension=".go",
            run_command="go run {entry}",
            install_command="go mod download",
            config_files=["go.mod", "go.sum"],
            detector_files=["main.go"],
        ),
        "rust": LanguageInfo(
            name="Rust",
            extension=".rs",
            run_command="cargo run",
            install_command="cargo build",
            config_files=["Cargo.toml", "Cargo.lock"],
            detector_files=["main.rs", "lib.rs"],
        ),
        "java": LanguageInfo(
            name="Java",
            extension=".java",
            run_command="javac {entry} && java {class_name}",
            install_command="mvn install / gradle build",
            config_files=["pom.xml", "build.gradle", "settings.gradle"],
            detector_files=["Main.java", "App.java"],
        ),
        "csharp": LanguageInfo(
            name="C#",
            extension=".cs",
            run_command="dotnet run",
            install_command="dotnet restore",
            config_files=["*.csproj", "*.sln"],
            detector_files=["Program.cs", "Main.cs"],
        ),
        "php": LanguageInfo(
            name="PHP",
            extension=".php",
            run_command="php {entry}",
            install_command="composer install",
            config_files=["composer.json", "composer.lock"],
            detector_files=["index.php", "main.php"],
        ),
    }

    def __init__(self):
        self.language: Optional[LanguageInfo] = None
        self.detected_files: List[str] = []

    async def detect(self, project_path: str) -> Optional[LanguageInfo]:
        """檢測語言"""
        path = Path(project_path)

        # 方法1：檢測配置文件
        for lang_name, lang_info in self.LANGUAGES.items():
            for config_file in lang_info.config_files:
                if (path / config_file).exists():
                    self.language = lang_info
                    return lang_info

        # 方法2：檢測源碼文件
        for lang_name, lang_info in self.LANGUAGES.items():
            for detector_file in lang_info.detector_files:
                files = list(path.glob(f"**/{detector_file}"))
                if files:
                    self.detected_files = [str(f) for f in files[:5]]
                    self.language = lang_info
                    return lang_info

        # 方法3：檢測文件擴展名
        extensions = {}
        for lang_name, lang_info in self.LANGUAGES.items():
            ext_count = len(list(path.glob(f"**/*{lang_info.extension}")))
            if ext_count > 0:
                extensions[lang_name] = ext_count

        if extensions:
            detected = max(extensions, key=extensions.get)
            self.language = self.LANGUAGES[detected]
            return self.language

        return None

    def get_run_command(self, entry_file: str = None) -> str:
        """獲取運行命令"""
        if not self.language:
            return ""

        if "{entry}" in self.language.run_command and entry_file:
            return self.language.run_command.format(entry=entry_file)
        return self.language.run_command

    def get_install_command(self) -> str:
        """獲取安裝命令"""
        if self.language:
            return self.language.install_command
        return ""

    def suggest_entry_point(self, project_path: str) -> Optional[str]:
        """建議入口文件"""
        if not self.language:
            return None

        path = Path(project_path)
        for detector_file in self.language.detector_files:
            # 根目錄查找
            root_file = path / detector_file
            if root_file.exists():
                return str(root_file)

            # 遞歸查找
            files = list(path.glob(f"**/{detector_file}"))
            if files:
                return str(files[0])

        return None
