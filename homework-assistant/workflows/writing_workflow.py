"""
写作工作流 (Writing Workflow)
处理写作类作业的完整流程
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class WritingPhase(Enum):
    RESEARCH = "research"
    OUTLINE = "outline"
    DRAFTING = "drafting"
    REVISION = "revision"
    PROOFREADING = "proofreading"
    COMPLETE = "complete"


@dataclass
class Document:
    """文档结构"""
    title: str = ""
    sections: List[Dict] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    word_count: int = 0
    content: str = ""


class WritingWorkflow:
    """写作任务工作流"""

    def __init__(self):
        self.current_phase = WritingPhase.RESEARCH
        self.document = Document()
        self.outline = {}
        self.research_notes = ""

    def run(self, task_requirement: Dict) -> Dict:
        """
        执行完整的写作任务工作流

        Args:
            task_requirement: 任务需求字典

        Returns:
            Dict: 执行结果
        """
        results = {}

        # 阶段1: 研究资料
        results['research'] = self._do_research(task_requirement)

        # 阶段2: 设计大纲
        results['outline'] = self._create_outline(task_requirement)

        # 阶段3: 撰写初稿
        results['drafting'] = self._write_draft(task_requirement)

        # 阶段4: 修订优化
        results['revision'] = self._revise(task_requirement)

        # 阶段5: 校对检查
        results['proofreading'] = self._proofread(task_requirement)

        self.current_phase = WritingPhase.COMPLETE

        return results

    def _do_research(self, requirement: Dict) -> Dict:
        """研究相关资料"""
        research = {
            "key_concepts": self._identify_key_concepts(requirement),
            "related_topics": self._identify_related_topics(requirement),
            "search_suggestions": self._generate_search_suggestions(requirement),
            "reference_format": self._detect_reference_format(requirement),
            "notes": "",
        }

        research["notes"] = f"""
