---
name: homework-assistant
description: 智能作业助手 - 帮助分析课程作业、拆解任务、自动化完成编程和写作任务，具备长期记忆能力
license: MIT
---

# Homework Assistant

智能作业助手，帮助学生高效完成各类课程作业。

## 核心能力

- 任务分析与拆解
- 编程任务实现
- 文档写作任务
- PDF 解析与内容提取
- 长期记忆与知识积累

## 使用场景

当用户需要帮助完成课程作业时使用，特别是：
- 编程类作业（Web 开发、算法等）
- 写作类作业（报告、论文等）
- 需要解析 PDF 作业要求

## 与其他 Skill 的协同

### 前端设计任务
当作业涉及前端页面设计、UI 组件开发时，**必须调用 `frontend-design` skill**：
- `/frontend-design`
- 获取高质量前端代码和设计指导

### PDF 解析任务
当用户提供 PDF 文件时，**必须调用 `pdf` skill**：
- `/pdf`
- 解析 PDF 内容并提取关键信息

---

## 新功能：作业解读报告

### 功能描述
自动解析 PDF 作业文件，生成结构化的 Markdown 解读文档，包括：
- 基本信息（课程、截止日期、总分）
- 题目概览（题号、分值、主题）
- 详细要求
- 注意事项
- 待办清单

### 使用方法
```python
from tools.pdf_parser import generate_homework_report

# 1. 生成作业解读报告（自动中文翻译）
result = generate_homework_report('/path/to/assignment.pdf')
# 输出: /path/to/assignment_解读.md

# 2. 将解读报告转换为 PDF
from tools.pdf_parser import markdown_to_pdf
pdf_path = markdown_to_pdf('/path/to/assignment_解读.md', '/path/to/output.pdf')

# 3. 直接创建作业 PDF
from tools.pdf_parser import create_homework_pdf
pdf_path = create_homework_pdf(
    title="作业标题",
    content="# 作业内容\n\n这里是正文...",
    output_path="/path/to/homework.pdf",
    course="CMSC5730"
)

# 4. 生成自然风格的写作内容（避免 AI 痕迹）
from tools.pdf_parser import generate_natural_writing
content = generate_natural_writing(
    topic="讨论主题",
    style="academic",  # academic, report, essay
    length="medium"
)
```

### 输出示例

**1. 作业解读报告 (`xxx_解读.md`)**
- 作业基本信息表格
- 题目分值汇总表
- 每道题的详细要求
- 运行环境要求
- 提交注意事项
- 待办清单

**2. 生成的作业 PDF**
- 专业的 PDF 排版
- 自然流畅的写作风格
- 避免 AI 检测的写作模式
- 支持多种学术写作风格

---

## User-Learned Best Practices & Constraints

### Skill 协同规则 (2026-01-27)

**preferences:**
- 当作业涉及前端页面设计时，必须调用 `frontend-design` skill 获取专业的前端设计指导
- 当需要读取 PDF 文件时，必须调用 `pdf` skill，而不是直接用代码解析
- 在评估作业完成情况时，仔细阅读评分标准中的特殊声明（如 "JavaScript is NOT necessary"）

**fixes:**
- 不要直接用 Python/pdfplumber 读取 PDF，应该调用 `/pdf` skill
- 前端设计任务不要自己写代码，应该委托给 `frontend-design` skill

**custom_prompts:**
- 当用户说 "帮我评估作业" 时，先确认是否需要读取 PDF（调用 `/pdf`），再分析代码，最后对照评分标准逐项检查

### PDF 生成最佳实践 (2026-02-05)

根据内容类型使用不同排版：

#### 1. 纯文字内容（论文、报告、案例分析）

**fonts:**
- 统一使用 Helvetica 字体（避免混用 Times Roman）
- 字号：标题 18pt，小节标题 12pt，正文 11pt，页脚 9pt

**formatting:**
- 行间距 15pt，段落间距 10pt
- 段落首行不缩进，用额外间距分隔
- 页面底部保留至少 70pt
- 长段落拆分（每段 3-5 行）

#### 2. 代码内容（编程作业、算法实现）

**fonts:**
- 代码块使用等宽字体（Courier、Consolas 或 monospace）
- 字号 10-11pt

**formatting:**
- 代码块左侧缩进（类似 Markdown 的 ``` 代码块）
- 保持代码缩进结构
- 必要时添加行号
- 代码前后增加额外间距

#### 3. 表格内容（数据展示、对比分析）

**formatting:**
- 使用表格组件绘制
- 列宽根据内容自动调整
- 表头加粗或使用不同背景色
- 单元格内容居中或左对齐
- 表格过长时分页显示

#### 通用规则

**output:**
- 支持在封面添加学生 ID（如 "Student ID: 1155239091"）
- 删除 Markdown 源文件中的 "---" 分隔符再生成 PDF
- 验证 PDF 文件大小和页数是否合理
- 中文字符会导致显示问题，英文 PDF 确保全部 ASCII

### 避免 AI 写作痕迹指南 (2026-02-05)

**avoid_patterns:**
- 过度使用 "One of the most important factors was..."
- "The concept of X is central to Y's philosophy"
- "This approach has enabled..." (过度使用)
- "It is worth noting that..."
- "In conclusion, I would like to say that..."
- 多次使用相同句式开头（如以 "This" 开头的句子）

**improvements:**
- 使用描述性的小节标题（如 "From Student to Entrepreneur" 而非 "How They Got Started"）
- 直接开始主题，不要过度铺垫
- 简化过渡表达，自然衔接段落
- 保持句子长度变化，避免统一句式
- 避免排比句和对仗结构

### 工具函数更新

```python
from tools.pdf_parser import create_homework_pdf

# 创建带学生 ID 的专业 PDF
pdf_path = create_homework_pdf(
    title="Case Study on Successful Entrepreneur",
    subtitle="Zhang Yiming (Founder of ByteDance)",
    content="# 作业内容\n\n...",
    output_path="/path/to/homework.pdf",
    course="CMSC5730 - IT Entrepreneurship and Marketing",
    student_id="1155239091",  # 新增参数
    date="2026-02-05"
)
```
