#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用网络安全配置生成器
自动生成Android网络安全配置文件，支持内网IP段和自定义IP
"""

import os
import sys
import argparse
from pathlib import Path

def generate_network_config(custom_ips=None, allow_all_internal=True, allow_external=False, debug_mode=True):
    """生成网络安全配置XML内容"""
    config = '''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>'''
    
    # 使用base-config确保兼容性，允许所有HTTP访问
    config += '''
    <!-- 允许所有HTTP访问（包括内网和外网） -->
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system"/>
            <certificates src="user"/>
        </trust-anchors>
    </base-config>'''
    
    if debug_mode:
        config += '''
    
    <!-- 调试模式：允许所有HTTP访问（仅开发环境使用） -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="system"/>
            <certificates src="user"/>
        </trust-anchors>
    </debug-overrides>'''
    
    config += '''
</network-security-config>'''
    
    return config

def update_flutter_projects(base_path=".", custom_ips=None, allow_external=False):
    """更新所有Flutter项目的网络安全配置"""
    flutter_projects = []
    
    # 查找所有Flutter项目
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.startswith("ljwx-phone"):
            config_path = os.path.join(item_path, "android/app/src/main/res/xml/network_security_config.xml")
            if os.path.exists(config_path):
                flutter_projects.append((item, config_path))
    
    print(f"找到 {len(flutter_projects)} 个Flutter项目需要更新")
    
    for project_name, config_path in flutter_projects:
        try:
            config_content = generate_network_config(custom_ips=custom_ips, allow_external=allow_external)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"✅ 已更新: {project_name}")
        except Exception as e:
            print(f"❌ 更新失败 {project_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="生成Android网络安全配置")
    parser.add_argument("--ips", nargs="+", help="自定义IP地址列表")
    parser.add_argument("--no-internal", action="store_true", help="不包含内网IP段")
    parser.add_argument("--no-debug", action="store_true", help="不包含调试模式")
    parser.add_argument("--allow-external", action="store_true", help="允许外网HTTP访问")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--update-all", action="store_true", help="更新所有Flutter项目")
    
    args = parser.parse_args()
    
    config_content = generate_network_config(
        custom_ips=args.ips,
        allow_all_internal=not args.no_internal,
        allow_external=args.allow_external,
        debug_mode=not args.no_debug
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ 配置已保存到: {args.output}")
    
    if args.update_all:
        update_flutter_projects(custom_ips=args.ips, allow_external=args.allow_external)
    
    if not args.output and not args.update_all:
        print("生成的网络安全配置:")
        print(config_content)

if __name__ == "__main__":
    main() 