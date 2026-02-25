"""
任务规划器 (Task Planner)
智能拆解任务，制定执行计划
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SubTask:
    """子任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    estimated_time: int = 30  # 分钟
    actual_time: int = 0
    notes: str = ""
    result: Any = None


@dataclass
class TaskPlan:
    """任务计划"""
    task_id: str
    title: str
    description: str
    subtasks: List[SubTask] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_estimated_time: int = 0
    complexity: str = "medium"


class TaskPlanner:
    """任务规划器"""

    def __init__(self):
        self.plans: Dict[str, TaskPlan] = {}

    def create_plan(self, task_id: str, title: str, description: str,
                    task_type: str = "general", complexity: str = "medium") -> TaskPlan:
        """
        创建任务计划

        Args:
            task_id: 任务ID
            title: 任务标题
            description: 任务描述
            task_type: 任务类型
            complexity: 复杂度

        Returns:
            TaskPlan: 创建的任务计划
        """
        plan = TaskPlan(
            task_id=task_id,
            title=title,
            description=description,
            complexity=complexity
        )

        # 根据任务类型生成子任务
        subtasks = self._generate_subtasks(task_type, description)
        plan.subtasks = subtasks

        # 计算总预估时间
        plan.total_estimated_time = sum(t.estimated_time for t in subtasks)

        self.plans[task_id] = plan
        return plan

    def _generate_subtasks(self, task_type: str, description: str) -> List[SubTask]:
        """根据任务类型生成子任务"""
        subtasks = []

        # 通用子任务模板
        common_templates = [
            SubTask(
                id="task_understand",
                name="理解需求",
                description="理解任务要求和约束条件",
                priority=TaskPriority.CRITICAL,
                estimated_time=10
            ),
            SubTask(
                id="task_analyze",
                name="分析问题",
                description="分析问题本质，确定解决方案",
                priority=TaskPriority.HIGH,
                estimated_time=15
            ),
            SubTask(
                id="task_execute",
                name="执行核心任务",
                description="完成主要工作内容",
                priority=TaskPriority.CRITICAL,
                estimated_time=60
            ),
            SubTask(
                id="task_review",
                name="检查验证",
                description="检查结果是否满足要求",
                priority=TaskPriority.HIGH,
                estimated_time=15
            ),
        ]

        # 编程任务子任务
        programming_templates = [
            SubTask(
                id="prog_design",
                name="设计解决方案",
                description="设计算法和数据结构",
                priority=TaskPriority.HIGH,
                estimated_time=20
            ),
            SubTask(
                id="prog_implement",
                name="编写代码",
                description="实现核心功能代码",
                priority=TaskPriority.CRITICAL,
                estimated_time=45
            ),
            SubTask(
                id="prog_test",
                name="编写测试",
                description="编写单元测试和集成测试",
                priority=TaskPriority.HIGH,
                estimated_time=20
            ),
            SubTask(
                id="prog_debug",
                name="调试优化",
                description="修复bug，优化性能",
                priority=TaskPriority.MEDIUM,
                estimated_time=20
            ),
            SubTask(
                id="prog_document",
                name="编写文档",
                description="编写代码注释和使用文档",
                priority=TaskPriority.MEDIUM,
                estimated_time=15
            ),
        ]

        # 写作任务子任务
        writing_templates = [
            SubTask(
                id="write_research",
                name="资料研究",
                description="收集和整理相关资料",
                priority=TaskPriority.HIGH,
                estimated_time=30
            ),
            SubTask(
                id="write_outline",
                name="设计大纲",
                description="设计文档结构和章节安排",
                priority=TaskPriority.HIGH,
                estimated_time=15
            ),
            SubTask(
                id="write_draft",
                name="撰写初稿",
                description="撰写各章节内容",
                priority=TaskPriority.CRITICAL,
                estimated_time=90
            ),
            SubTask(
                id="write_revise",
                name="修订优化",
                description="修改完善内容，改进表达",
                priority=TaskPriority.HIGH,
                estimated_time=30
            ),
            SubTask(
                id="write_proofread",
                name="校对排版",
                description="检查格式、语法、标点",
                priority=TaskPriority.MEDIUM,
                estimated_time=15
            ),
        ]

        # 根据任务类型选择模板
        if task_type == "programming":
            templates = programming_templates
        elif task_type == "writing":
            templates = writing_templates
        else:
            templates = common_templates

        # 添加依赖关系
        for i, subtask in enumerate(templates):
            if i > 0:
                subtask.dependencies = [templates[i-1].id]

        return templates

    def get_plan(self, task_id: str) -> Optional[TaskPlan]:
        """
        获取任务计划

        Args:
            task_id: 任务ID

        Returns:
            TaskPlan 或 None
        """
        return self.plans.get(task_id)

    def update_subtask_status(self, task_id: str, subtask_id: str,
                              status: TaskStatus, result: Any = None) -> bool:
        """
        更新子任务状态

        Args:
            task_id: 任务ID
            subtask_id: 子任务ID
            status: 新状态
            result: 执行结果

        Returns:
            bool: 是否成功
        """
        plan = self.plans.get(task_id)
        if not plan:
            return False

        for subtask in plan.subtasks:
            if subtask.id == subtask_id:
                subtask.status = status
                if result:
                    subtask.result = result
                return True

        return False

    def get_next_task(self, task_id: str) -> Optional[SubTask]:
        """
        获取下一个待执行的子任务

        Args:
            task_id: 任务ID

        Returns:
            SubTask 或 None
        """
        plan = self.plans.get(task_id)
        if not plan:
            return None

        for subtask in plan.subtasks:
            if subtask.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                deps_completed = all(
                    self._get_subtask_status(plan, dep) == TaskStatus.COMPLETED
                    for dep in subtask.dependencies
                )
                if deps_completed:
                    return subtask

        return None

    def _get_subtask_status(self, plan: TaskPlan, subtask_id: str) -> TaskStatus:
        """获取子任务状态"""
        for subtask in plan.subtasks:
            if subtask.id == subtask_id:
                return subtask.status
        return TaskStatus.PENDING

    def get_progress(self, task_id: str) -> Dict:
        """
        获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            Dict: 进度信息
        """
        plan = self.plans.get(task_id)
        if not plan:
            return {}

        total = len(plan.subtasks)
        completed = sum(1 for t in plan.subtasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in plan.subtasks if t.status == TaskStatus.IN_PROGRESS)

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": total - completed - in_progress,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "estimated_remaining": sum(
                t.estimated_time for t in plan.subtasks
                if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
            ),
        }

    def format_plan_for_display(self, task_id: str) -> str:
        """
        格式化任务计划用于显示

        Args:
            task_id: 任务ID

        Returns:
            str: 格式化的计划字符串
        """
        plan = self.plans.get(task_id)
        if not plan:
            return "任务计划不存在"

        progress = self.get_progress(task_id)

        output = f"""
# 任务计划: {plan.title}

**总预估时间**: {plan.total_estimated_time} 分钟
**复杂度**: {plan.complexity}
**进度**: {progress['completed']}/{progress['total']} ({progress['progress_percent']:.0f}%)

---

## 子任务列表

| # | 任务 | 状态 | 预计时间 | 依赖 |
|---|------|------|----------|------|
"""
        for i, task in enumerate(plan.subtasks, 1):
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.BLOCKED: "🚫",
                TaskStatus.SKIPPED: "⏭️",
            }.get(task.status, "❓")

            deps = ", ".join(task.dependencies) if task.dependencies else "-"
            output += f"| {i} | {task.name} | {status_icon} | {task.estimated_time}分钟 | {deps} |\n"

        return output

    def remove_plan(self, task_id: str) -> bool:
        """
        删除任务计划

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功
        """
        if task_id in self.plans:
            del self.plans[task_id]
            return True
        return False


def main():
    """测试函数"""
    planner = TaskPlanner()

    # 创建计划
    plan = planner.create_plan(
        task_id="test_001",
        title="快速排序实现",
        description="实现快速排序算法并编写测试",
        task_type="programming",
        complexity="medium"
    )

    # 显示计划
    print(planner.format_plan_for_display("test_001"))

    # 获取进度
    print("\n进度:", planner.get_progress("test_001"))

    # 获取下一个任务
    print("\n下一个任务:", planner.get_next_task("test_001"))


if __name__ == "__main__":
    main()
