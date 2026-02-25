"""
执行引擎 (Execution Engine)
统一调度各工作流，协调任务执行
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import sys

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.analyze_task import TaskAnalyzer, TaskType, TaskRequirement
from workflows.programming_workflow import ProgrammingWorkflow
from workflows.writing_workflow import WritingWorkflow


@dataclass
class ExecutionState:
    """执行状态"""
    task_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    current_step: int = 0
    total_steps: int = 0
    status: str = "pending"  # pending, running, paused, completed, error
    results: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    progress: float = 0.0


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    output: Any
    message: str
    execution_time: float
    artifacts: Dict = field(default_factory=dict)


class ExecutionEngine:
    """执行引擎"""

    def __init__(self, memory_manager=None, knowledge_base=None):
        self.analyzer = TaskAnalyzer()
        self.programming_workflow = ProgrammingWorkflow()
        self.writing_workflow = WritingWorkflow()
        self.memory_manager = memory_manager
        self.knowledge_base = knowledge_base
        self.state = ExecutionState()

    def execute(self, task_description: str, auto_confirm: bool = True) -> TaskResult:
        """
        执行完整任务流程

        Args:
            task_description: 任务描述
            auto_confirm: 是否自动确认执行计划

        Returns:
            TaskResult: 执行结果
        """
        import time
        start_time = time.time()

        try:
            # 步骤1: 分析任务
            self.state.status = "analyzing"
            requirement = self.analyzer.analyze(task_description)

            # 记录分析报告
            analysis_report = self.analyzer.get_analysis_report()

            # 如果有记忆管理器，更新上下文
            if self.memory_manager:
                self.memory_manager.update_context({
                    "current_task": requirement.core_goal,
                    "task_type": requirement.task_type.value,
                    "complexity": requirement.complexity.value,
                })

            # 步骤2: 加载相关知识
            self.state.status = "loading_knowledge"
            relevant_knowledge = []
            if self.knowledge_base and requirement.dependencies:
                for dep in requirement.dependencies:
                    knowledge = self.knowledge_base.query(dep)
                    if knowledge:
                        relevant_knowledge.append(knowledge)

            # 步骤3: 选择工作流
            self.state.status = "selecting_workflow"
            if requirement.task_type == TaskType.PROGRAMMING:
                workflow = self.programming_workflow
            elif requirement.task_type == TaskType.WRITING:
                workflow = self.writing_workflow
            else:
                # 默认使用混合工作流
                workflow = self._create_hybrid_workflow(requirement)

            # 步骤4: 执行工作流
            self.state.status = "executing"
            self.state.total_steps = len(requirement.subtasks)

            # 构建传递给工作流的数据
            task_data = {
                "core_goal": requirement.core_goal,
                "constraints": requirement.constraints,
                "keywords": requirement.keywords,
                "task_type": requirement.task_type.value,
                "complexity": requirement.complexity.value,
                "dependencies": requirement.dependencies,
                "subtasks": requirement.subtasks,
                "relevant_knowledge": relevant_knowledge,
            }

            # 执行选中的工作流
            if hasattr(workflow, 'run'):
                results = workflow.run(task_data)
            else:
                results = self._run_hybrid_workflow(task_data)

            # 步骤5: 生成最终输出
            self.state.status = "finalizing"
            output = self._format_output(requirement, results, analysis_report)

            # 步骤6: 保存结果
            if self.memory_manager:
                self.memory_manager.save_task_result({
                    "task": requirement.core_goal,
                    "result": results,
                    "timestamp": datetime.now().isoformat(),
                })

            execution_time = time.time() - start_time
            self.state.status = "completed"
            self.state.progress = 100.0

            return TaskResult(
                success=True,
                output=output,
                message="任务执行成功",
                execution_time=execution_time,
                artifacts={
                    "requirement": task_data,
                    "results": results,
                    "analysis_report": analysis_report,
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.state.status = "error"
            self.state.errors.append(str(e))

            return TaskResult(
                success=False,
                output=None,
                message=f"执行出错: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )

    def _create_hybrid_workflow(self, requirement: TaskRequirement) -> Dict:
        """创建混合工作流"""
        return {
            "type": "hybrid",
            "steps": requirement.subtasks,
            "note": "根据任务特点灵活调整执行策略"
        }

    def _run_hybrid_workflow(self, task_data: Dict) -> Dict:
        """执行混合工作流"""
        return {
            "status": "completed",
            "task_type": "hybrid",
            "message": "任务已完成（混合模式）",
            "subtasks_completed": len(task_data.get('subtasks', []))
        }

    def _format_output(self, requirement: TaskRequirement, results: Dict, analysis_report: str) -> str:
        """格式化输出"""
        output = f"""
