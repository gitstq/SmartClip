#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartClip 构建脚本
支持多平台打包
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    print(result.stdout)
    return True


def clean_build():
    """清理构建目录"""
    dirs_to_remove = ['build', 'dist', '__pycache__', '*.spec']
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"已删除目录: {path}")
            elif path.is_file():
                path.unlink()
                print(f"已删除文件: {path}")


def install_deps():
    """安装依赖"""
    print("安装依赖...")
    return run_command(f"{sys.executable} -m pip install -r requirements.txt")


def build_windows():
    """构建Windows版本"""
    print("构建 Windows 版本...")
    
    # 检查pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("安装 PyInstaller...")
        run_command(f"{sys.executable} -m pip install pyinstaller")
    
    # 构建GUI版本
    cmd = (
        f"pyinstaller --noconfirm --onefile --windowed "
        f"--name SmartClip "
        f"--icon=assets/icon.ico "
        f"--add-data 'assets;assets' "
        f"smartclip.py"
    )
    
    if run_command(cmd):
        print("✓ Windows GUI 版本构建成功")
        print(f"  输出: dist/SmartClip.exe")
        return True
    return False


def build_linux():
    """构建Linux版本"""
    print("构建 Linux 版本...")
    
    try:
        import PyInstaller
    except ImportError:
        print("安装 PyInstaller...")
        run_command(f"{sys.executable} -m pip install pyinstaller")
    
    # 构建GUI版本
    cmd = (
        f"pyinstaller --noconfirm --onefile "
        f"--name smartclip "
        f"smartclip.py"
    )
    
    if run_command(cmd):
        print("✓ Linux 版本构建成功")
        print(f"  输出: dist/smartclip")
        return True
    return False


def build_macos():
    """构建macOS版本"""
    print("构建 macOS 版本...")
    
    try:
        import PyInstaller
    except ImportError:
        print("安装 PyInstaller...")
        run_command(f"{sys.executable} -m pip install pyinstaller")
    
    # 构建.app bundle
    cmd = (
        f"pyinstaller --noconfirm --onefile --windowed "
        f"--name SmartClip "
        f"--icon=assets/icon.icns "
        f"smartclip.py"
    )
    
    if run_command(cmd):
        print("✓ macOS 版本构建成功")
        print(f"  输出: dist/SmartClip.app")
        return True
    return False


def build_cli():
    """构建CLI版本"""
    print("构建 CLI 版本...")
    
    try:
        import PyInstaller
    except ImportError:
        print("安装 PyInstaller...")
        run_command(f"{sys.executable} -m pip install pyinstaller")
    
    cmd = (
        f"pyinstaller --noconfirm --onefile "
        f"--name smartclip-cli "
        f"smartclip_cli.py"
    )
    
    if run_command(cmd):
        print("✓ CLI 版本构建成功")
        return True
    return False


def create_installer():
    """创建安装程序（平台特定）"""
    system = platform.system()
    
    if system == "Windows":
        print("创建 Windows 安装程序...")
        # 需要NSIS或其他安装程序制作工具
        print("请手动使用 Inno Setup 或 NSIS 创建安装程序")
    
    elif system == "Linux":
        print("创建 Linux 软件包...")
        # 可以创建deb/rpm包
        print("请手动创建 deb/rpm 包")
    
    elif system == "Darwin":
        print("创建 macOS DMG...")
        # 使用create-dmg工具
        cmd = "create-dmg dist/SmartClip.app dist/"
        run_command(cmd)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartClip 构建脚本')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    parser.add_argument('--all', action='store_true', help='构建所有版本')
    parser.add_argument('--gui', action='store_true', help='构建GUI版本')
    parser.add_argument('--cli', action='store_true', help='构建CLI版本')
    parser.add_argument('--installer', action='store_true', help='创建安装程序')
    
    args = parser.parse_args()
    
    # 清理
    if args.clean:
        clean_build()
        return
    
    # 安装依赖
    install_deps()
    
    system = platform.system()
    success = True
    
    # 构建
    if args.all or args.gui:
        if system == "Windows":
            success = build_windows() and success
        elif system == "Linux":
            success = build_linux() and success
        elif system == "Darwin":
            success = build_macos() and success
    
    if args.all or args.cli:
        success = build_cli() and success
    
    if args.installer:
        create_installer()
    
    if not (args.all or args.gui or args.cli or args.installer):
        parser.print_help()
    
    if success:
        print("\n✓ 构建完成!")
    else:
        print("\n✗ 构建失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
