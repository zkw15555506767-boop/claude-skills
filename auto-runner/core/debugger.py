"""錯誤調試器"""

import re
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ErrorType(Enum):
    """錯誤類型"""
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    CONFIG_ERROR = "config_error"
    DEPENDENCY_ERROR = "dependency_error"
    RUNTIME_ERROR = "runtime_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """錯誤信息"""
    error_type: ErrorType
    message: str
    file: str
    line: int
    suggestion: str
    fix_command: str


class Debugger:
    """自動調試"""

    # 錯誤模式匹配
    ERROR_PATTERNS = [
        # ImportError
        (
            r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
            ErrorType.IMPORT_ERROR,
            lambda m: f"安裝模塊: pip install {m.group(1)}",
            lambda m: f"pip install {m.group(1)}",
        ),
        (
            r"ImportError: cannot import name ['\"]([^'\"]+)['\"]",
            ErrorType.IMPORT_ERROR,
            lambda m: f"檢查導入: 可能需要安裝額外依賴",
            lambda m: "pip install -r requirements.txt",
        ),
        # SyntaxError
        (
            r"SyntaxError: invalid syntax",
            ErrorType.SYNTAX_ERROR,
            lambda m: "檢查語法錯誤，可能需要手動修復",
            lambda m: "",
        ),
        (
            r"SyntaxError: unexpected EOF while parsing",
            ErrorType.SYNTAX_ERROR,
            lambda m: "文件可能不完整，缺少結尾",
            lambda m: "",
        ),
        # ConfigError
        (
            r"FileNotFoundError: No such file or directory: ['\"]([^'\"]+)['\"]",
            ErrorType.CONFIG_ERROR,
            lambda m: f"創建缺失的文件: {m.group(1)}",
            lambda m: "",
        ),
        (
            r"ValueError: .*",
            ErrorType.CONFIG_ERROR,
            lambda m: "配置值錯誤，檢查環境變量或配置文件",
            lambda m: "",
        ),
        # DependencyError
        (
            r"npm ERR!",
            ErrorType.DEPENDENCY_ERROR,
            lambda m: "npm 安裝失敗，嘗試清除緩存",
            lambda m: "rm -rf node_modules package-lock.json && npm install",
        ),
        (
            r"go: .*",
            ErrorType.DEPENDENCY_ERROR,
            lambda m: "Go 依賴問題",
            lambda m: "go mod tidy",
        ),
        # PermissionError
        (
            r"PermissionError: .*",
            ErrorType.PERMISSION_ERROR,
            lambda m: "權限不足，嘗試修改權限",
            lambda m: "chmod +x",
        ),
        # RuntimeError
        (
            r"RuntimeError: .*",
            ErrorType.RUNTIME_ERROR,
            lambda m: "運行時錯誤，檢查代碼邏輯",
            lambda m: "",
        ),
        # ConnectionError
        (
            r"ConnectionError: .*",
            ErrorType.RUNTIME_ERROR,
            lambda m: "網絡連接問題，檢查網絡設置",
            lambda m: "",
        ),
    ]

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.error_history: List[ErrorInfo] = []

    def analyze(self, error_output: str) -> List[ErrorInfo]:
        """分析錯誤輸出"""
        errors = []

        for pattern, error_type, suggestion_fn, fix_fn in self.ERROR_PATTERNS:
            matches = re.finditer(pattern, error_output)
            for match in matches:
                error = ErrorInfo(
                    error_type=error_type,
                    message=match.group(0),
                    file=self._extract_file(match.group(0)),
                    line=self._extract_line(match.group(0)),
                    suggestion=suggestion_fn(match),
                    fix_command=fix_fn(match),
                )
                errors.append(error)
                self.error_history.append(error)

        if not errors:
            # 未知錯誤
            errors.append(ErrorInfo(
                error_type=ErrorType.UNKNOWN,
                message=error_output[:500],
                file="",
                line=0,
                suggestion="需要手動檢查錯誤",
                fix_command="",
            ))

        return errors

    def apply_fix(self, error: ErrorInfo) -> tuple[bool, str]:
        """應用修復"""
        from utils.common import run_command

        if not error.fix_command:
            return False, "無修復命令"

        import os
        cwd = os.path.dirname(error.file) if error.file else self.project_path

        success, output = run_command(error.fix_command, cwd=cwd)
        return success, output

    async def auto_fix(self, error_output: str, max_attempts: int = 3) -> tuple[bool, str, List[ErrorInfo]]:
        """自動修復"""
        errors = self.analyze(error_output)

        for attempt in range(max_attempts):
            for error in errors:
                if error.fix_command:
                    success, output = self.apply_fix(error)
                    if success:
                        return True, f"修復成功: {error.suggestion}", errors

        return False, "無法自動修復", errors

    def get_fix_summary(self, errors: List[ErrorInfo]) -> str:
        """獲取修復摘要"""
        if not errors:
            return "未檢測到錯誤"

        lines = ["### 錯誤分析\n"]
        for i, error in enumerate(errors, 1):
            lines.append(f"**{i}. {error.error_type.value}**")
            lines.append(f"   - 錯誤: {error.message[:100]}")
            lines.append(f"   - 建議: {error.suggestion}")
            if error.fix_command:
                lines.append(f"   - 修復命令: `{error.fix_command}`")
            lines.append("")

        return "\n".join(lines)

    def _extract_file(self, message: str) -> str:
        """提取文件名"""
        patterns = [
            r"File ['\"]([^'\"]+)['\"]",
            r"'([^']+\.py)'",
            r'"([^"]+\.js)"',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return ""

    def _extract_line(self, message: str) -> int:
        """提取行號"""
        match = re.search(r"line (\d+)", message)
        if match:
            return int(match.group(1))
        return 0
