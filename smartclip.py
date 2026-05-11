#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartClip - AI驱动的智能剪贴板管理器
SmartClip - AI-Powered Intelligent Clipboard Manager

@author: SmartClip Team
@license: MIT
@version: 1.0.0
"""

import sys
import os
import json
import sqlite3
import hashlib
import threading
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import re
import urllib.parse

# GUI imports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont

# Clipboard handling
try:
    import pyperclip
except ImportError:
    pyperclip = None

# For hotkey handling
try:
    import keyboard
except ImportError:
    keyboard = None


class ContentType(Enum):
    """剪贴板内容类型枚举"""
    TEXT = "text"
    CODE = "code"
    URL = "url"
    EMAIL = "email"
    IMAGE = "image"
    FILE_PATH = "file_path"
    COMMAND = "command"
    UNKNOWN = "unknown"


@dataclass
class ClipboardItem:
    """剪贴板条目数据类"""
    id: str
    content: str
    content_type: ContentType
    created_at: str
    updated_at: str
    tags: List[str]
    favorite: bool
    usage_count: int
    source_app: str
    hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "content_type": self.content_type.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "favorite": self.favorite,
            "usage_count": self.usage_count,
            "source_app": self.source_app,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardItem':
        return cls(
            id=data["id"],
            content=data["content"],
            content_type=ContentType(data.get("content_type", "text")),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            tags=data.get("tags", []),
            favorite=data.get("favorite", False),
            usage_count=data.get("usage_count", 0),
            source_app=data.get("source_app", ""),
            hash=data.get("hash", "")
        )


class ContentClassifier:
    """AI内容分类器 - 智能识别剪贴板内容类型"""
    
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
    def classify(cls, content: str) -> ContentType:
        """智能分类内容类型"""
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
        for line in lines[:10]:  # 检查前10行
            for pattern in cls.CODE_PATTERNS:
                if re.search(pattern, line):
                    code_indicators += 1
                    break
        
        # 如果代码特征超过2个，判定为代码
        if code_indicators >= 2 or (len(lines) > 1 and code_indicators >= 1):
            return ContentType.CODE
        
        return ContentType.TEXT
    
    @classmethod
    def extract_tags(cls, content: str, content_type: ContentType) -> List[str]:
        """从内容中提取标签"""
        tags = []
        content_lower = content.lower()
        
        # 编程语言标签
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
        
        # URL域名标签
        if content_type == ContentType.URL:
            try:
                domain = urllib.parse.urlparse(content).netloc
                if domain:
                    tags.append(domain.replace('www.', '').split('.')[0])
            except:
                pass
        
        # 添加类型标签
        tags.append(content_type.value)
        
        return list(set(tags))


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            config_dir = os.path.expanduser("~/.smartclip")
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, "clipboard.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT,
                    favorite INTEGER DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    source_app TEXT,
                    hash TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_items(content_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_favorite ON clipboard_items(favorite)
            """)
            
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS clipboard_fts USING fts5(
                    content, content_type, tags,
                    content_rowid=rowid
                )
            """)
            
            conn.commit()
    
    def add_item(self, item: ClipboardItem) -> bool:
        """添加剪贴板条目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO clipboard_items 
                    (id, content, content_type, created_at, updated_at, tags, favorite, usage_count, source_app, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.id, item.content, item.content_type.value,
                    item.created_at, item.updated_at,
                    json.dumps(item.tags), int(item.favorite),
                    item.usage_count, item.source_app, item.hash
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding item: {e}")
            return False
    
    def get_items(self, limit: int = 100, content_type: ContentType = None, 
                  favorite_only: bool = False) -> List[ClipboardItem]:
        """获取剪贴板条目列表"""
        query = "SELECT * FROM clipboard_items WHERE 1=1"
        params = []
        
        if content_type:
            query += " AND content_type = ?"
            params.append(content_type.value)
        
        if favorite_only:
            query += " AND favorite = 1"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                item_data = dict(row)
                item_data['tags'] = json.loads(item_data.get('tags', '[]'))
                item_data['favorite'] = bool(item_data.get('favorite', 0))
                items.append(ClipboardItem.from_dict(item_data))
            
            return items
    
    def search_items(self, query: str, limit: int = 50) -> List[ClipboardItem]:
        """搜索剪贴板条目"""
        search_query = f"%{query}%"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM clipboard_items 
                WHERE content LIKE ? OR tags LIKE ? OR content_type LIKE ?
                ORDER BY 
                    CASE WHEN content LIKE ? THEN 1 ELSE 2 END,
                    usage_count DESC,
                    created_at DESC
                LIMIT ?
            """, (search_query, search_query, search_query, search_query, limit))
            
            rows = cursor.fetchall()
            items = []
            for row in rows:
                item_data = dict(row)
                item_data['tags'] = json.loads(item_data.get('tags', '[]'))
                item_data['favorite'] = bool(item_data.get('favorite', 0))
                items.append(ClipboardItem.from_dict(item_data))
            
            return items
    
    def toggle_favorite(self, item_id: str) -> bool:
        """切换收藏状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE clipboard_items 
                    SET favorite = NOT favorite, updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), item_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error toggling favorite: {e}")
            return False
    
    def increment_usage(self, item_id: str):
        """增加使用计数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE clipboard_items 
                    SET usage_count = usage_count + 1, updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), item_id))
                conn.commit()
        except Exception as e:
            print(f"Error incrementing usage: {e}")
    
    def delete_item(self, item_id: str) -> bool:
        """删除条目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False
    
    def clear_all(self) -> bool:
        """清空所有数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM clipboard_items")
                conn.commit()
                return True
        except Exception as e:
            print(f"Error clearing items: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM clipboard_items")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM clipboard_items WHERE favorite = 1")
            favorites = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT content_type, COUNT(*) as count 
                FROM clipboard_items 
                GROUP BY content_type
            """)
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total": total,
                "favorites": favorites,
                "type_counts": type_counts
            }


