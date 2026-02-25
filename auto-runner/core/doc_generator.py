"""文檔生成器"""

import os
from typing import List, Dict
from pathlib import Path


class DocGenerator:
    """生成文檔"""

    def __init__(self, project_path: str, output_path: str = None):
        self.project_path = project_path
        self.output_path = output_path or project_path

    async def generate_all(self, run_result=None) -> Dict[str, str]:
        """生成所有文檔"""
        return {
            "README.md": await self.generate_readme(run_result),
            "TESTING.md": await self.generate_testing(),
            "CODE_ANALYSIS.md": await self.generate_code_analysis(),
        }

    async def generate_readme(self, run_result=None) -> str:
        """生成 README.md"""
        from core.language_detector import LanguageDetector

        detector = LanguageDetector()
        await detector.detect(self.project_path)
        language_name = detector.language.name if detector.language else "Unknown"

        lines = [
            "# 項目使用指南",
            "",
            "## 項目信息",
            f"- **語言**: {language_name}",
            f"- **運行狀態**: {'✅ 正常運行' if run_result and run_result.status.value == 'success' else '⚠️ 需要配置'}",
            "",
            "## 快速開始",
            "",
            "```bash",
            "# 克隆項目",
            f"git clone <此倉庫地址>",
            "",
            f"# 安裝依賴",
            f"{detector.get_install_command() if detector.language else '# 根據項目類型安裝'}",
            "",
            f"# 運行項目",
            f"{detector.get_run_command() if detector.language else '# 查看項目具體運行方式'}",
            "```",
            "",
        ]

        # 添加常見問題
        if run_result and run_result.stderr:
            lines.extend([
                "## 運行注意",
                "",
                "```",
                run_result.stderr[:500],
                "```",
                "",
            ])

        lines.extend([
            "## 目錄結構",
            "```",
            self._tree_structure(),
            "```",
            "",
            "## 依賴說明",
        ])

        # 添加依賴文件內容
        req_files = ["requirements.txt", "package.json", "go.mod", "Cargo.toml"]
        for req_file in req_files:
            path = os.path.join(self.project_path, req_file)
            if os.path.exists(path):
                lines.extend([
                    f"### {req_file}",
                    "```",
                    self._read_file(path),
                    "```",
                    "",
                ])

        return "\n".join(lines)

    async def generate_testing(self) -> str:
        """生成測試文檔"""
        from core.language_detector import LanguageDetector

        detector = LanguageDetector()
        await detector.detect(self.project_path)

        lines = [
            "# 測試用例",
            "",
            "## 基本測試",
            "",
            "### 1. 依賴安裝測試",
            "```bash",
            f"{detector.get_install_command() if detector.language else 'npm install'}",
            "```",
            "",
            "### 2. 運行測試",
            "```bash",
            f"{detector.get_run_command() if detector.language else 'npm start'}",
            "```",
            "",
            "### 3. 代碼質量測試",
        ]

        # 根據語言添加測試命令
        if detector.language:
            if detector.language.name == "Python":
                lines.extend([
                    "```bash",
                    "# 單元測試",
                    "pytest",
                    "",
                    "# 代碼格式檢查",
                    "flake8 .",
                    "",
                    "# 類型檢查",
                    "mypy .",
                    "```",
                ])
            elif detector.language.name in ["Node.js", "TypeScript"]:
                lines.extend([
                    "```bash",
                    "# 單元測試",
                    "npm test",
                    "",
                    "# 代碼格式檢查",
                    "npx eslint .",
                    "```",
                ])

        lines.extend([
            "",
            "## 自定義測試",
            "",
            "根據項目需求添加更多測試用例...",
            "",
            "## 測試結果記錄",
            "",
            "| 日期 | 測試項 | 結果 | 備註 |",
            "|------|--------|------|------|",
            "|      |        |      |      |",
        ])

        return "\n".join(lines)

    async def generate_code_analysis(self) -> str:
        """生成代碼解析文檔"""
        from core.language_detector import LanguageDetector

        detector = LanguageDetector()
        language = await detector.detect(self.project_path)

        lines = [
            "# 代碼解析文檔",
            "",
            "## 項目概覽",
            f"- **語言**: {language.name if language else 'Unknown'}",
            f"- **路徑**: {self.project_path}",
            "",
            "## 核心文件",
        ]

        # 列出主要源碼文件
        if language:
            source_files = list(Path(self.project_path).glob(f"**/*{language.extension}"))
            for f in source_files[:10]:
                lines.append(f"- {f.relative_to(self.project_path)}")

        lines.extend([
            "",
            "## 架構分析",
            "",
            "### 主要模塊",
            "",
            "（根據代碼結構自動生成）",
            "",
            "### 數據流",
            "",
            "（待補充）",
            "",
            "## API 接口",
            "",
            "（如適用）",
            "",
            "## 配置說明",
            "",
        ])

        # 讀取配置文件
        config_files = list(Path(self.project_path).glob("*.json"))
        config_files.extend(Path(self.project_path).glob("*.yaml"))
        config_files.extend(Path(self.project_path).glob("*.yml"))

        for config in config_files[:5]:
            lines.extend([
                f"### {config.name}",
                "```",
                self._read_file(str(config)),
                "```",
                "",
            ])

        return "\n".join(lines)

    def _tree_structure(self, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        """生成樹狀結構"""
        if current_depth >= max_depth:
            return ""

        result = []
        path = Path(self.project_path) if current_depth == 0 else Path(prefix)

        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                new_prefix = prefix + ("    " if is_last else "│   ")

                result.append(connector + item.name)

                if item.is_dir() and not item.name.startswith("."):
                    result.append(self._tree_structure(
                        str(item) + "/",
                        max_depth,
                        current_depth + 1
                    ))
        except PermissionError:
            pass

        return "\n".join(result)

    def _read_file(self, path: str, max_lines: int = 50) -> str:
        """讀取文件"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:max_lines]
                return "".join(lines)
        except Exception:
            return ""

    async def save_docs(self, docs: Dict[str, str]) -> bool:
        """保存文檔"""
        from utils.common import safe_mkdir

        await safe_mkdir(self.output_path)

        for filename, content in docs.items():
            path = os.path.join(self.output_path, filename)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"保存 {filename} 失敗: {e}")
                return False

        return True
