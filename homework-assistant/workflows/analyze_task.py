"""
任务分析器 (Task Analyzer)
负责解析作业要求，提取关键信息，判断任务类型和复杂度
"""

import re
from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass


class TaskType(Enum):
    PROGRAMMING = "programming"
    WRITING = "writing"
    UNKNOWN = "unknown"


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class TaskRequirement:
    """任务要求结构"""
    core_goal: str           # 核心目标
    constraints: List[str]   # 约束条件
    keywords: List[str]      # 关键词
    task_type: TaskType      # 任务类型
    complexity: TaskComplexity  # 复杂度
    dependencies: List[str]  # 依赖知识
    subtasks: List[str]      # 子任务列表


class TaskAnalyzer:
    """任务分析器"""

    # 编程任务关键词
    PROGRAMMING_KEYWORDS = [
        "实现", "编写", "开发", "编程", "代码", "算法",
        "function", "class", "program", "implement", "code",
        "algorithm", "debug", "refactor", "api", "interface"
    ]

    # 写作任务关键词
    WRITING_KEYWORDS = [
        "论文", "报告", "文档", "分析", "研究", "综述",
        "essay", "report", "paper", "document", "analysis",
        "research", "review", "proposal", "proposal"
    ]

    # 复杂度指示词
    COMPLEXITY_HIGH = ["复杂", "综合", "完整系统", "完整项目", "大型"]
    COMPLEXITY_LOW = ["简单", "基础", "入门", "单个", "简单实现"]

    def __init__(self):
        self.requirement = None

    def analyze(self, task_description: str) -> TaskRequirement:
        """
        分析任务描述，提取关键信息

        Args:
            task_description: 任务描述文本

        Returns:
            TaskRequirement: 解析后的任务要求
        """
        # 提取核心目标
        core_goal = self._extract_core_goal(task_description)

        # 提取约束条件
        constraints = self._extract_constraints(task_description)

        # 提取关键词
        keywords = self._extract_keywords(task_description)

        # 判断任务类型
        task_type = self._determine_task_type(keywords)

        # 判断复杂度
        complexity = self._determine_complexity(task_description)

        # 识别依赖知识
        dependencies = self._identify_dependencies(task_description)

        # 初步拆分子任务
        subtasks = self._generate_subtasks(task_description, task_type)

        self.requirement = TaskRequirement(
            core_goal=core_goal,
            constraints=constraints,
            keywords=keywords,
            task_type=task_type,
            complexity=complexity,
            dependencies=dependencies,
            subtasks=subtasks
        )

        return self.requirement

    def _extract_core_goal(self, description: str) -> str:
        """提取核心目标"""
        # 移除常见的开头语
        patterns = [
            r"请帮我完成.+?\n",
            r"作业要求[：:]\s*",
            r"题目[：:]\s*",
            r"要求[：:]\s*"
        ]
        cleaned = description
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # 取第一句或前100字作为核心目标
        sentences = re.split(r'[。\n]', cleaned)
        core_goal = sentences[0].strip() if sentences else cleaned[:100]

        return core_goal

    def _extract_constraints(self, description: str) -> List[str]:
        """提取约束条件"""
        constraints = []

        # 截止日期
        deadline_match = re.search(
            r"截止[日期时间]|deadline|due\s*date[:\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            description, re.IGNORECASE
        )
        if deadline_match:
            constraints.append(f"截止日期: {deadline_match.group(1)}")

        # 字数要求
        word_count = re.search(r"(\d+)\s*(字|词|words?)", description, re.IGNORECASE)
        if word_count:
            constraints.append(f"字数要求: {word_count.group(1)}")

        # 技术约束
        tech_constraints = re.findall(
            r"使用(?!.*(?<!不)使用)(Python|Java|JavaScript|C\+\+|Go|Rust|Node\.js|React|Flask|Django|Pandas|NumPy)",
            description, re.IGNORECASE
        )
        for tech in tech_constraints:
            constraints.append(f"技术要求: {tech}")

        # 评分标准
        if "评分" in description or "grading" in description.lower():
            constraints.append("需关注评分标准")

        return constraints

    def _extract_keywords(self, description: str) -> List[str]:
        """提取关键词"""
        # 提取技术术语和重要概念
        keywords = []

        # 提取英文技术词汇
        tech_terms = re.findall(
            r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
            description
        )

        # 提取中文关键词（2-4个字）
        cn_terms = re.findall(r'[\u4e00-\u9fa5]{2,4}', description)

        # 过滤常见词
        stopwords = {'这个', '那个', '什么', '如何', '怎样', '可以', '需要', '应该'}

        all_terms = tech_terms + cn_terms
        keywords = [t for t in all_terms if t.lower() not in stopwords and len(t) > 1]

        # 去重并保留出现次数多的
        from collections import Counter
        keyword_counts = Counter(keywords)
        keywords = [k for k, _ in keyword_counts.most_common(15)]

        return keywords

    def _determine_task_type(self, keywords: List[str]) -> TaskType:
        """判断任务类型"""
        programming_score = sum(1 for k in keywords if k.lower() in [
            kw.lower() for kw in self.PROGRAMMING_KEYWORDS
        ])
        writing_score = sum(1 for k in keywords if k.lower() in [
            kw.lower() for kw in self.WRITING_KEYWORDS
        ])

        if programming_score > writing_score:
            return TaskType.PROGRAMMING
        elif writing_score > programming_score:
            return TaskType.WRITING
        else:
            return TaskType.UNKNOWN

    def _determine_complexity(self, description: str) -> TaskComplexity:
        """判断任务复杂度"""
        text = description.lower()

        if any(word in text for word in self.COMPLEXITY_HIGH):
            return TaskComplexity.COMPLEX
        elif any(word in text for word in self.COMPLEXITY_LOW):
            return TaskComplexity.SIMPLE
        else:
            # 根据长度和关键词数量估算
            word_count = len(description.split())
            if word_count < 50:
                return TaskComplexity.SIMPLE
            elif word_count < 200:
                return TaskComplexity.MEDIUM
            else:
                return TaskComplexity.COMPLEX

    def _identify_dependencies(self, description: str) -> List[str]:
        """识别依赖知识领域"""
        dependencies = []

        # 常见课程领域
        domains = {
            "算法": ["算法", "algorithm", "sort", "search", "graph", "tree"],
            "数据结构": ["数据结构", "data structure", "array", "list", "stack", "queue"],
            "机器学习": ["机器学习", "machine learning", "ml", "neural", "deep learning"],
            "数据库": ["数据库", "database", "sql", "mysql", "mongodb"],
            "Web开发": ["web", "http", "api", "frontend", "backend"],
            "操作系统": ["操作系统", "os", "process", "thread", "memory"],
            "网络": ["网络", "network", "socket", "tcp", "http"],
            "软件工程": ["软件工程", "software engineering", "design", "test"],
        }

        for domain, keywords in domains.items():
            if any(kw.lower() in description.lower() for kw in keywords):
                dependencies.append(domain)

        return dependencies

    def _generate_subtasks(self, description: str, task_type: TaskType) -> List[str]:
        """生成子任务列表"""
        subtasks = []

        if task_type == TaskType.PROGRAMMING:
            subtasks = [
                "理解需求并设计解决方案",
                "编写核心代码",
                "编写测试用例",
                "调试和优化",
                "编写文档和注释"
            ]
        elif task_type == TaskType.WRITING:
            subtasks = [
                "收集和整理资料",
                "设计文档结构",
                "撰写各章节内容",
                "优化结构和表达",
                "格式检查和最终校对"
            ]
        else:
            subtasks = [
                "分析任务需求",
                "制定执行计划",
                "逐步完成任务",
                "检查和优化",
                "整理和交付"
            ]

        return subtasks

    def get_analysis_report(self) -> str:
        """生成分析报告"""
        if not self.requirement:
            return "请先运行 analyze() 方法"

        r = self.requirement

        report = f"""
## 任务分析报告

### 核心目标
{r.core_goal}

### 任务类型
{r.task_type.value.upper()}

### 复杂度
{r.complexity.value.upper()}

### 约束条件
{'、'.join(r.constraints) if r.constraints else '无特殊约束'}

### 关键词
{', '.join(r.keywords[:10])}

### 依赖知识领域
{'、'.join(r.dependencies) if r.dependencies else '通用知识'}

### 建议的子任务
"""
        for i, task in enumerate(r.subtasks, 1):
            report += f"{i}. {task}\n"

        return report
