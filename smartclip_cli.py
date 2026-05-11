#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartClip CLI - 命令行版本
SmartClip CLI - Command Line Interface

用于无GUI环境下的剪贴板管理和查询
"""

import sys
import os
import argparse
import json
from typing import Optional

# 导入核心模块
from smartclip import (
    DatabaseManager, ContentClassifier, ContentType,
    ClipboardItem, pyperclip
)


def print_colored(text: str, color: str = "white"):
    """打印彩色文本"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")


def cmd_add(args):
    """添加内容到剪贴板历史"""
    db = DatabaseManager()
    
    content = args.content
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print_colored(f"错误: 无法读取文件 - {e}", "red")
            return
    
    if not content:
        print_colored("错误: 内容不能为空", "red")
        return
    
    import hashlib
    from datetime import datetime
    
    content_hash = hashlib.md5(content.encode()).hexdigest()
    content_type = ContentClassifier.classify(content)
    tags = ContentClassifier.extract_tags(content, content_type)
    now = datetime.now().isoformat()
    
    item = ClipboardItem(
        id=content_hash[:16],
        content=content,
        content_type=content_type,
        created_at=now,
        updated_at=now,
        tags=tags,
        favorite=args.favorite,
        usage_count=0,
        source_app="cli",
        hash=content_hash
    )
    
    if db.add_item(item):
        print_colored(f"✓ 已添加 [{content_type.value}] {len(content)} 字符", "green")
        if tags:
            print_colored(f"  标签: {', '.join(tags)}", "cyan")
    else:
        print_colored("✗ 添加失败", "red")


def cmd_list(args):
    """列出剪贴板历史"""
    db = DatabaseManager()
    
    items = db.get_items(
        limit=args.limit,
        content_type=ContentType(args.type) if args.type else None,
        favorite_only=args.favorite
    )
    
    if not items:
        print_colored("剪贴板历史为空", "yellow")
        return
    
    type_icons = {
        ContentType.TEXT: "📝",
        ContentType.CODE: "💻",
        ContentType.URL: "🔗",
        ContentType.EMAIL: "📧",
        ContentType.IMAGE: "🖼️",
        ContentType.FILE_PATH: "📁",
        ContentType.COMMAND: "⚡",
        ContentType.UNKNOWN: "📄"
    }
    
    print_colored(f"\n{'='*80}", "blue")
    print_colored(f"  共 {len(items)} 条记录", "cyan")
    print_colored(f"{'='*80}\n", "blue")
    
    for i, item in enumerate(items, 1):
        icon = type_icons.get(item.content_type, "📄")
        favorite = "⭐ " if item.favorite else "   "
        content = item.content[:60] + "..." if len(item.content) > 60 else item.content
        content = content.replace("\n", " ")
        
        print_colored(f"{i:3d}. {favorite}{icon} [{item.content_type.value:8s}] {content}", "white")
        
        if args.verbose and item.tags:
            print_colored(f"     标签: {', '.join(item.tags)}", "cyan")
        if args.verbose:
            print_colored(f"     时间: {item.created_at[:19]}", "magenta")
            print()


def cmd_search(args):
    """搜索剪贴板历史"""
    db = DatabaseManager()
    
    items = db.search_items(args.query, limit=args.limit)
    
    if not items:
        print_colored(f"未找到包含 '{args.query}' 的内容", "yellow")
        return
    
    print_colored(f"\n找到 {len(items)} 条匹配记录:\n", "green")
    
    for i, item in enumerate(items, 1):
        content = item.content[:80] + "..." if len(item.content) > 80 else item.content
        content = content.replace("\n", " ")
        favorite = "⭐" if item.favorite else "  "
        
        print_colored(f"{i:2d}. {favorite} [{item.content_type.value}] {content}", "white")


