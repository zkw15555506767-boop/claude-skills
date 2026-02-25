"""
编程工作流 (Programming Workflow)
处理编程类作业的完整流程
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class CodingPhase(Enum):
    REQUIREMENT = "requirement"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    COMPLETE = "complete"


@dataclass
class CodeSolution:
    """代码解决方案"""
    language: str = ""
    code: str = ""
    test_cases: List[Dict] = field(default_factory=list)
    test_results: List[Dict] = field(default_factory=list)
    documentation: str = ""
    issues: List[str] = field(default_factory=list)


class ProgrammingWorkflow:
    """编程任务工作流"""

    def __init__(self):
        self.current_phase = CodingPhase.REQUIREMENT
        self.solution = CodeSolution()
        self.design_notes = ""
        self.implementation_notes = ""

    def run(self, task_requirement: Dict) -> Dict:
        """
        执行完整的编程任务工作流

        Args:
            task_requirement: 任务需求字典

        Returns:
            Dict: 执行结果
        """
        results = {}

        # 阶段1: 理解需求
        results['requirement_analysis'] = self._analyze_requirement(task_requirement)

        # 阶段2: 设计解决方案
        results['design'] = self._design_solution(task_requirement)

        # 阶段3: 编写代码
        results['implementation'] = self._implement(task_requirement)

        # 阶段4: 编写测试
        results['testing'] = self._write_tests(task_requirement)

        # 阶段5: 调试优化
        results['debugging'] = self._debug_and_optimize(task_requirement)

        # 阶段6: 编写文档
        results['documentation'] = self._write_documentation(task_requirement)

        self.current_phase = CodingPhase.COMPLETE

        return results

    def _analyze_requirement(self, requirement: Dict) -> Dict:
        """分析编程需求"""
        analysis = {
            "inputs": self._extract_inputs(requirement),
            "outputs": self._extract_outputs(requirement),
            "algorithms_needed": self._suggest_algorithms(requirement),
            "data_structures_needed": self._suggest_data_structures(requirement),
            "edge_cases": self._identify_edge_cases(requirement),
        }
        return analysis

    def _extract_inputs(self, requirement: Dict) -> List[Dict]:
        """提取输入规格"""
        description = requirement.get('core_goal', '')
        inputs = []

        # 常见的输入模式
        input_patterns = [
            (r'输入[：:]\s*(.+)', 'specified'),
            (r'给定[：:]\s*(.+)', 'specified'),
            (r'参数[：:]\s*(.+)', 'specified'),
        ]

        for pattern, ptype in input_patterns:
            import re
            matches = re.findall(pattern, description)
            for match in matches:
                inputs.append({"type": ptype, "description": match})

        if not inputs:
            inputs = [{"type": "unknown", "description": "需要进一步确认输入格式"}]

        return inputs

    def _extract_outputs(self, requirement: Dict) -> List[Dict]:
        """提取输出规格"""
        description = requirement.get('core_goal', '')
        outputs = []

        import re
        output_patterns = [
            (r'输出[：:]\s*(.+)', 'specified'),
            (r'返回[：:]\s*(.+)', 'specified'),
            (r'结果[：:]\s*(.+)', 'specified'),
        ]

        for pattern, ptype in output_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                outputs.append({"type": ptype, "description": match})

        if not outputs:
            outputs = [{"type": "unknown", "description": "需要进一步确认输出格式"}]

        return outputs

    def _suggest_algorithms(self, requirement: Dict) -> List[str]:
        """建议需要的算法"""
        description = requirement.get('core_goal', '').lower()
        algorithms = []

        # 根据关键词推荐算法
        algo_keywords = {
            "排序": ["快速排序", "归并排序", "堆排序"],
            "搜索": ["二分搜索", "广度优先搜索", "深度优先搜索"],
            "最短路径": ["Dijkstra", "Floyd-Warshall", "Bellman-Ford"],
            "动态规划": ["背包问题", "最长公共子序列", "编辑距离"],
            "图遍历": ["BFS", "DFS", "拓扑排序"],
            "树": ["二叉搜索树", "平衡树", "红黑树"],
            "字符串": ["KMP", "正则匹配", "字符串哈希"],
            "递归": ["分治", "回溯"],
        }

        for algo_type, algos in algo_keywords.items():
            if algo_type.lower() in description:
                algorithms.extend(algos)

        return list(set(algorithms))

    def _suggest_data_structures(self, requirement: Dict) -> List[str]:
        """建议需要的数据结构"""
        description = requirement.get('core_goal', '').lower()
        structures = []

        struct_keywords = {
            "数组": ["数组", "list", "array"],
            "链表": ["链表", "linked list"],
            "栈": ["栈", "stack"],
            "队列": ["队列", "queue"],
            "哈希表": ["哈希", "hash", "字典", "map"],
            "堆": ["堆", "heap", "优先队列"],
            "图": ["图", "graph", "节点", "边"],
            "树": ["树", "tree", "节点"],
        }

        for struct, keywords in struct_keywords.items():
            if any(kw in description for kw in keywords):
                structures.append(struct)

        return structures

    def _identify_edge_cases(self, requirement: Dict) -> List[str]:
        """识别边界情况"""
        edge_cases = [
            "空输入处理",
            "边界值处理",
            "异常输入处理",
        ]

        # 根据具体需求添加
        description = requirement.get('core_goal', '')

        if "最大" in description or "最小" in description:
            edge_cases.append("最大值/最小值边界")

        if "重复" in description:
            edge_cases.append("重复元素处理")

        if "排序" in description:
            edge_cases.extend([
                "已排序数组",
                "逆序数组",
                "全相同元素数组"
            ])

        return edge_cases

    def _design_solution(self, requirement: Dict) -> Dict:
        """设计解决方案"""
        design = {
            "approach": "",  # 解决方案概述
            "algorithm_choice": "",  # 选择的算法
            "complexity_analysis": {},  # 复杂度分析
            "class_design": [],  # 类设计
            "function_design": [],  # 函数设计
        }

        # 根据任务类型生成设计方案
        task_type = requirement.get('task_type', 'unknown')

        design["approach"] = self._generate_approach_description(requirement)
        design["complexity_analysis"] = {
            "time": self._estimate_time_complexity(requirement),
            "space": self._estimate_space_complexity(requirement)
        }

        self.design_notes = json.dumps(design, ensure_ascii=False, indent=2)
        return design

    def _generate_approach_description(self, requirement: Dict) -> str:
        """生成解决方案描述"""
        approach = f"""
