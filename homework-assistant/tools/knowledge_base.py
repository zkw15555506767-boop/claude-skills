"""
知识库管理器 (Knowledge Base Manager)
管理课程知识和参考资料
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import re


@dataclass
class KnowledgeEntry:
    """知识条目"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0


class KnowledgeBase:
    """知识库管理器"""

    def __init__(self, knowledge_dir: str = "../knowledge"):
        self.knowledge_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/knowledge"

        # 确保目录存在
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "courses"), exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "resources"), exist_ok=True)

        self.index_file = os.path.join(self.knowledge_dir, "index.json")
        self.entries: Dict[str, KnowledgeEntry] = {}

        # 加载知识库
        self._load_index()
        self._scan_knowledge_dir()

    def _load_index(self):
        """加载索引文件"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = {
                        k: KnowledgeEntry(**v) for k, v in data.items()
                    }
            except Exception as e:
                print(f"加载知识库索引失败: {e}")
                self.entries = {}

    def _save_index(self):
        """保存索引文件"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {k: asdict(v) for k, v in self.entries.items()},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            print(f"保存知识库索引失败: {e}")

    def _scan_knowledge_dir(self):
        """扫描知识目录，加载已有文件"""
        # 扫描课程目录
        courses_dir = os.path.join(self.knowledge_dir, "courses")
        if os.path.exists(courses_dir):
            for filename in os.listdir(courses_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(courses_dir, filename)
                    self._load_markdown_file(filepath, "course")

        # 扫描模板目录
        templates_dir = os.path.join(self.knowledge_dir, "templates")
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith(('.md', '.py', '.txt')):
                    filepath = os.path.join(templates_dir, filename)
                    self._load_markdown_file(filepath, "template")

    def _load_markdown_file(self, filepath: str, category: str):
        """加载markdown文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取标题
            title = os.path.basename(filepath).replace('.md', '').replace('_', ' ')
            title = re.sub(r'^#+\s*', '', content.split('\n')[0]) if content else title

            # 生成ID
            file_id = os.path.splitext(os.path.basename(filepath))[0]

            entry = KnowledgeEntry(
                id=file_id,
                title=title,
                content=content,
                category=category,
                tags=[category]
            )

            self.entries[file_id] = entry

        except Exception as e:
            print(f"加载文件失败 {filepath}: {e}")

    def query(self, keyword: str, category: str = None, limit: int = 5) -> List[KnowledgeEntry]:
        """
        搜索知识库

        Args:
            keyword: 搜索关键词
            category: 可选的分类筛选
            limit: 返回结果数量

        Returns:
            List[KnowledgeEntry]: 匹配的知识条目
        """
        results = []

        keyword_lower = keyword.lower()

        for entry in self.entries.values():
            # 分类过滤
            if category and entry.category != category:
                continue

            # 关键词匹配
            score = 0
            if keyword_lower in entry.title.lower():
                score += 10
            if keyword_lower in entry.content.lower():
                score += 5
            if any(keyword_lower in tag.lower() for tag in entry.tags):
                score += 3

            if score > 0:
                entry.usage_count += 1
                results.append((score, entry))

        # 按分数排序
        results.sort(key=lambda x: -x[0])
        entries = [entry for _, entry in results[:limit]]

        # 保存更新
        self._save_index()

        return entries

    def query_by_tags(self, tags: List[str], limit: int = 5) -> List[KnowledgeEntry]:
        """
        通过标签搜索

        Args:
            tags: 标签列表
            limit: 返回数量

        Returns:
            List[KnowledgeEntry]: 匹配的知识条目
        """
        results = []

        for entry in self.entries.values():
            if any(tag in entry.tags for tag in tags):
                results.append(entry)

        return results[:limit]

    def add_entry(self, title: str, content: str, category: str, tags: List[str] = None) -> str:
        """
        添加知识条目

        Args:
            title: 标题
            content: 内容
            category: 分类
            tags: 标签

        Returns:
            str: 条目ID
        """
        import hashlib

        # 生成ID
        content_hash = hashlib.md5((title + content).encode()).hexdigest()[:8]
        entry_id = f"{category}_{content_hash}"

        entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [category]
        )

        self.entries[entry_id] = entry
        self._save_index()

        # 如果是课程知识，同时保存为文件
        if category == "course":
            self._save_entry_to_file(entry)

        return entry_id

    def _save_entry_to_file(self, entry: KnowledgeEntry):
        """保存条目到文件"""
        filepath = os.path.join(
            self.knowledge_dir,
            "courses",
            f"{entry.id}.md"
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {entry.title}\n\n")
                f.write(f"---\n\n")
                f.write(entry.content)
        except Exception as e:
            print(f"保存知识条目失败: {e}")

    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """
        更新知识条目

        Args:
            entry_id: 条目ID
            **kwargs: 要更新的字段

        Returns:
            bool: 是否成功
        """
        if entry_id not in self.entries:
            return False

        entry = self.entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        entry.updated_at = datetime.now().isoformat()
        self._save_index()

        return True

    def delete_entry(self, entry_id: str) -> bool:
        """
        删除知识条目

        Args:
            entry_id: 条目ID

        Returns:
            bool: 是否成功
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save_index()
            return True
        return False

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """
        获取指定条目

        Args:
            entry_id: 条目ID

        Returns:
            KnowledgeEntry 或 None
        """
        return self.entries.get(entry_id)

    def get_all_entries(self, category: str = None) -> List[KnowledgeEntry]:
        """
        获取所有条目

        Args:
            category: 可选的分类筛选

        Returns:
            List[KnowledgeEntry]: 条目列表
        """
        entries = list(self.entries.values())
        if category:
            entries = [e for e in entries if e.category == category]
        return entries

    def get_statistics(self) -> Dict:
        """
        获取知识库统计信息

        Returns:
            Dict: 统计信息
        """
        categories = {}
        total_usage = 0

        for entry in self.entries.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1
            total_usage += entry.usage_count

        return {
            "total_entries": len(self.entries),
            "categories": categories,
            "total_usage": total_usage,
        }

    def format_for_prompt(self, query: str, max_entries: int = 3) -> str:
        """
        格式化知识供提示词使用

        Args:
            query: 查询关键词
            max_entries: 最大条目数

        Returns:
            str: 格式化的知识内容
        """
        entries = self.query(query, limit=max_entries)

        if not entries:
            return ""

        parts = ["【相关知识】"]

        for entry in entries:
            parts.append(f"\n## {entry.title}")
            parts.append(f"分类: {entry.category}")
            parts.append(f"标签: {', '.join(entry.tags)}")
            parts.append(f"\n{entry.content[:500]}")

        return "\n".join(parts)


def asdict(obj):
    """将对象转为字典（处理datetime）"""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: asdict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    elif isinstance(obj, list):
        return [asdict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: asdict(v) for k, v in obj.items()}
    else:
        return obj


def main():
    """测试函数"""
    kb = KnowledgeBase()

    # 添加测试条目
    kb.add_entry(
        "快速排序算法",
        """
## 算法原理
快速排序是一种分治算法，通过选择一个基准元素，将数组分成两部分...

## 时间复杂度
- 平均: O(n log n)
- 最坏: O(n²)

## 空间复杂度
O(log n)

## 实现要点
1. 选择基准元素
2. 分区操作
3. 递归排序
        """,
        "algorithm",
        ["排序", "算法", "快速排序"]
    )

    # 搜索
    results = kb.query("快速排序")
    print("搜索结果:", [r.title for r in results])

    # 统计
    print("统计:", kb.get_statistics())


if __name__ == "__main__":
    main()
