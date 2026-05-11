#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartClip 核心功能测试
"""

import sys
import os
import hashlib
import json
from datetime import datetime

# 测试内容分类器
class ContentType:
    TEXT = "text"
    CODE = "code"
    URL = "url"
    EMAIL = "email"
    IMAGE = "image"
    FILE_PATH = "file_path"
    COMMAND = "command"
    UNKNOWN = "unknown"


class ContentClassifier:
    """AI内容分类器 - 智能识别剪贴板内容类型"""
    
    import re
    
    # 代码特征模式
    CODE_PATTERNS = [
        r'^(def|class|function|import|from|const|let|var|if|for|while)\s',
        r'[{\[\]};]$',
        r'^(#|//|/\*|\*|<!--)',
        r'[=+\-*/<>!]+',
        r'\(.*\)\s*\{',
        r'^(print|echo|console\.log|printf)',
    ]
    
    # URL模式
    URL_PATTERN = re.compile(
        r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$',
        re.IGNORECASE
    )
    
    # 邮箱模式
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # 文件路径模式
    FILE_PATH_PATTERN = re.compile(
        r'^(/[\w\-./]+|[A-Za-z]:\\[\\\w\-.]+|~/[\w\-./]+)$'
    )
    
    # 命令模式
    COMMAND_PATTERN = re.compile(
        r'^(git|npm|pip|docker|kubectl|curl|wget|ssh|cd|ls|cat|grep|awk|sed)\s',
        re.IGNORECASE
    )
    
    @classmethod
    def classify(cls, content: str) -> str:
        """智能分类内容类型"""
        import re
        content = content.strip()
        
        if not content:
            return ContentType.UNKNOWN
        
        # 检查URL
        if cls.URL_PATTERN.match(content):
            return ContentType.URL
        
        # 检查邮箱
        if cls.EMAIL_PATTERN.match(content):
            return ContentType.EMAIL
        
        # 检查文件路径
        if cls.FILE_PATH_PATTERN.match(content) and ('/' in content or '\\' in content):
            return ContentType.FILE_PATH
        
        # 检查命令
        if cls.COMMAND_PATTERN.match(content):
            return ContentType.COMMAND
        
        # 检查代码
        lines = content.split('\n')
        code_indicators = 0
        for line in lines[:10]:
            for pattern in cls.CODE_PATTERNS:
                if re.search(pattern, line):
                    code_indicators += 1
                    break
        
        if code_indicators >= 2 or (len(lines) > 1 and code_indicators >= 1):
            return ContentType.CODE
        
        return ContentType.TEXT
    
    @classmethod
    def extract_tags(cls, content: str, content_type: str) -> list:
        """从内容中提取标签"""
        tags = []
        content_lower = content.lower()
        
        lang_patterns = {
            'python': ['python', 'def ', 'import ', 'print(', '.py'],
            'javascript': ['javascript', 'js', 'const ', 'let ', 'var ', 'function(', '=>'],
            'typescript': ['typescript', 'ts', ': string', ': number', 'interface '],
            'java': ['java', 'public class', 'private ', 'System.out'],
            'go': ['golang', 'go', 'func ', 'package main'],
            'rust': ['rust', 'fn ', 'let mut', 'impl '],
            'bash': ['bash', 'shell', '#!/bin/bash', '#!/bin/sh'],
            'sql': ['sql', 'select ', 'from ', 'where ', 'insert ', 'update '],
            'html': ['html', '<div', '<span', '<p>', '<html'],
            'css': ['css', '{', '}', 'px;', 'em;', 'rem;'],
            'json': ['json', '{"', '[{"', '}]'],
        }
        
        for lang, patterns in lang_patterns.items():
            if any(p in content_lower for p in patterns):
                tags.append(lang)
                break
        
        tags.append(content_type)
        return list(set(tags))


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("🧪 SmartClip 核心功能测试")
    print("=" * 60)
    
    # 测试内容分类
    test_cases = [
        ('def hello():\n    print("world")', ContentType.CODE),
        ('https://github.com/user/repo', ContentType.URL),
        ('test@example.com', ContentType.EMAIL),
        ('/home/user/file.txt', ContentType.FILE_PATH),
        ('git clone https://github.com/user/repo', ContentType.COMMAND),
        ('Hello World', ContentType.TEXT),
    ]
    
    print("\n📋 内容分类测试:")
    all_passed = True
    for content, expected in test_cases:
        result = ContentClassifier.classify(content)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} [{result:10s}] {content[:40]}...")
    
    # 测试标签提取
    print("\n🏷️  标签提取测试:")
    code = 'def hello():\n    print("world")'
    ctype = ContentType.CODE
    tags = ContentClassifier.extract_tags(code, ctype)
    print(f"  ✓ 提取标签: {tags}")
    
    # 测试数据库
    print("\n💾 数据库测试:")
    try:
        import sqlite3
        db_path = '/tmp/smartclip_test.db'
        
        # 清理旧数据
        if os.path.exists(db_path):
            os.remove(db_path)
        
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # 插入测试数据
        test_id = hashlib.md5(b"test").hexdigest()[:16]
        conn.execute(
            "INSERT INTO clipboard_items VALUES (?, ?, ?, ?)",
            (test_id, 'print("Hello")', ContentType.CODE, datetime.now().isoformat())
        )
        conn.commit()
        
        # 查询数据
        cursor = conn.execute("SELECT * FROM clipboard_items")
        rows = cursor.fetchall()
        print(f"  ✓ 数据库操作成功: {len(rows)} 条记录")
        
        conn.close()
        os.remove(db_path)
        
    except Exception as e:
        print(f"  ✗ 数据库测试失败: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("⚠️  部分测试未通过")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
