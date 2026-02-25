"""
PDF Parser Tool for Homework Assistant
Provides PDF text extraction and analysis capabilities.
"""

import os
import re
import subprocess
from typing import Dict, List, Optional
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content as string
    """
    # Try pdfplumber first (best for text extraction)
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text
    except ImportError:
        pass
    except Exception:
        pass

    # Try pypdf as second option
    try:
        import pypdf
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: use pdftotext command line tool
    try:
        result = subprocess.run(
            ['pdftotext', pdf_path, '-'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout.strip():
            return result.stdout
    except FileNotFoundError:
        pass

    return "Error: Unable to extract text from PDF. Please install pdfplumber: pip install pdfplumber"


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extract images from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images

    Returns:
        List of paths to extracted images
    """
    try:
        from pypdf import PdfReader

        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(pdf_path)
        image_paths = []

        for page_num, page in enumerate(reader.pages):
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject']
                for obj_name in xObject:
                    if xObject[obj_name]['/Subtype'] == '/Image':
                        image_paths.append(f"{output_dir}/page_{page_num}_{obj_name}.png")

        return image_paths
    except Exception as e:
        return [f"Error extracting images: {str(e)}"]


def analyze_pdf_structure(pdf_path: str) -> Dict:
    """
    Analyze PDF structure and metadata.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with PDF metadata and structure info
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            info = {
                "num_pages": len(pdf.pages),
                "metadata": pdf.metadata or {},
                "is_encrypted": False
            }

            # Analyze each page
            page_info = []
            for i, page in enumerate(pdf.pages):
                page_data = {
                    "page_num": i + 1,
                    "has_text": False,
                    "has_images": len(page.images) > 0 if hasattr(page, 'images') else False,
                    "text_length": 0
                }

                text = page.extract_text()
                if text and text.strip():
                    page_data["has_text"] = True
                    page_data["text_length"] = len(text)

                page_info.append(page_data)

            info["pages"] = page_info
            return info

    except Exception as e:
        return {"error": str(e)}


def extract_tables_from_pdf(pdf_path: str) -> List[str]:
    """
    Attempt to extract tabular data from PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of extracted table texts
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            tables = []

            for page in pdf.pages:
                # Try to extract tables using pdfplumber's table extraction
                extracted_tables = page.extract_tables()
                if extracted_tables:
                    for table in extracted_tables:
                        table_text = "\n".join(["| " + " | ".join([str(cell) if cell else "" for cell in row]) + " |" for row in table])
                        tables.append(table_text)

            return tables if tables else ["No tables found"]
    except Exception as e:
        return [f"Error extracting tables: {str(e)}"]


def summarize_pdf(pdf_path: str, max_length: int = 1000) -> str:
    """
    Generate a summary of PDF content.

    Args:
        pdf_path: Path to the PDF file
        max_length: Maximum length of summary

    Returns:
        Summary text
    """
    text = extract_text_from_pdf(pdf_path)
    if not text or text.startswith("Error"):
        return text

    # Simple summary: first few paragraphs + key headings
    lines = text.split('\n')
    summary_lines = []

    for line in lines:
        if line.isupper() and len(line) > 10:  # Likely a heading
            summary_lines.append(f"\n## {line}\n")
        elif line.strip() and len(line) > 50:
            summary_lines.append(line)

    summary = ' '.join(summary_lines[:20])  # Take first 20 substantial lines
    return summary[:max_length] + "..." if len(summary) > max_length else summary


def convert_pdf_to_markdown(pdf_path: str, output_path: str = None) -> str:
    """
    Convert PDF content to Markdown format.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path to save markdown file

    Returns:
        Markdown formatted text
    """
    text = extract_text_from_pdf(pdf_path)
    if not text or text.startswith("Error"):
        return text

    markdown = "# Document Content\n\n"

    lines = text.split('\n')
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect headings (all caps or short lines ending with :)
        if (line.isupper() and len(line) > 5) or (len(line) < 50 and line.endswith(':')):
            markdown += f"\n## {line}\n"
        # Detect list items
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            if not in_list:
                in_list = True
                markdown += "\n"
            markdown += f"{line}\n"
        # Regular text
        else:
            in_list = False
            markdown += f"{line}\n"

    if output_path:
        with open(output_path, 'w') as f:
            f.write(markdown)

    return markdown


