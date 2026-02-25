"""
代码执行器 (Code Executor)
安全地执行和验证代码
"""

import subprocess
import sys
import os
import tempfile
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    SECURITY_ERROR = "security_error"


@dataclass
class ExecutionResult:
    """执行结果"""
    status: ExecutionStatus
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    test_results: List[Dict] = None


class CodeExecutor:
    """代码执行器"""

    # 不安全的操作列表
    UNSAFE_PATTERNS = [
        "import os",
        "import subprocess",
        "__import__",
        "eval(",
        "exec(",
        "open(",
        "file(",
        "input(",
        "os.system",
        "os.popen",
        "subprocess.call",
        "subprocess.Popen",
    ]

    # 可执行的语言
    SUPPORTED_LANGUAGES = {
        "python": {
            "extension": ".py",
            "command": ["python3", "-c"],
            "shebang": "#!/usr/bin/env python3"
        },
        "python3": {
            "extension": ".py",
            "command": ["python3", "-c"],
            "shebang": "#!/usr/bin/env python3"
        },
    }

    def __init__(self, timeout: int = 30, max_output_size: int = 10000):
        """
        初始化代码执行器

        Args:
            timeout: 超时时间（秒）
            max_output_size: 最大输出大小（字节）
        """
        self.timeout = timeout
        self.max_output_size = max_output_size

    def execute(self, code: str, language: str = "python",
                test_cases: List[Dict] = None) -> ExecutionResult:
        """
        执行代码

        Args:
            code: 要执行的代码
            language: 编程语言
            test_cases: 测试用例列表

        Returns:
            ExecutionResult: 执行结果
        """
        import time
        start_time = time.time()

        # 安全检查
        if not self._is_safe(code):
            return ExecutionResult(
                status=ExecutionStatus.SECURITY_ERROR,
                stdout="",
                stderr="代码包含不安全的操作",
                return_code=-1,
                execution_time=time.time() - start_time,
                test_results=[]
            )

        # 获取语言配置
        lang_config = self.SUPPORTED_LANGUAGES.get(language.lower())
        if not lang_config:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stdout="",
                stderr=f不支持的语言: {language}",
                return_code=-1,
                execution_time=time.time() - start_time,
                test_results=[]
            )

        # 处理代码
        if language.lower() in ["python", "python3"]:
            result = self._execute_python(code, test_cases)

        result.execution_time = time.time() - start_time
        return result

    def _is_safe(self, code: str) -> bool:
        """
        检查代码是否安全

        Args:
            code: 要检查的代码

        Returns:
            bool: 是否安全
        """
        code_lower = code.lower()

        for pattern in self.UNSAFE_PATTERNS:
            if pattern.lower() in code_lower:
                return False

        return True

    def _execute_python(self, code: str,
                        test_cases: List[Dict] = None) -> ExecutionResult:
        """执行Python代码"""
        import time

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                          delete=False) as f:
            # 添加测试框架代码
            test_framework = """
import sys

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def assert_equal(self, actual, expected, message=""):
        if actual == expected:
            self.passed += 1
            self.results.append({"status": "pass", "message": message})
        else:
            self.failed += 1
            self.results.append({
                "status": "fail",
                "message": f"{message}: expected {expected}, got {actual}"
            })

test_result = TestResult()

"""
            # 添加用户代码
            f.write(test_framework)
            f.write(code)

            # 添加测试执行代码
            if test_cases:
                f.write("\n\n# 测试用例执行\n")
                for i, tc in enumerate(test_cases, 1):
                    input_code = tc.get('input', '')
                    expected = tc.get('expected', '')
                    description = tc.get('description', f'Test {i}')

                    f.write(f'\n# {description}\n')
                    f.write(f'test_result.assert_equal(\n')
                    f.write(f'    ({input_code}),\n')
                    f.write(f'    {repr(expected)},\n')
                    f.write(f'    "{description}"\n')
                    f.write(f')\n')

            # 打印测试结果
            f.write("\n\n# 输出测试结果\n")
            f.write('print(json.dumps({\n')
            f.write('    "passed": test_result.passed,\n')
            f.write('    "failed": test_result.failed,\n')
            f.write('    "results": test_result.results\n')
            f.write('}))')

            temp_file = f.name

        try:
            # 执行代码
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PYTHONPATH": ""}
            )

            # 解析测试结果
            test_results = []
            try:
                if result.stdout.strip():
                    output = json.loads(result.stdout.strip().split('\n')[-1])
                    test_results = output.get('results', [])
            except json.JSONDecodeError:
                pass

            # 确定状态
            if result.returncode == 0:
                status = ExecutionStatus.SUCCESS
            else:
                status = ExecutionStatus.ERROR

            # 截断输出
            stdout = result.stdout[:self.max_output_size]
            stderr = result.stderr[:self.max_output_size]

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                return_code=result.returncode,
                execution_time=0,
                test_results=test_results
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                stdout="",
                stderr=f"执行超时（{self.timeout}秒）",
                return_code=-1,
                execution_time=self.timeout,
                test_results=[]
            )

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass

    def run_test_suite(self, code: str, test_cases: List[Dict],
                       language: str = "python") -> Dict:
        """
        运行测试套件

        Args:
            code: 要测试的代码
            test_cases: 测试用例列表
            language: 编程语言

        Returns:
            Dict: 测试结果汇总
        """
        result = self.execute(code, language, test_cases)

        # 汇总结果
        summary = {
            "status": result.status.value,
            "total": len(test_cases) if test_cases else 0,
            "passed": 0,
            "failed": 0,
            "execution_time": result.execution_time,
            "details": []
        }

        # 计算通过/失败数
        if result.test_results:
            summary["passed"] = sum(1 for r in result.test_results if r["status"] == "pass")
            summary["failed"] = sum(1 for r in result.test_results if r["status"] == "fail")
            summary["details"] = result.test_results
        elif result.status == ExecutionStatus.SUCCESS:
            summary["passed"] = summary["total"]
            summary["failed"] = 0
            summary["details"] = [{"status": "pass", "message": "代码执行成功"}]
        else:
            summary["failed"] = summary["total"]
            summary["details"] = [{"status": "fail", "message": result.stderr}]

        return summary

    def generate_test_code(self, code: str, language: str = "python") -> str:
        """
        为代码生成测试框架

        Args:
            code: 原始代码
            language: 编程语言

        Returns:
            str: 包含测试框架的代码
        """
        if language.lower() in ["python", "python3"]:
            return self._generate_python_test_framework(code)
        return code

    def _generate_python_test_framework(self, code: str) -> str:
        """生成Python测试框架"""
        test_framework = '''
import unittest
import json

class TestSolution(unittest.TestCase):
    """测试用例"""

    def setUp(self):
        """设置测试环境"""
        pass

    def test_example(self):
        """示例测试"""
        # TODO: 添加测试用例
        pass

if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
'''
        return code + "\n\n" + test_framework


def main():
    """测试函数"""
    executor = CodeExecutor(timeout=10)

    # 测试代码
    test_code = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
'''

    test_cases = [
        {"input": "add(1, 2)", "expected": 3, "description": "正数加法"},
        {"input": "add(-1, 1)", "expected": 0, "description": "正负数加法"},
        {"input": "subtract(5, 3)", "expected": 2, "description": "减法测试"},
    ]

    # 执行测试
    result = executor.run_test_suite(test_code, test_cases)
    print("测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