研究要点：
1. 核心概念：{'、'.join(research['key_concepts'])}
2. 相关主题：{'、'.join(research['related_topics'])}
3. 推荐搜索：{'、'.join(research['search_suggestions'])}
4. 引用格式：{research['reference_format']}
"""

        self.research_notes = research["notes"]
        return research

    def _identify_key_concepts(self, requirement: Dict) -> List[str]:
        """识别核心概念"""
        description = requirement.get('core_goal', '')
        concepts = []

        # 从描述中提取专业术语
        import re

        # 提取英文术语
        english_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', description)

        # 提取中文学术词汇
        academic_cn = re.findall(r'[\u4e00-\u9fa5]{3,}', description)

        concepts = english_terms + academic_cn

        # 添加常见学术概念
        common_concepts = [
            "背景介绍", "研究方法", "分析讨论", "结论建议",
            "理论框架", "案例分析", "数据来源", "研究意义"
        ]

        for concept in common_concepts:
            if concept in description:
                concepts.append(concept)

        return list(set(concepts))[:10]

    def _identify_related_topics(self, requirement: Dict) -> List[str]:
        """识别相关主题"""
        description = requirement.get('core_goal', '').lower()
        topics = []

        topic_keywords = {
            "文献综述": ["文献综述", "literature review", "相关研究"],
            "案例分析": ["案例", "case study", "实例"],
            "比较分析": ["比较", "对比", "compare"],
            "因果分析": ["原因", "结果", "因果", "effect"],
            "问题解决": ["问题", "解决", "方案", "solution"],
            "趋势分析": ["趋势", "发展", "evolution"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in description for kw in keywords):
                topics.append(topic)

        return topics

    def _generate_search_suggestions(self, requirement: Dict) -> List[str]:
        """生成搜索建议"""
        core_goal = requirement.get('core_goal', '')

        suggestions = [
            f"关键词: {core_goal[:20]}...",
            "相关理论和概念",
            "最新研究进展",
            "实际应用案例",
        ]

        return suggestions

    def _detect_reference_format(self, requirement: Dict) -> str:
        """检测引用格式"""
        description = str(requirement.get('constraints', []))

        formats = {
            "APA": ["apa", "APA"],
            "MLA": ["mla", "MLA"],
            "Chicago": ["chicago", "Chicago"],
            "IEEE": ["ieee", "IEEE"],
            "GB/T 7714": ["gb", "GB", "中国标准"],
        }

        for fmt, keywords in formats.items():
            if any(kw in description for kw in keywords):
                return fmt

        return "未指定（建议使用通用学术格式）"

    def _create_outline(self, requirement: Dict) -> Dict:
        """创建文档大纲"""
        outline = {
            "title": requirement.get('core_goal', '文档标题'),
            "structure": self._generate_structure(requirement),
            "section_descriptions": {},
            "word_distribution": {},
        }

        # 生成各章节说明
        structure = outline["structure"]
        for section in structure:
            outline["section_descriptions"][section] = self._get_section_description(section)

        # 估算字数分布
        total_words = requirement.get('estimated_words', 2000)
        outline["word_distribution"] = self._distribute_words(structure, total_words)

        self.outline = outline
        return outline

    def _generate_structure(self, requirement: Dict) -> List[str]:
        """生成文档结构"""
        description = requirement.get('core_goal', '').lower()

        # 报告类结构
        report_structure = [
            "摘要",
            "引言",
            "正文主体",
            "结论",
            "参考文献"
        ]

        # 论文类结构
        paper_structure = [
            "摘要",
            "关键词",
            "引言",
            "文献综述",
            "研究方法",
            "结果与分析",
            "讨论",
            "结论",
            "参考文献"
        ]

        # 分析类结构
        analysis_structure = [
            "摘要",
            "背景介绍",
            "现状分析",
            "问题识别",
            "解决方案",
            "实施建议",
            "结论"
        ]

        # 根据内容选择结构
        if "论文" in description or "research" in description:
            return paper_structure
        elif "分析" in description or "analysis" in description:
            return analysis_structure
        else:
            return report_structure

    def _get_section_description(self, section: str) -> str:
        """获取章节描述"""
        descriptions = {
            "摘要": "简明扼要地概述研究目的、方法、主要结果和结论",
            "关键词": "3-5个能够反映论文核心内容的词汇",
            "引言": "介绍研究背景、目的、意义和研究问题",
            "文献综述": "回顾相关研究现状，找出研究空白",
            "研究方法": "说明采用的研究方法和数据来源",
            "结果与分析": "呈现研究结果，进行深入分析",
            "讨论": "解释结果的意义，与已有研究比较",
            "结论": "总结研究发现，提出未来研究方向",
            "参考文献": "列出引用的所有文献",
            "背景介绍": "提供必要的背景信息和上下文",
            "现状分析": "描述当前情况，分析特点和问题",
            "问题识别": "明确指出存在的问题和挑战",
            "解决方案": "提出具体的解决方案和建议",
            "实施建议": "给出可行的实施步骤和建议",
            "正文主体": "核心内容部分，包含主要论证和分析",
        }

        return descriptions.get(section, "本章节的核心内容")

    def _distribute_words(self, structure: List[str], total: int) -> Dict[str, int]:
        """分配字数"""
        # 各部分比例
        ratios = {
            "摘要": 0.05,
            "关键词": 0.01,
            "引言": 0.10,
            "文献综述": 0.15,
            "研究方法": 0.10,
            "结果与分析": 0.25,
            "讨论": 0.15,
            "结论": 0.08,
            "参考文献": 0.02,
            "背景介绍": 0.10,
            "现状分析": 0.15,
            "问题识别": 0.10,
            "解决方案": 0.20,
            "实施建议": 0.15,
            "正文主体": 0.30,
        }

        distribution = {}
        for section in structure:
            ratio = ratios.get(section, 0.10)
            distribution[section] = int(total * ratio)

        return distribution

    def _write_draft(self, requirement: Dict) -> Dict:
        """撰写初稿"""
        draft = {
            "full_text": "",
            "sections": {},
            "current_section": 0,
            "total_sections": len(self.outline.get('structure', [])),
        }

        # 根据大纲生成各章节内容
        structure = self.outline.get('structure', [])

        for i, section in enumerate(structure):
            section_content = self._write_section(section, requirement)
            draft["sections"][section] = section_content

        # 合并为完整文本
        draft["full_text"] = self._assemble_document(draft["sections"])

        self.document.content = draft["full_text"]
        self.document.sections = [{"title": k, "content": v} for k, v in draft["sections"].items()]

        return draft

    def _write_section(self, section: str, requirement: Dict) -> str:
        """撰写单个章节"""
        description = self.outline.get('section_descriptions', {}).get(section, "")
        target_words = self.outline.get('word_distribution', {}).get(section, 500)

        # 根据章节类型生成内容模板
        templates = {
            "摘要": f"""