def parse_assignment_checklist(pdf_path: str) -> Dict:
    """
    Parse assignment checklist PDF specifically.

    Args:
        pdf_path: Path to the assignment checklist PDF

    Returns:
        Structured assignment information
    """
    text = extract_text_from_pdf(pdf_path)

    assignment = {
        "course": "",
        "title": "",
        "tasks": [],
        "deadlines": [],
        "requirements": [],
        "total_marks": 0
    }

    # Extract course info
    course_match = re.search(r'([A-Z]{4}\d{4,})', text)
    if course_match:
        assignment["course"] = course_match.group(1)

    # Extract tasks (looking for numbered sections)
    task_pattern = r'(Task\s*\d+[:\.]?\s*)([^\n]+)([\s\S]*?)(?=Task\s*\d+|$)'
    tasks = re.findall(task_pattern, text, re.IGNORECASE)

    for i, (task_num, task_name, task_content) in enumerate(tasks):
        task_info = {
            "task_num": i + 1,
            "name": task_name.strip(),
            "content": task_content.strip()[:200]  # First 200 chars
        }

        # Extract deadline
        deadline_match = re.search(r'(?:Deadline|due|submit|截止日期)[:\s]*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})', task_content, re.IGNORECASE)
        if deadline_match:
            task_info["deadline"] = deadline_match.group(1)

        # Extract marks
        marks_match = re.search(r'(\d+)\s*(?:marks?|分)', task_content, re.IGNORECASE)
        if marks_match:
            task_info["marks"] = int(marks_match.group(1))
            assignment["total_marks"] += int(marks_match.group(1))

        assignment["tasks"].append(task_info)

    return assignment


def translate_text(text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    """
    Translate text from source language to target language.

    Args:
        text: Text to translate
        source_lang: Source language code (default: en)
        target_lang: Target language code (default: zh)

    Returns:
        Translated text
    """
    try:
        from deep_translator import GoogleTranslator
        lang_map = {"en": "en", "zh": "zh-CN"}
        src = lang_map.get(source_lang, source_lang)
        dst = lang_map.get(target_lang, target_lang)
        translator = GoogleTranslator(source=src, target=dst)
        result = translator.translate(text)
        return result
    except ImportError:
        pass
    except Exception:
        pass

    return f"[翻译失败]: {text[:100]}..."


def convert_pdf_to_chinese(pdf_path: str, output_path: str = None) -> str:
    """
    Convert English PDF to Chinese Markdown file.

    Args:
        pdf_path: Path to the source PDF file
        output_path: Path to save the Chinese Markdown (optional)

    Returns:
        Path to the generated Chinese Markdown file
    """
    try:
        # Extract text from PDF
        original_text = extract_text_from_pdf(pdf_path)
        if original_text.startswith("Error"):
            return original_text

        # Translate text using deep_translator
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source="en", target="zh-CN")
            # Split into chunks for better translation (limit to 5000 chars per request)
            chunks = [original_text[i:i+4500] for i in range(0, len(original_text), 4500)]
            translated_chunks = []
            for chunk in chunks:
                if chunk.strip():
                    translated = translator.translate(chunk)
                    if translated:
                        translated_chunks.append(str(translated))
            chinese_text = "".join(translated_chunks)
        except ImportError:
            chinese_text = original_text
        except Exception as e:
            print(f"Translation error: {e}")
            chinese_text = original_text

        # Output path - save as markdown
        if not output_path:
            output_path = pdf_path.replace('.pdf', '_CN.md')

        # Convert to Markdown format
        markdown = "# 中文翻译版本\n\n"

        lines = chinese_text.split('\n')
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect headings
            if (line.isupper() and len(line) > 5) or (len(line) < 50 and (line.endswith(':') or line.endswith('.'))):
                markdown += f"\n## {line}\n"
            # Detect list items
            elif line.startswith('•') or line.startswith('-') or line.startswith('*') or line.startswith('o '):
                if not in_list:
                    in_list = True
                    markdown += "\n"
                markdown += f"- {line.lstrip('•-* ')}\n"
            # Regular text
            else:
                in_list = False
                markdown += f"{line}\n\n"

        # Save markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return output_path

    except ImportError:
        return "Error: 需要安装 deep-translator\n运行: pip install deep-translator"
    except Exception as e:
        return f"Error: {str(e)}"


