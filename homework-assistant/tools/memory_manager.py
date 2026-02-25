"""
记忆管理器 (Memory Manager)
管理短期对话记忆和长期任务上下文
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import hashlib


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    category: str = "general"
    importance: int = 1  # 1-5, 越高越重要


@dataclass
class ConversationTurn:
    """对话轮次"""
    turn_id: int
    user_input: str
    assistant_response: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    task_context: Dict = field(default_factory=dict)


class MemoryManager:
    """记忆管理器"""

    def __init__(self, memory_dir: str = "../memory"):
        self.memory_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/memory"

        # 确保目录存在
        os.makedirs(self.memory_dir, exist_ok=True)

        self.conversation_history_file = os.path.join(self.memory_dir, "conversation_history.json")
        self.task_context_file = os.path.join(self.memory_dir, "task_context.json")

        # 初始化存储
        self.conversation_history: List[ConversationTurn] = []
        self.task_context: Dict[str, Any] = {}

        # 加载已有记忆
        self._load_memory()

    def _load_memory(self):
        """加载已有记忆"""
        # 加载对话历史
        if os.path.exists(self.conversation_history_file):
            try:
                with open(self.conversation_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = [
                        ConversationTurn(**turn) for turn in data
                    ]
            except Exception as e:
                print(f"加载对话历史失败: {e}")
                self.conversation_history = []

        # 加载任务上下文
        if os.path.exists(self.task_context_file):
            try:
                with open(self.task_context_file, 'r', encoding='utf-8') as f:
                    self.task_context = json.load(f)
            except Exception as e:
                print(f"加载任务上下文失败: {e}")
                self.task_context = {}

    def _save_memory(self):
        """保存记忆到文件"""
        # 保存对话历史
        try:
            with open(self.conversation_history_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [asdict(turn) for turn in self.conversation_history],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            print(f"保存对话历史失败: {e}")

        # 保存任务上下文
        try:
            with open(self.task_context_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_context, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务上下文失败: {e}")

    def add_turn(self, user_input: str, assistant_response: str, task_context: Dict = None):
        """
        添加一轮对话

        Args:
            user_input: 用户输入
            assistant_response: 助手回复
            task_context: 任务上下文
        """
        turn = ConversationTurn(
            turn_id=len(self.conversation_history),
            user_input=user_input,
            assistant_response=assistant_response,
            task_context=task_context or {}
        )

        self.conversation_history.append(turn)

        # 只保留最近20轮对话
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        self._save_memory()

    def get_recent_context(self, n: int = 5) -> List[ConversationTurn]:
        """
        获取最近n轮对话的上下文

        Args:
            n: 轮次数量

        Returns:
            List[ConversationTurn]: 对话轮次列表
        """
        return self.conversation_history[-n:]

    def update_context(self, context: Dict):
        """
        更新任务上下文

        Args:
            context: 要更新的上下文内容
        """
        self.task_context.update(context)
        self._save_memory()

    def get_context(self, key: str = None) -> Any:
        """
        获取任务上下文

        Args:
            key: 可选的键名

        Returns:
            上下文值或整个上下文
        """
        if key:
            return self.task_context.get(key)
        return self.task_context

    def save_task_result(self, result: Dict):
        """
        保存任务结果到长期记忆

        Args:
            result: 任务结果
        """
        task_id = result.get("task", "unknown")
        timestamp = result.get("timestamp", datetime.now().isoformat())

        memory_key = f"task_{hashlib.md5(task_id.encode()).hexdigest()[:8]}"

        self.task_context[memory_key] = {
            "task": task_id,
            "result_summary": str(result.get("result", ""))[:500],
            "timestamp": timestamp,
        }

        self._save_memory()

    def remember_concept(self, concept: str, details: Dict, category: str = "concept"):
        """
        记忆一个概念

        Args:
            concept: 概念名称
            details: 概念详情
            category: 分类
        """
        key = f"concept_{hashlib.md5(concept.encode()).hexdigest()[:8]}"

        entry = MemoryEntry(
            key=key,
            value={"concept": concept, "details": details},
            category=category,
            importance=3
        )

        self.task_context[key] = asdict(entry)
        self._save_memory()

    def recall_concepts(self, category: str = None) -> List[Dict]:
        """
        回忆概念

        Args:
            category: 可选的分类筛选

        Returns:
            List[Dict]: 概念列表
        """
        concepts = []

        for key, value in self.task_context.items():
            if key.startswith("concept_"):
                if category is None or value.get("category") == category:
                    concepts.append(value)

        return concepts

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self._save_memory()

    def clear_all_memory(self):
        """清空所有记忆"""
        self.conversation_history = []
        self.task_context = {}
        self._save_memory()

    def get_memory_summary(self) -> Dict:
        """
        获取记忆摘要

        Returns:
            Dict: 记忆摘要信息
        """
        return {
            "conversation_turns": len(self.conversation_history),
            "context_keys": len(self.task_context),
            "concepts_stored": len([k for k in self.task_context.keys() if k.startswith("concept_")]),
            "tasks_completed": len([k for k in self.task_context.keys() if k.startswith("task_")]),
        }

    def format_context_for_prompt(self, max_turns: int = 3) -> str:
        """
        格式化上下文供提示词使用

        Args:
            max_turns: 包含的最大对话轮数

        Returns:
            str: 格式化的上下文字符串
        """
        context_parts = []

        # 添加任务上下文
        if self.task_context:
            context_parts.append("【任务上下文】")
            for key, value in self.task_context.items():
                if key.startswith(("task_", "concept_")):
                    context_parts.append(f"- {value}")

        # 添加最近对话
        recent_turns = self.get_recent_context(max_turns)
        if recent_turns:
            context_parts.append("\n【最近对话】")
            for turn in recent_turns:
                context_parts.append(f"用户: {turn.user_input[:100]}...")
                context_parts.append(f"助手: {turn.assistant_response[:100]}...")

        return "\n".join(context_parts)


def main():
    """测试函数"""
    memory = MemoryManager()

    # 添加测试对话
    memory.add_turn(
        "帮我完成快速排序作业",
        "好的，我来帮你分析并完成快速排序作业。",
        {"task": "quick_sort"}
    )

    # 获取摘要
    print("记忆摘要:", memory.get_memory_summary())

    # 格式化上下文
    print("\n上下文:", memory.format_context_for_prompt())


if __name__ == "__main__":
    main()