def cmd_get(args):
    """获取指定内容并复制到剪贴板"""
    db = DatabaseManager()
    
    items = db.search_items(args.query, limit=1)
    
    if not items:
        print_colored(f"未找到: {args.query}", "red")
        return
    
    item = items[0]
    
    if pyperclip:
        pyperclip.copy(item.content)
        db.increment_usage(item.id)
        print_colored(f"✓ 已复制到剪贴板 [{item.content_type.value}]", "green")
        print_colored(f"  {item.content[:100]}...", "cyan")
    else:
        print_colored(item.content, "white")


def cmd_stats(args):
    """显示统计信息"""
    db = DatabaseManager()
    stats = db.get_stats()
    
    print_colored("\n📊 SmartClip 统计信息", "cyan")
    print_colored("=" * 40, "blue")
    print_colored(f"总条目数: {stats['total']}", "white")
    print_colored(f"收藏条目: {stats['favorites']}", "yellow")
    
    if stats['type_counts']:
        print_colored("\n按类型分布:", "cyan")
        for content_type, count in sorted(stats['type_counts'].items(), key=lambda x: -x[1]):
            bar = "█" * (count * 20 // max(stats['type_counts'].values()))
            print_colored(f"  {content_type:10s}: {bar} {count}", "white")


def cmd_export(args):
    """导出数据"""
    db = DatabaseManager()
    items = db.get_items(limit=10000)
    
    data = {
        "exported_at": __import__('datetime').datetime.now().isoformat(),
        "total": len(items),
        "items": [item.to_dict() for item in items]
    }
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print_colored(f"✓ 已导出 {len(items)} 条记录到 {args.output}", "green")
    except Exception as e:
        print_colored(f"✗ 导出失败: {e}", "red")


def cmd_clear(args):
    """清空数据"""
    if not args.force:
        confirm = input("确定要清空所有数据吗？输入 'yes' 确认: ")
        if confirm.lower() != 'yes':
            print_colored("操作已取消", "yellow")
            return
    
    db = DatabaseManager()
    if db.clear_all():
        print_colored("✓ 所有数据已清空", "green")
    else:
        print_colored("✗ 清空失败", "red")


def main():
    parser = argparse.ArgumentParser(
        prog='smartclip',
        description='SmartClip - AI驱动的智能剪贴板管理器 (CLI)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s list                    # 列出最近100条记录
  %(prog)s list -l 20 -f           # 列出最近20条收藏记录
  %(prog)s search "python"         # 搜索包含python的内容
  %(prog)s add "Hello World"       # 添加内容
  %(prog)s get "function"          # 获取并复制包含function的内容
  %(prog)s stats                   # 显示统计信息
  %(prog)s export backup.json      # 导出数据
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='列出剪贴板历史')
    list_parser.add_argument('-l', '--limit', type=int, default=100, help='限制数量')
    list_parser.add_argument('-t', '--type', choices=[t.value for t in ContentType], help='按类型筛选')
    list_parser.add_argument('-f', '--favorite', action='store_true', help='仅显示收藏')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    list_parser.set_defaults(func=cmd_list)
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索剪贴板历史')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('-l', '--limit', type=int, default=50, help='限制数量')
    search_parser.set_defaults(func=cmd_search)
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加内容')
    add_parser.add_argument('content', nargs='?', help='内容文本')
    add_parser.add_argument('-f', '--file', help='从文件读取')
    add_parser.add_argument('--favorite', action='store_true', help='标记为收藏')
    add_parser.set_defaults(func=cmd_add)
    
    # get 命令
    get_parser = subparsers.add_parser('get', help='获取并复制到剪贴板')
    get_parser.add_argument('query', help='搜索关键词')
    get_parser.set_defaults(func=cmd_get)
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    stats_parser.set_defaults(func=cmd_stats)
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出数据')
    export_parser.add_argument('output', help='输出文件路径')
    export_parser.set_defaults(func=cmd_export)
    
    # clear 命令
    clear_parser = subparsers.add_parser('clear', help='清空所有数据')
    clear_parser.add_argument('--force', action='store_true', help='强制清空，不提示')
    clear_parser.set_defaults(func=cmd_clear)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