class ClipboardMonitor:
    """剪贴板监控器"""
    
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_content = ""
        self.running = False
        self.monitor_thread = None
        self.check_interval = 0.5  # 检查间隔（秒）
    
    def start(self):
        """启动监控"""
        if not pyperclip:
            print("Warning: pyperclip not available")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitor started")
    
    def stop(self):
        """停止监控"""
        self.running = False
        print("Clipboard monitor stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                current = pyperclip.paste()
                if current != self.last_content and current.strip():
                    self.last_content = current
                    self.callback(current)
            except Exception as e:
                print(f"Clipboard read error: {e}")
            
            time.sleep(self.check_interval)


class SmartClipApp:
    """SmartClip主应用程序"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.monitor = None
        self.root = None
        self.items_list = []
        self.current_filter = None
        self.search_var = None
        
        # 类型图标映射
        self.type_icons = {
            ContentType.TEXT: "📝",
            ContentType.CODE: "💻",
            ContentType.URL: "🔗",
            ContentType.EMAIL: "📧",
            ContentType.IMAGE: "🖼️",
            ContentType.FILE_PATH: "📁",
            ContentType.COMMAND: "⚡",
            ContentType.UNKNOWN: "📄"
        }
    
    def run(self):
        """运行应用程序"""
        self.root = tk.Tk()
        self.root.title("SmartClip - AI智能剪贴板")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        
        # 设置主题颜色
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#007acc"
        self.secondary_bg = "#252526"
        
        self.root.configure(bg=self.bg_color)
        
        # 设置窗口图标（如果有）
        try:
            self.root.iconbitmap("smartclip.ico")
        except:
            pass
        
        self._setup_ui()
        self._start_monitor()
        self._refresh_list()
        
        # 设置关闭行为
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.mainloop()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 SmartClip", 
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_frame,
            text="AI驱动的智能剪贴板管理器",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="#888888"
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=8)
        
        # 搜索栏
        search_frame = tk.Frame(main_frame, bg=self.secondary_bg)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_icon = tk.Label(search_frame, text="🔍", bg=self.secondary_bg, fg=self.fg_color)
        search_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            bg=self.secondary_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)
        
        # 筛选按钮
        filter_frame = tk.Frame(main_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        filters = [
            ("全部", None),
            ("代码", ContentType.CODE),
            ("链接", ContentType.URL),
            ("命令", ContentType.COMMAND),
            ("收藏", "favorite")
        ]
        
        for text, filter_type in filters:
            btn = tk.Button(
                filter_frame,
                text=text,
                command=lambda ft=filter_type: self._set_filter(ft),
                bg=self.secondary_bg,
                fg=self.fg_color,
                activebackground=self.accent_color,
                activeforeground=self.fg_color,
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 列表区域
        list_frame = tk.Frame(main_frame, bg=self.secondary_bg)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("type", "content", "time", "tags")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # 定义列
        self.tree.heading("type", text="类型")
        self.tree.heading("content", text="内容")
        self.tree.heading("time", text="时间")
        self.tree.heading("tags", text="标签")
        
        self.tree.column("type", width=60, anchor="center")
        self.tree.column("content", width=400)
        self.tree.column("time", width=120)
        self.tree.column("tags", width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self._on_item_double_click)
        self.tree.bind("<Button-3>", self._on_item_right_click)
        
        # 样式设置
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=self.secondary_bg,
            foreground=self.fg_color,
            fieldbackground=self.secondary_bg,
            rowheight=35
        )
        style.configure(
            "Treeview.Heading",
            background=self.bg_color,
            foreground=self.fg_color,
            font=("Segoe UI", 10, "bold")
        )
        style.map("Treeview", background=[("selected", self.accent_color)])
        
        # 底部按钮栏
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        buttons = [
            ("📋 复制选中", self._copy_selected),
            ("⭐ 收藏/取消", self._toggle_favorite_selected),
            ("🗑️ 删除", self._delete_selected),
            ("🧹 清空全部", self._clear_all),
            ("📊 统计", self._show_stats)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=self.accent_color,
                fg=self.fg_color,
                activebackground="#005a9e",
                activeforeground=self.fg_color,
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor="hand2",
                font=("Segoe UI", 9)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            bg=self.bg_color,
            fg="#888888",
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _start_monitor(self):
        """启动剪贴板监控"""
        self.monitor = ClipboardMonitor(self._on_clipboard_change)
        self.monitor.start()
    
    def _on_clipboard_change(self, content: str):
        """剪贴板内容变化回调"""
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 分类内容
        content_type = ContentClassifier.classify(content)
        
        # 提取标签
        tags = ContentClassifier.extract_tags(content, content_type)
        
        # 创建条目
        now = datetime.now().isoformat()
        item = ClipboardItem(
            id=content_hash[:16],
            content=content,
            content_type=content_type,
            created_at=now,
            updated_at=now,
            tags=tags,
            favorite=False,
            usage_count=0,
            source_app="",
            hash=content_hash
        )
        
        # 保存到数据库
        if self.db.add_item(item):
            self.status_var.set(f"已捕获: {content_type.value} | {len(content)} 字符")
            self._refresh_list()
    
    def _refresh_list(self):
        """刷新列表显示"""
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取数据
        if self.current_filter == "favorite":
            items = self.db.get_items(favorite_only=True)
        elif isinstance(self.current_filter, ContentType):
            items = self.db.get_items(content_type=self.current_filter)
        else:
            items = self.db.get_items()
        
        self.items_list = items
        
        # 填充列表
        for item in items:
            icon = self.type_icons.get(item.content_type, "📄")
            content_preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
            content_preview = content_preview.replace("\n", " ")
            
            time_str = item.created_at[11:16] if len(item.created_at) > 16 else item.created_at
            tags_str = ", ".join(item.tags[:3]) if item.tags else ""
            
            if item.favorite:
                content_preview = "⭐ " + content_preview
            
            self.tree.insert(
                "",
                tk.END,
                values=(icon, content_preview, time_str, tags_str),
                tags=(item.id,)
            )
    
    def _on_search(self, *args):
        """搜索回调"""
        query = self.search_var.get().strip()
        
        if not query:
            self._refresh_list()
            return
        
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 搜索并显示
        items = self.db.search_items(query)
        self.items_list = items
        
        for item in items:
            icon = self.type_icons.get(item.content_type, "📄")
            content_preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
            content_preview = content_preview.replace("\n", " ")
            
            time_str = item.created_at[11:16] if len(item.created_at) > 16 else item.created_at
            tags_str = ", ".join(item.tags[:3]) if item.tags else ""
            
            if item.favorite:
                content_preview = "⭐ " + content_preview
            
            self.tree.insert(
                "",
                tk.END,
                values=(icon, content_preview, time_str, tags_str),
                tags=(item.id,)
            )
    
    def _set_filter(self, filter_type):
        """设置筛选条件"""
        self.current_filter = filter_type
        self._refresh_list()
    
    def _get_selected_item(self) -> Optional[ClipboardItem]:
        """获取选中的条目"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item_id = self.tree.item(selection[0], "tags")[0]
        for item in self.items_list:
            if item.id == item_id:
                return item
        return None
    
    def _on_item_double_click(self, event):
        """双击条目"""
        self._copy_selected()
    
    def _on_item_right_click(self, event):
        """右键点击条目"""
        # 创建右键菜单
        menu = tk.Menu(self.root, tearoff=0, bg=self.secondary_bg, fg=self.fg_color)
        menu.add_command(label="复制", command=self._copy_selected)
        menu.add_command(label="收藏/取消收藏", command=self._toggle_favorite_selected)
        menu.add_separator()
        menu.add_command(label="删除", command=self._delete_selected)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _copy_selected(self):
        """复制选中条目到剪贴板"""
        item = self._get_selected_item()
        if not item:
            messagebox.showwarning("提示", "请先选择一个条目")
            return
        
        if pyperclip:
            pyperclip.copy(item.content)
            self.db.increment_usage(item.id)
            self.status_var.set(f"已复制: {item.content[:30]}...")
            self._refresh_list()
        else:
            messagebox.showerror("错误", "剪贴板功能不可用")
    
    def _toggle_favorite_selected(self):
        """切换选中条目的收藏状态"""
        item = self._get_selected_item()
        if not item:
            messagebox.showwarning("提示", "请先选择一个条目")
            return
        
        if self.db.toggle_favorite(item.id):
            self.status_var.set("收藏状态已更新")
            self._refresh_list()
    
    def _delete_selected(self):
        """删除选中条目"""
        item = self._get_selected_item()
        if not item:
            messagebox.showwarning("提示", "请先选择一个条目")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个条目吗？"):
            if self.db.delete_item(item.id):
                self.status_var.set("条目已删除")
                self._refresh_list()
    
    def _clear_all(self):
        """清空所有条目"""
        if messagebox.askyesno("确认", "确定要清空所有剪贴板历史吗？此操作不可恢复！"):
            if self.db.clear_all():
                self.status_var.set("所有数据已清空")
                self._refresh_list()
    
    def _show_stats(self):
        """显示统计信息"""
        stats = self.db.get_stats()
        
        stats_text = f"""
📊 SmartClip 统计信息

总条目数: {stats['total']}
收藏条目: {stats['favorites']}

按类型分布:
"""
        for content_type, count in stats['type_counts'].items():
            stats_text += f"  • {content_type}: {count}\n"
        
        messagebox.showinfo("统计信息", stats_text)
    
    def _on_close(self):
        """关闭窗口"""
        if self.monitor:
            self.monitor.stop()
        self.root.destroy()


def main():
    """主入口函数"""
    # 检查依赖
    missing_deps = []
    
    if not pyperclip:
        missing_deps.append("pyperclip")
    
    if missing_deps:
        print(f"缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install pyperclip")
        sys.exit(1)
    
    # 启动应用
    app = SmartClipApp()
    app.run()


if __name__ == "__main__":
    main()
