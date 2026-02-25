"""通用工具函数"""

import subprocess
import os
import shutil
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_command(
    cmd: str,
    cwd: str = None,
    timeout: int = 300,
    env: dict = None,
    capture: bool = True,
) -> tuple[bool, str]:
    """执行命令并返回结果"""
    try:
        result = await asyncio.wait_for(
            asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE if capture else None,
                stderr=asyncio.subprocess.PIPE if capture else None,
                cwd=cwd,
                env=env or os.environ.copy(),
            ),
            timeout=timeout,
        )
        stdout, stderr = await result.communicate()
        output = (stdout.decode() + stderr.decode()).strip()
        return result.returncode == 0, output
    except asyncio.TimeoutExpired:
        return False, f"命令超时 ({timeout}s): {cmd}"
    except Exception as e:
        return False, f"执行错误: {str(e)}"


async def safe_mkdir(path: str) -> bool:
    """安全创建目录"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {e}")
        return False


async def cleanup_temp(path: str) -> bool:
    """清理临时目录"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        logger.error(f"清理临时目录失败: {e}")
        return False


def extract_file_content(path: str, max_lines: int = 100) -> str:
    """提取文件内容（限制行数）"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[:max_lines]
            return "".join(lines)
    except Exception:
        return ""


def log_step(step: str, message: str):
    """记录步骤日志"""
    logger.info(f"[{step}] {message}")


def log_info(message: str):
    """记录信息日志"""
    logger.info(message)
