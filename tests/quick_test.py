#!/usr/bin/env python3
"""
快速测试脚本 - 用于快速验证服务器基本功能
"""

import json
import requests
import time
import sys

def quick_test():
    """快速测试服务器基本功能"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始快速测试...")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    tests = []
    
    # 1. 健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查: {data.get('status', 'unknown')}")
            tests.append(True)
        else:
            print(f"❌ 健康检查: HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ 健康检查: {e}")
        tests.append(False)
    
    # 2. 应用列表
    try:
        response = requests.get(f"{base_url}/list-apps", timeout=5)
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ 应用列表: {len(apps)} 个应用")
            print(f"   应用: {apps}")
            tests.append(True)
        else:
            print(f"❌ 应用列表: HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ 应用列表: {e}")
        tests.append(False)
    
    # 3. 平台应用
    try:
        response = requests.get(f"{base_url}/platform/apps", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 平台应用: 成功")
            tests.append(True)
        else:
            print(f"❌ 平台应用: HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ 平台应用: {e}")
        tests.append(False)
    
    # 4. 会话创建
    try:
        app_name = "adk_demo"
        user_id = "test_user"
        response = requests.post(f"{base_url}/apps/{app_name}/users/{user_id}/sessions", timeout=5)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("id", "unknown")
            print(f"✅ 会话创建: {session_id}")
            tests.append(True)
            
            # 5. 智能体运行
            try:
                run_data = {
                    "appName": app_name,
                    "userId": user_id,
                    "sessionId": session_id,
                    "newMessage": {
                        "role": "user",
                        "parts": [{"text": "Hello"}]
                    }
                }
                response = requests.post(f"{base_url}/run", json=run_data, timeout=30)
                if response.status_code == 200:
                    events = response.json()
                    print(f"✅ 智能体运行: {len(events)} 个事件")
                    tests.append(True)
                else:
                    print(f"❌ 智能体运行: HTTP {response.status_code}")
                    tests.append(False)
            except Exception as e:
                print(f"❌ 智能体运行: {e}")
                tests.append(False)
                
        else:
            print(f"❌ 会话创建: HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ 会话创建: {e}")
        tests.append(False)
    
    # 结果统计
    print("=" * 50)
    passed = sum(tests)
    total = len(tests)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(quick_test())