def translate_to_chinese(text: str) -> str:
    """翻译英文文本为中文"""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="en", target="zh-CN")
        # 限制每次翻译的长度
        if len(text) > 4500:
            text = text[:4500]
        result = translator.translate(text)
        return result if result else text
    except Exception:
        return text


def generate_homework_report(pdf_path: str, output_path: str = None) -> str:
    """
    生成作业详细解读报告（Markdown格式）

    功能：
    - 解析PDF作业要求
    - 提取课程信息、截止日期、题目分值
    - 生成结构化的待办清单
    - 识别特殊要求和注意事项
    - 自动翻译为中文

    Args:
        pdf_path: PDF作业文件路径
        output_path: 输出Markdown文件路径（可选）

    Returns:
        生成的Markdown文件路径
    """
    text = extract_text_from_pdf(pdf_path)
    if not text or text.startswith("Error"):
        return text

    # 提取基本信息
    course_match = re.search(r'([A-Z]{4}\s*\d{4,})', text)
    course = course_match.group(1) if course_match else "未知课程"

    # 提取截止日期
    deadline_match = re.search(r'Deadline[:\s]*(\d{1,2}[-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/\s]*\d{2,4}|\d{1,2}[-/\.]\d{1,2}[-/\.](\d{2,4})?)', text, re.IGNORECASE)
    deadline = deadline_match.group(1) if deadline_match else "未指定"

    # 提取作业标题
    title_match = re.search(r'(Assignment|作业|Project|实验)[^\n]*(?:\d+)?', text, re.IGNORECASE)
    title = title_match.group(0) if title_match else "作业"

    # 解析题目 (a), (b), (c), (d)
    questions = []

    # 按 "(a)" 分隔不同题目
    parts = re.split(r'\n([a-d]\)\s)', text)
    # parts[0] 是标题部分，parts[1] 是 (a) 标记，parts[2] 是 a 的内容...

    if len(parts) > 2:
        i = 1
        while i < len(parts):
            q_num = parts[i].replace(')', '').strip()
            q_content = parts[i+1] if i+1 < len(parts) else ""

            # 提取分值 [XX marks]
            marks_match = re.search(r'\[(\d+)\s*marks?\]', q_content, re.IGNORECASE)
            q_marks = int(marks_match.group(1)) if marks_match else 0

            # 清理描述，移除分值标记和多余空白
            q_content_clean = re.sub(r'\s*\[\d+\s*marks?\].*', '', q_content, flags=re.IGNORECASE)
            q_content_clean = re.sub(r'\s+', ' ', q_content_clean).strip()
            q_desc = q_content_clean[:500]  # 增加长度以获取完整描述

            # 翻译为中文
            q_desc_cn = translate_to_chinese(q_desc)

            questions.append({
                "num": q_num,
                "description": q_desc,
                "description_cn": q_desc_cn,
                "marks": q_marks
            })
            i += 2

    # 如果没找到，尝试另一种方式提取
    if not questions:
        # 查找 (a), (b), (c) 等
        part_pattern = r'\(([a-d])\)\s*([^\n]+(?:\n[^\n]+){0,3})'
        matches = re.findall(part_pattern, text)
        for match in matches:
            desc_cn = translate_to_chinese(match[1].strip()[:200])
            questions.append({
                "num": match[0],
                "description": re.sub(r'\s+', ' ', match[1]).strip()[:200],
                "description_cn": desc_cn,
                "marks": 0
            })

    # 提取注意事项（特殊符号开头的列表，包括Unicode bullet）
    notes = []
    # 只匹配行首的bullet字符
    bullet_pattern = r'(?:^|\n)\s*[\uf0b7•*]\s*([^\n]+)'
    bullet_matches = re.findall(bullet_pattern, text)
    for match in bullet_matches:
        note = match.strip()
        # 只保留长度适中、有意义的条目
        if 20 < len(note) < 250 and note not in str(notes):
            notes.append(note)

    # 翻译注意事项
    notes_cn = [translate_to_chinese(n) for n in notes[:8]]

    # 提取VM/平台要求
    vm_notes = []
    vm_pattern = r'(VM|Red Hat|kernel|platform|平台|虚拟机)[^\n]*'
    vm_matches = re.findall(vm_pattern, text, re.IGNORECASE)
    for match in vm_matches:
        if len(match) > 20:
            vm_notes.append(match.strip())

    # 翻译VM要求
    vm_notes_cn = [translate_to_chinese(n) for n in vm_notes[:3]]

    # 提取提交要求
    submission_match = re.search(r'(?:提交|Submission|提交要求)[:\s]*([^\n]+(?:\n[^\n]+){0,2})', text, re.IGNORECASE)
    submission = submission_match.group(1).strip() if submission_match else ""
    submission_cn = translate_to_chinese(submission) if submission else ""

    # 计算总分
    total_marks = sum(q["marks"] for q in questions)

    # 生成中文Markdown报告
    report = f"""# {course} - {title}

## 基本信息

| 项目 | 内容 |
|------|------|
| **课程** | {course} |
| **作业** | {title} |
| **截止日期** | {deadline} |
| **总分** | {total_marks} 分 |

---

## 题目概览

| 题号 | 分值 | 主题/要求 | 状态 |
|------|------|-----------|------|
"""

    for q in questions:
        short_desc = q.get("description_cn", q["description"])[:40] + "..." if len(q.get("description_cn", q["description"])) > 40 else q.get("description_cn", q["description"])
        report += f"| ({q['num']}) | {q['marks']}分 | {short_desc} | ☐ |\n"

    report += """
---

## 详细要求

"""

    # 为每道题添加详细分析
    for i, q in enumerate(questions):
        report += f"### 第 ({q['num']}) 题 [{q['marks']}分]\n\n"
        desc_cn = q.get("description_cn", q["description"])
        report += f"**题目要求**：{desc_cn}\n\n"
        report += f"**答题要点**：\n"
        report += f"- [ ] 理解题目要求\n"
        report += f"- [ ] 参考相关知识点\n"
        report += f"- [ ] 整理答案\n\n"

    report += """---

## 注意事项

"""

    # 添加 VM/平台要求（使用中文翻译）
    if vm_notes_cn:
        report += "**运行环境要求**：\n"
        for note in vm_notes_cn:
            report += f"- {note}\n"
        report += "\n"

    for note in notes_cn:
        report += f"- {note}\n"

    if submission_cn:
        report += f"\n**提交要求**：{submission_cn}\n"

    report += """
---

## 待办清单

| 步骤 | 任务 | 状态 |
|------|------|------|
"""

    for i, q in enumerate(questions, 1):
        report += f"| {i} | 完成第 ({q['num']}) 题 ({q['marks']}分) | ☐ |\n"

    report += f"| {len(questions)+1} | 整理并提交作业 | ☐ |\n"

    report += """
---

## 下一步行动

1. 下载并安装必要的工具/环境
2. 获取作业相关文件（代码、数据等）
3. 逐一完成各道题目
4. 检查并提交

---

*报告生成时间：自动生成*
"""
# 保存文件
    if not output_path:
        output_path = pdf_path.replace('.pdf', '_解读.md')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return output_path