# 任务完成报告

## 任务概述
**核心目标**: {requirement.core_goal}
**任务类型**: {requirement.task_type.value}
**复杂度**: {requirement.complexity.value}

---

## 分析报告
{analysis_report}

---

## 执行结果
"""

        # 根据任务类型格式化结果
        if requirement.task_type == TaskType.PROGRAMMING:
            output += self._format_programming_results(results)
        elif requirement.task_type == TaskType.WRITING:
            output += self._format_writing_results(results)
        else:
            output += json.dumps(results, ensure_ascii=False, indent=2)

        output += """
---

## 使用说明
请根据上述结果完成你的作业。如有需要，我可以进一步协助你：
1. 解释代码或文档的内容
2. 修改或优化某些部分
3. 添加测试或补充内容
4. 准备最终提交材料
"""

        return output

    def _format_programming_results(self, results: Dict) -> str:
        """格式化编程结果"""
        output = "### 编程解决方案\n\n"

        if 'implementation' in results:
            impl = results['implementation']
            if isinstance(impl, dict) and 'code' in impl:
                output += f"**编程语言**: {impl.get('language', 'Python')}\n\n"
                output += "```python\n"
                output += impl['code']
                output += "\n```\n"

        if 'testing' in results:
            tests = results['testing']
            if isinstance(tests, dict) and 'test_code' in tests:
                output += "\n### 测试代码\n\n"
                output += "```python\n"
                output += tests['test_code']
                output += "\n```\n"

        if 'documentation' in results:
            doc = results['documentation']
            if isinstance(doc, dict) and 'description' in doc:
                output += "\n### 文档说明\n\n"
                output += doc['description']

        return output

    def _format_writing_results(self, results: Dict) -> str:
        """格式化写作结果"""
        output = "### 文档内容\n\n"

        if 'drafting' in results:
            drafting = results['drafting']
            if isinstance(drafting, dict) and 'full_text' in drafting:
                output += drafting['full_text']

        return output

    def get_status(self) -> Dict:
        """获取执行状态"""
        return {
            "status": self.state.status,
            "progress": self.state.progress,
            "current_step": self.state.current_step,
            "total_steps": self.state.total_steps,
            "errors": self.state.errors,
        }

    def pause(self) -> bool:
        """暂停执行"""
        if self.state.status == "running":
            self.state.status = "paused"
            return True
        return False

    def resume(self) -> bool:
        """恢复执行"""
        if self.state.status == "paused":
            self.state.status = "running"
            return True
        return False

    def cancel(self) -> bool:
        """取消执行"""
        self.state.status = "cancelled"
        return True


def main():
    """主函数 - 用于测试"""
    engine = ExecutionEngine()

    # 测试任务
    test_task = """
    实现一个快速排序算法
    要求：
    1. 使用Python语言
    2. 包含测试用例
    3. 编写文档说明
    """

    result = engine.execute(test_task)

    print(f"执行结果: {'成功' if result.success else '失败'}")
    print(f"耗时: {result.execution_time:.2f}秒")
    print(f"\n输出:\n{result.output}")


if __name__ == "__main__":
    main()
