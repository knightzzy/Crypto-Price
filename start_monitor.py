#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币监控系统启动脚本
提供简单的命令行界面来启动和管理监控系统
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = ['requests', 'sqlite3']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_config():
    """检查配置文件"""
    config_file = 'config.py'
    if not os.path.exists(config_file):
        print(f"⚠️ 未找到配置文件 {config_file}，将使用默认配置")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def test_webhook():
    """测试企业微信webhook连接"""
    try:
        import requests
        from config import WECHAT_WEBHOOK
        
        test_payload = {
            "msgtype": "text",
            "text": {
                "content": f"🧪 监控系统连接测试\n⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        response = requests.post(WECHAT_WEBHOOK, json=test_payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            print("✅ 企业微信webhook连接测试成功")
            return True
        else:
            print(f"❌ 企业微信webhook测试失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ webhook测试出错: {e}")
        return False

def start_basic_monitor():
    """启动基础版监控"""
    print("🚀 启动基础版加密货币监控系统...")
    try:
        subprocess.run([sys.executable, 'crypto_monitor.py'])
    except KeyboardInterrupt:
        print("\n⏹️ 监控系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def start_enhanced_monitor():
    """启动增强版监控"""
    print("🚀 启动增强版加密货币监控系统...")
    try:
        subprocess.run([sys.executable, 'enhanced_monitor.py'])
    except KeyboardInterrupt:
        print("\n⏹️ 监控系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def show_status():
    """显示系统状态"""
    print("📊 系统状态检查")
    print("=" * 50)
    
    # 检查文件
    files_to_check = [
        'crypto_monitor.py',
        'enhanced_monitor.py', 
        'config.py',
        'requirements.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} (缺失)")
    
    # 检查数据库
    if os.path.exists('crypto_monitor.db'):
        size = os.path.getsize('crypto_monitor.db')
        print(f"✅ crypto_monitor.db ({size} bytes)")
    else:
        print("ℹ️ crypto_monitor.db (未创建)")
    
    # 检查日志
    if os.path.exists('crypto_monitor.log'):
        size = os.path.getsize('crypto_monitor.log')
        print(f"✅ crypto_monitor.log ({size} bytes)")
    else:
        print("ℹ️ crypto_monitor.log (未创建)")

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='加密货币监控系统启动器')
    parser.add_argument('--mode', choices=['basic', 'enhanced'], default='enhanced',
                       help='选择监控模式 (默认: enhanced)')
    parser.add_argument('--test', action='store_true', help='测试webhook连接')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('--install', action='store_true', help='安装依赖包')
    parser.add_argument('--check', action='store_true', help='检查系统环境')
    parser.add_argument('--demo-reload', action='store_true', help='演示配置自动重载功能')
    parser.add_argument('--test-reload', action='store_true', help='测试配置自动重载功能')
    
    args = parser.parse_args()
    
    print("🤖 加密货币监控系统启动器")
    print("=" * 50)
    
    if args.install:
        install_dependencies()
        return
    
    if args.status:
        show_status()
        return
    
    if args.check:
        print("🔍 系统环境检查")
        print("-" * 30)
        deps_ok = check_dependencies()
        config_ok = check_config()
        
        if deps_ok and config_ok:
            print("\n✅ 系统环境检查通过，可以启动监控")
        else:
            print("\n❌ 系统环境检查未通过，请先解决问题")
        return
    
    if args.test:
        print("🧪 测试企业微信连接")
        print("-" * 30)
        test_webhook()
        return
    
    if args.demo_reload:
        print("🎬 启动配置自动重载演示...")
        os.system("python demo_config_reload.py")
        return
    
    if args.test_reload:
        print("🧪 启动配置自动重载测试...")
        os.system("python test_config_reload.py")
        return
    
    # 启动前检查
    print("🔍 启动前检查...")
    if not check_dependencies():
        print("请先安装依赖: python start_monitor.py --install")
        return
    
    check_config()
    
    # 启动监控
    if args.mode == 'basic':
        start_basic_monitor()
    else:
        start_enhanced_monitor()

if __name__ == "__main__":
    main()