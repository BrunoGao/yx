#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优雅的模板同步脚本
极致码高尔夫风格，一键同步所有模板和静态资源
"""

import os
import shutil
import glob
from pathlib import Path

def sync_templates():
    """同步模板文件"""
    source_dir = "../ljwx-bigscreen/bigscreen/bigScreen"
    target_dir = "."
    
    # 核心页面文件
    core_pages = [
        'bigscreen_main.html',
        'personal.html', 
        'main.html',
        'optimized.html'
    ]
    
    # View页面文件
    view_pages = glob.glob(f"{source_dir}/templates/*_view.html")
    
    # 其他重要页面
    other_pages = [
        'alert.html',
        'message.html',
        'chart.html',
        'map.html',
        'track_view.html',
        'health_table.html',
        'health_trends.html',
        'health_main.html',
        'health_baseline.html',
        'user_health_data_analysis.html',
        'config_management.html',
        'user_profile.html',
        'user_view.html',
        'device_view.html'
    ]
    
    print("🔄 开始同步模板文件...")
    
    # 同步核心页面
    for page in core_pages:
        src = f"{source_dir}/templates/{page}"
        dst = f"{target_dir}/templates/bigscreen/{page}"
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ 同步核心页面: {page}")
    
    # 同步view页面
    for view_page in view_pages:
        page_name = os.path.basename(view_page)
        dst = f"{target_dir}/templates/bigscreen/{page_name}"
        shutil.copy2(view_page, dst)
        print(f"✅ 同步view页面: {page_name}")
    
    # 同步其他页面
    for page in other_pages:
        src = f"{source_dir}/templates/{page}"
        dst = f"{target_dir}/templates/bigscreen/{page}"
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ 同步其他页面: {page}")
    
    # 同步index子目录
    index_src = f"{source_dir}/templates/index"
    index_dst = f"{target_dir}/templates/bigscreen/index"
    if os.path.exists(index_src):
        if os.path.exists(index_dst):
            shutil.rmtree(index_dst)
        shutil.copytree(index_src, index_dst)
        print("✅ 同步index子目录")
    
    print("🎉 模板文件同步完成!")

def sync_static_resources():
    """同步静态资源文件"""
    source_dir = "../ljwx-bigscreen/bigscreen/bigScreen"
    target_dir = "."
    
    print("🔄 开始同步静态资源...")
    
    # 同步CSS文件
    css_src = f"{source_dir}/static/css"
    css_dst = f"{target_dir}/static/css"
    if os.path.exists(css_src):
        for css_file in glob.glob(f"{css_src}/*"):
            shutil.copy2(css_file, css_dst)
            print(f"✅ 同步CSS: {os.path.basename(css_file)}")
    
    # 同步JS文件
    js_src = f"{source_dir}/static/js"
    js_dst = f"{target_dir}/static/js"
    if os.path.exists(js_src):
        for js_file in glob.glob(f"{js_src}/*"):
            shutil.copy2(js_file, js_dst)
            print(f"✅ 同步JS: {os.path.basename(js_file)}")
    
    # 同步templates目录下的JS文件
    templates_js = glob.glob(f"{source_dir}/templates/*.js")
    for js_file in templates_js:
        shutil.copy2(js_file, js_dst)
        print(f"✅ 同步模板JS: {os.path.basename(js_file)}")
    
    print("🎉 静态资源同步完成!")

def create_directories():
    """创建必要的目录结构"""
    dirs = [
        "templates/bigscreen",
        "static/css",
        "static/js", 
        "static/images"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {dir_path}")

def main():
    """主函数"""
    print("🚀 开始优雅同步模板和静态资源...")
    
    # 创建目录结构
    create_directories()
    
    # 同步模板文件
    sync_templates()
    
    # 同步静态资源
    sync_static_resources()
    
    print("🎊 所有文件同步完成!")
    print("\n📋 可访问的页面:")
    print("  - /bigscreen/bigscreen_main  (大屏主页面)")
    print("  - /bigscreen/optimized       (优化页面)")
    print("  - /bigscreen/main            (主页面)")
    print("  - /bigscreen/personal        (个人页面)")
    print("  - /bigscreen/alert_view      (告警视图)")
    print("  - /bigscreen/message_view    (消息视图)")
    print("  - /bigscreen/device_view     (设备视图)")
    print("  - /bigscreen/user_view       (用户视图)")

if __name__ == "__main__":
    main() 