def markdown_to_pdf(markdown_path: str, output_path: str = None) -> str:
    """
    将 Markdown 文件转换为 PDF 格式。

    使用 reportlab 生成专业的 PDF 文档，避免 AI 写作痕迹的自然排版。

    Args:
        markdown_path: Markdown 文件路径
        output_path: 输出 PDF 路径（可选）

    Returns:
        生成的 PDF 文件路径
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
        from reportlab.lib.units import inch

        # 读取 markdown 内容
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        # 解析 markdown
        lines = markdown_text.split('\n')
        elements = []

        # 创建样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            leading=14,
            alignment=TA_JUSTIFY
        )

        # 生成输出路径
        if not output_path:
            output_path = markdown_path.replace('.md', '.pdf')

        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 标题检测
            if line.startswith('# '):
                clean_title = line[2:].strip()
                elements.append(Paragraph(clean_title, title_style))
            # 标题2
            elif line.startswith('## '):
                clean_heading = line[3:].strip()
                elements.append(Paragraph(clean_heading, heading_style))
            # 列表项
            elif line.startswith('- ') or line.startswith('* '):
                clean_item = line[2:].strip()
                elements.append(Paragraph(f"• {clean_item}", body_style))
            # 编号列表
            elif re.match(r'^\d+\. ', line):
                clean_item = re.sub(r'^\d+\. ', '', line).strip()
                elements.append(Paragraph(f"  {clean_item}", body_style))
            # 粗体文本
            elif '**' in line:
                clean_line = line.replace('**', '')
                elements.append(Paragraph(clean_line, body_style))
            # 普通段落
            elif len(line) > 10:
                elements.append(Paragraph(line, body_style))

            elements.append(Spacer(1, 6))

        # 构建 PDF
        doc.build(elements)
        return output_path

    except ImportError:
        return "Error: 需要安装 reportlab\n运行: pip install reportlab"
    except Exception as e:
        return f"Error: {str(e)}"


def create_homework_pdf(
    title: str,
    content: str,
    output_path: str,
    course: str = "",
    author: str = "Student"
) -> str:
    """
    直接创建作业 PDF 文档，支持自然写作风格。

    Args:
        title: 作业标题
        content: 作业内容（Markdown 格式）
        output_path: 输出 PDF 路径
        course: 课程名称
        author: 作者姓名

    Returns:
        生成的 PDF 文件路径
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
        from reportlab.lib.units import inch
        from datetime import datetime

        elements = []
        styles = getSampleStyleSheet()

        # 标题样式
        title_style = ParagraphStyle(
            'HomeworkTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_LEFT
        )

        # 正文样式 - 使用更适合阅读的排版
        body_style = ParagraphStyle(
            'HomeworkBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=8,
            leading=16,
            alignment=TA_JUSTIFY,
            firstLineIndent=24
        )

        # 标题样式
        heading_style = ParagraphStyle(
            'HomeworkHeading',
            parent=styles['Heading2'],
            fontSize=13,
            spaceBefore=15,
            spaceAfter=10
        )

        # 添加标题
        if course:
            elements.append(Paragraph(f"{course}", body_style))
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))

        # 解析内容
        lines = content.split('\n')
        current_para = ""

        for line in lines:
            line = line.strip()

            if not line:
                if current_para:
                    elements.append(Paragraph(current_para, body_style))
                    current_para = ""
                continue

            # 标题检测
            if line.startswith('# '):
                if current_para:
                    elements.append(Paragraph(current_para, body_style))
                    current_para = ""
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(line[2:].strip(), title_style))
            elif line.startswith('## '):
                if current_para:
                    elements.append(Paragraph(current_para, body_style))
                    current_para = ""
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(line[3:].strip(), heading_style))
            # 列表项
            elif line.startswith('- ') or line.startswith('* '):
                if current_para:
                    elements.append(Paragraph(current_para, body_style))
                    current_para = ""
                elements.append(Paragraph(f"• {line[2:].strip()}", body_style))
            # 代码块（简化处理）
            elif line.startswith('```') or line.startswith('```'):
                pass
            elif '```' in line:
                pass
            elif line.startswith('    ') or line.startswith('\t'):
                if current_para:
                    elements.append(Paragraph(current_para, body_style))
                    current_para = ""
                elements.append(Paragraph(f"<code>{line.strip()}</code>", body_style))
            # 普通段落
            else:
                clean_line = line.replace('**', '').replace('*', '').replace('`', '')
                current_para += clean_line + " "

        # 添加最后的段落
        if current_para:
            elements.append(Paragraph(current_para, body_style))

        # 添加日期
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"提交日期: {datetime.now().strftime('%Y-%m-%d')}", body_style))

        # 生成 PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        doc.build(elements)

        return output_path

    except Exception as e:
        return f"Error: {str(e)}"


