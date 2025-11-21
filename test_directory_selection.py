#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 测试目录选择功能
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_plugin_cleaner import SmartPluginCleaner

def test_directory_selection():
    """测试目录选择功能"""
    print("=== 测试目录自动识别功能 ===\n")
    
    # 测试自动查找
    found_dirs = SmartPluginCleaner.find_eclipse_plugin_dirs()
    
    print(f"自动找到 {len(found_dirs)} 个可能的插件目录:")
    for i, dir_path in enumerate(found_dirs, 1):
        print(f"  {i}. {dir_path}")
    
    # 测试当前目录
    current_dir = os.getcwd()
    print(f"\n当前目录: {current_dir}")
    
    if os.path.exists(current_dir):
        print("当前目录存在")
        files = os.listdir(current_dir)[:5]
        print(f"当前目录包含: {', '.join(files)}")
    else:
        print("当前目录不存在")

if __name__ == "__main__":
    test_directory_selection()