## 摘要

{description}

[在此处撰写约{target_words}字的摘要内容，包括研究目的、主要方法和结论]
""",
            "引言": f"""
## 引言

### 背景
{description}
在当今[相关领域]的发展背景下，[研究主题]具有重要的理论和实践意义。

### 研究目的
本文旨在[研究目的]。

### 研究问题
本文将围绕以下问题展开研究：
1. [问题1]
2. [问题2]
3. [问题3]
""",
            "文献综述": f"""
## 文献综述

### 领域概述
{description}
[相关领域]在过去几十年中取得了显著进展。

### 主要研究观点
1. [观点1]：...
2. [观点2]：...
3. [观点3]：...

### 研究空白
通过文献梳理发现，现有研究在[方面]尚存在不足，有待进一步探索。
""",
            "正文主体": f"""
## 正文

### 主要内容
{description}

[根据具体要求撰写核心内容]
""",
            "结论": f"""
## 结论

### 主要发现
1. [发现1]
2. [发现2]
3. [发现3]

### 研究意义
本研究对[领域]的理论发展和实践应用具有重要意义。

### 局限性
本研究存在以下局限性：
1. [局限1]
2. [局限2]

### 未来展望
未来研究可以从以下方向深入：
1. [方向1]
2. [方向2]
""",
        }

        # 默认模板
        template = templates.get(section, f"""
## {section}

{description}

[撰写约{target_words}字的{section}内容]
""")

        return template

    def _assemble_document(self, sections: Dict[str, str]) -> str:
        """组装完整文档"""
        title = self.outline.get('title', '文档标题')
        document = f"# {title}\n\n"

        for section, content in sections.items():
            document += content + "\n"

        return document

    def _revise(self, requirement: Dict) -> Dict:
        """修订优化"""
        revision = {
            "structure_check": self._check_structure(),
            "content_quality": self._assess_quality(),
            "improvements": [],
            "revised_text": "",
        }

        # 结构检查
        revision["structure_check"] = {
            "has_abstract": "摘要" in self.document.sections,
            "has_conclusion": "结论" in self.document.sections,
            "flow_logical": True,  # 简化判断
            "balance": True,  # 简化判断
        }

        # 质量评估
        revision["content_quality"] = {
            "clarity": "待评估",
            "coherence": "待评估",
            "depth": "待评估",
            "originality": "待评估",
        }

        # 建议改进
        revision["improvements"] = [
            "检查各章节之间的逻辑衔接",
            "确保论证充分、证据确凿",
            "优化语言表达，提高可读性",
            "统一格式规范",
        ]

        return revision

    def _check_structure(self) -> Dict:
        """检查文档结构"""
        return {
            "sections_count": len(self.document.sections),
            "required_sections": ["摘要", "正文", "结论"],
            "missing_sections": [],
            "order_correct": True,
        }

    def _assess_quality(self) -> Dict:
        """评估内容质量"""
        return {
            "argument_strength": "中等",
            "evidence_quality": "待完善",
            "writing_style": "待评估",
            "overall": "初稿质量",
        }

    def _proofread(self, requirement: Dict) -> Dict:
        """校对检查"""
        proofread = {
            "grammar_check": self._check_grammar(),
            "format_check": self._check_format(),
            "citation_check": self._check_citations(),
            "final_document": "",
        }

        # 格式检查
        proofread["format_check"] = {
            "heading_levels": "待检查",
            "paragraph_spacing": "待检查",
            "font_consistency": "待检查",
            "page_numbers": "待添加",
        }

        # 引用检查
        proofread["citation_check"] = {
            "format": self.outline.get("reference_format", "通用"),
            "completeness": "待验证",
        }

        proofread["final_document"] = self.document.content
        return proofread

    def _check_grammar(self) -> Dict:
        """语法检查"""
        return {
            "spelling_errors": [],
            "grammar_errors": [],
            "punctuation_issues": [],
            "suggestions": [],
        }

    def _check_format(self) -> Dict:
        """格式检查"""
        return {
            "heading_format": "待统一",
            "paragraph_format": "待调整",
            "reference_format": "待确认",
        }

    def _check_citations(self) -> Dict:
        """引用检查"""
        return {
            "in_text_citations": "待添加",
            "reference_list": "待完善",
            "format_compliance": "待验证",
        }

    def get_document(self) -> Document:
        """获取文档"""
        return self.document