def generate_natural_writing(
    topic: str,
    style: str = "academic",
    length: str = "medium"
) -> str:
    """
    生成自然、不像 AI 写作风格的内容。

    Args:
        topic: 写作主题
        style: 写作风格 (academic, report, essay)
        length: 长度 (short, medium, long)

    Returns:
        自然风格的文本内容
    """
    import random
    random.seed()

    length_map = {
        "short": (3, 5),
        "medium": (5, 8),
        "long": (8, 12)
    }
    min_para, max_para = length_map.get(length, (5, 8))
    num_paragraphs = (min_para + max_para) // 2

    style_config = {
        "academic": {
            "opening": [
                "在讨论这个问题之前，我认为有必要先回顾一下相关的背景知识。",
                "这个问题在实际应用中具有重要意义值得我们深入探讨。",
                "从课程所学的角度来看，这个问题涉及到多个核心概念。",
                "经过对相关资料的分析，我对这个问题有了更全面的理解。",
            ],
            "transitions": [
                "基于上述分析，我们可以进一步探讨...",
                "与此同时，我们也需要考虑...",
                "从这个角度来看，情况变得更加清晰。",
                "值得注意的是...",
                "从另一个角度来说...",
            ],
            "closing": [
                "综上所述，我认为这个问题需要从多个维度来理解。",
                "通过本次分析，我对这个问题有了更深入的认识。",
                "总的来说，这个问题值得我们继续研究和探讨。",
            ]
        },
        "report": {
            "opening": [
                "本报告旨在分析和探讨相关问题。",
                "根据收集到的资料，我们对这个问题进行了全面的调查。",
            ],
            "transitions": [
                "首先...",
                "其次...",
                "此外...",
                "同时...",
                "最后...",
            ],
            "closing": [
                "基于本次分析，我们得出以下结论...",
                "综上所述，建议采取以下措施...",
            ]
        },
        "essay": {
            "opening": [
                "这个问题一直引发我的思考。",
                "在我学习这门课程的过程中，这个问题给我留下了深刻的印象。",
            ],
            "transitions": [
                "但是...",
                "然而...",
                "不过...",
                "话虽如此...",
                "话又说回来...",
            ],
            "closing": [
                "这就是我对这个问题的一些思考。",
                "也许这个问题没有标准答案，但思考本身就是有价值的。",
            ]
        }
    }

    config = style_config.get(style, style_config["academic"])
    paragraphs = []

    paragraphs.append(random.choice(config["opening"]))

    for i in range(num_paragraphs - 2):
        if i == 0:
            para = f"首先，关于这个问题，我认为需要从以下几个方面来理解。{random.choice(config['transitions'])}在实际操作中，我们还需要注意一些细节问题。"
        elif i == num_paragraphs - 3:
            para = f"最后，通过这次分析，我深刻认识到理论学习与实践相结合的重要性。{random.choice(config['transitions'])}"
        else:
            transition = random.choice(config["transitions"])
            para = f"{transition} 具体来说，我认为可以从以下几个角度来分析这个问题。一方面，{random.choice(['这需要我们考虑实际情况', '这涉及到多方面的因素', '这对我们提出了新的要求'])}；另一方面，{random.choice(['我们也要注意可能的困难', '还需要结合具体案例', '这需要我们深入思考'])}。"

        paragraphs.append(para)

    paragraphs.append(random.choice(config["closing"]))

    return "\n\n".join(paragraphs)
