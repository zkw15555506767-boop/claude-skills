#!/usr/bin/env python3
"""
translate.py — 带磁盘缓存的翻译工具
缓存文件：~/daily-news/data/translate_cache.json
"""

import json, os, re, sys, time
from pathlib import Path

CACHE_PATH = Path.home() / "daily-news" / "data" / "translate_cache.json"

_cache: dict = {}
_dirty = False

def _load():
    global _cache
    if CACHE_PATH.exists():
        try:
            _cache = json.loads(CACHE_PATH.read_text("utf-8"))
        except Exception:
            _cache = {}

def _save():
    global _dirty
    if _dirty:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(_cache, ensure_ascii=False, indent=2), "utf-8")
        _dirty = False

# 检测是否包含足够多中文（超过 30% 视为已是中文）
def _is_chinese(text: str) -> bool:
    if not text:
        return True
    zh = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return zh / len(text) > 0.25

def translate(text: str, retries: int = 2) -> str:
    global _dirty
    if not text or _is_chinese(text):
        return text

    key = text[:200]  # 缓存键用前200字符
    if key in _cache:
        return _cache[key]

    for attempt in range(retries + 1):
        try:
            # 警告压制
            import warnings
            warnings.filterwarnings("ignore")
            from deep_translator import GoogleTranslator
            result = GoogleTranslator(source="auto", target="zh-CN").translate(text)
            if result:
                _cache[key] = result
                _dirty = True
                return result
        except Exception as e:
            if attempt < retries:
                time.sleep(1.5)
            else:
                print(f"[translate] 失败: {e} | 原文: {text[:50]}", file=sys.stderr)
    return text  # 翻译失败返回原文


def translate_batch(texts: list[str]) -> list[str]:
    """批量翻译，跳过已是中文的条目"""
    results = []
    for text in texts:
        results.append(translate(text))
        time.sleep(0.05)  # 小间隔避免频控
    _save()
    return results


_load()