针对任务「{requirement.get('core_goal', '未知目标')}」的设计方案：

1. 需求理解 - 明确输入输出规格
2. 算法选择 - 根据问题特性选择最优算法
3. 结构设计 - 设计清晰的模块和接口
4. 逐步实现 - 先核心后外围
5. 测试验证 - 确保正确性

具体实施将根据实际需求进行调整。
"""
        return approach.strip()

    def _estimate_time_complexity(self, requirement: Dict) -> str:
        """估算时间复杂度"""
        description = requirement.get('core_goal', '').lower()
        if "排序" in description:
            return "O(n log n)"
        elif "搜索" in description:
            return "O(log n) 或 O(n)"
        elif "遍历" in description:
            return "O(n)"
        else:
            return "待分析"

    def _estimate_space_complexity(self, requirement: Dict) -> str:
        """估算空间复杂度"""
        return "O(n) - 需要根据具体实现确定"

    def _implement(self, requirement: Dict) -> Dict:
        """实现代码"""
        implementation = {
            "language": self._detect_language(requirement),
            "code": "",  # 这里会填充实际代码
            "functions": [],
            "classes": [],
        }

        # 生成代码框架
        implementation["code"] = self._generate_code_scaffold(implementation["language"], requirement)

        self.implementation_notes = json.dumps(implementation, ensure_ascii=False, indent=2)
        return implementation

    def _detect_language(self, requirement: Dict) -> str:
        """检测编程语言"""
        description = requirement.get('constraints', [])
        full_text = str(description)

        languages = {
            "Python": ["python", "Python", "py"],
            "Java": ["java", "Java"],
            "JavaScript": ["javascript", "js", "node"],
            "C++": ["c++", "cpp", "C++"],
        }

        for lang, keywords in languages.items():
            if any(kw in full_text for kw in keywords):
                return lang

        return "Python"  # 默认使用Python

    def _generate_code_scaffold(self, language: str, requirement: Dict) -> str:
        """生成代码框架"""
        if language == "Python":
            scaffold = f'''
"""
{requirement.get('core_goal', '任务目标')}
"""

def main():
    """主函数"""
    # TODO: 实现主逻辑
    pass


class Solution:
    """解决方案类"""

    def __init__(self):
        """初始化"""
        pass

    def solve(self, input_data):
        """
        解决问题

        Args:
            input_data: 输入数据

        Returns:
            处理结果
        """
        # TODO: 实现求解逻辑
        pass


if __name__ == "__main__":
    main()
'''
        else:
            scaffold = f"// {language} 代码框架\n// 待实现"

        return scaffold

    def _write_tests(self, requirement: Dict) -> Dict:
        """编写测试用例"""
        tests = {
            "test_cases": [
                {"input": "", "expected": "", "description": "基础测试"},
                {"input": "", "expected": "", "description": "边界测试"},
                {"input": "", "expected": "", "description": "异常测试"},
            ],
            "test_code": "",
        }

        # 生成测试代码
        tests["test_code"] = self._generate_test_code(
            self.solution.language if self.solution.language else "Python"
        )

        return tests

    def _generate_test_code(self, language: str) -> str:
        """生成测试代码"""
        if language == "Python":
            test_code = '''
import unittest

class TestSolution(unittest.TestCase):
    """测试用例"""

    def setUp(self):
        """设置测试环境"""
        self.solution = Solution()

    def test_basic(self):
        """基础测试"""
        pass

    def test_edge_cases(self):
        """边界测试"""
        pass

    def test_errors(self):
        """异常测试"""
        pass

if __name__ == "__main__":
    unittest.main()
'''
        else:
            test_code = f"// {language} 测试代码框架"

        return test_code

    def _debug_and_optimize(self, requirement: Dict) -> Dict:
        """调试和优化"""
        return {
            "issues_found": [],
            "optimizations": [],
            "performance_notes": "",
        }

    def _write_documentation(self, requirement: Dict) -> Dict:
        """编写文档"""
        doc = {
            "description": f"""
# {requirement.get('core_goal', '项目文档')}

## 功能说明
TODO: 描述项目功能

## 使用方法
TODO: 说明使用方法

## 输入输出格式
TODO: 说明输入输出规格

## 注意事项
TODO: 列出注意事项
""",
            "api_docs": [],
            "examples": [],
        }

        self.solution.documentation = doc["description"]
        return doc

    def get_solution(self) -> CodeSolution:
        """获取解决方案"""
        return self.solution
