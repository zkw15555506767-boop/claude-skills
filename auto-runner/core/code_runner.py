"""代碼運行器"""

import asyncio
import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class RunStatus(Enum):
    """運行狀態"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RUNNING = "running"


@dataclass
class RunResult:
    """運行結果"""
    status: RunStatus
    command: str
    stdout: str
    stderr: str
    return_code: int
    duration: float


class CodeRunner:
    """運行代碼"""

    def __init__(self, project_path: str):
        self.project_path = project_path

    async def run(
        self,
        command: str,
        timeout: int = 120,
        env: dict = None,
    ) -> RunResult:
        """運行命令"""
        import time

        start_time = time.time()

        success, output = await self._execute(
            command,
            timeout,
            env,
        )

        duration = time.time() - start_time

        # 解析輸出
        lines = output.split("\n")
        stdout_lines = []
        stderr_lines = []
        in_stderr = False

        for line in lines:
            if "stderr:" in line.lower():
                in_stderr = True
                continue
            if in_stderr:
                stderr_lines.append(line)
            else:
                stdout_lines.append(line)

        return_code = 0 if success else 1

        # 判斷狀態
        if success:
            status = RunStatus.SUCCESS
        elif "timeout" in output.lower():
            status = RunStatus.TIMEOUT
        else:
            status = RunStatus.FAILED

        return RunResult(
            status=status,
            command=command,
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            return_code=return_code,
            duration=duration,
        )

    async def run_interactive(self, command: str, timeout: int = 60):
        """交互式運行（用於需要輸入的場景）"""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_path,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )
            return True, stdout.decode() + stderr.decode()
        except asyncio.TimeoutExpired:
            proc.kill()
            return False, "命令超時"

    async def detect_entry_point(self, language: str) -> Optional[str]:
        """檢測入口點"""
        from core.language_detector import LanguageDetector

        detector = LanguageDetector()
        return detector.suggest_entry_point(self.project_path)

    async def _execute(
        self,
        command: str,
        timeout: int,
        env: dict = None,
    ) -> tuple[bool, str]:
        """執行命令"""
        from utils.common import run_command as util_run

        return await util_run(
            cmd=command,
            cwd=self.project_path,
            timeout=timeout,
            env=env,
        )

    async def test_basic(self) -> RunResult:
        """基本測試運行"""
        # 嘗試運行入口文件
        from core.language_detector import LanguageDetector

        detector = LanguageDetector()
        await detector.detect(self.project_path)

        if detector.language:
            entry = detector.suggest_entry_point(self.project_path)
            if entry:
                command = detector.get_run_command(entry)
                return await self.run(command)

        return RunResult(
            status=RunStatus.FAILED,
            command="",
            stdout="",
            stderr="無法找到入口文件",
            return_code=1,
            duration=0,
        )
