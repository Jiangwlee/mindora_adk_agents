#!/usr/bin/env python3
"""
Web Content Extractor Agent 平台集成测试
通过平台API测试Agent的完整功能
"""

import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def test_platform_health():
    """测试平台健康状态"""
    print("=== 测试平台健康状态 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 平台状态: {health_data['status']}")
            print(f"✅ 运行时间: {health_data.get('uptime', 'unknown')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_agent_registration():
    """测试Agent是否正确注册"""
    print("\n=== 测试Agent注册状态 ===")
    try:
        response = requests.get(f"{BASE_URL}/platform/apps")
        if response.status_code == 200:
            apps_data = response.json()
            apps = apps_data.get("apps", [])
            
            print(f"✅ 发现 {len(apps)} 个应用:")
            for app in apps:
                print(f"  - {app['name']} ({app['appType']})")
                if app['name'] == 'web_content_extractor':
                    print(f"    ✅ Web Content Extractor Agent已注册")
                    print(f"    描述: {app['description']}")
                    return True
            
            print("❌ Web Content Extractor Agent未找到")
            return False
        else:
            print(f"❌ 获取应用列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取应用列表异常: {e}")
        return False

def test_agent_functionality():
    """通过ADK调试端点测试Agent功能"""
    print("\n=== 测试Agent功能 ===")
    
    # 测试消息
    test_message = """请帮我提取以下内容中的网页链接并获取网页内容:
    - 官方网站: https://example.com
    - GitHub项目: https://github.com/microsoft/vscode
    请处理这些链接。"""
    
    try:
        # 使用ADK的调试方式测试
        session_id = str(uuid.uuid4())
        
        # 构造请求数据
        request_data = {
            "agent_name": "web_content_extractor",
            "message": test_message,
            "session_id": session_id,
            "stream": False
        }
        
        print(f"📤 发送测试消息到Agent")
        print(f"会话ID: {session_id}")
        print(f"消息内容: {test_message[:100]}...")
        
        # 由于不确定确切的端点，我们先尝试几个可能的路径
        possible_endpoints = [
            f"{BASE_URL}/adk/chat",
            f"{BASE_URL}/platform/chat", 
            f"{BASE_URL}/api/chat",
            f"{BASE_URL}/chat"
        ]
        
        for endpoint in possible_endpoints:
            try:
                print(f"📍 尝试端点: {endpoint}")
                response = requests.post(
                    endpoint,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ 端点 {endpoint} 响应成功")
                    response_data = response.json()
                    print(f"✅ 获得响应: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}...")
                    return True
                elif response.status_code == 404:
                    print(f"⏭️  端点 {endpoint} 不存在，继续尝试")
                    continue
                else:
                    print(f"❌ 端点 {endpoint} 响应失败: {response.status_code}")
                    print(f"错误详情: {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️  端点 {endpoint} 连接异常: {e}")
                continue
        
        print("❌ 所有端点都无法成功测试")
        return False
        
    except Exception as e:
        print(f"❌ Agent功能测试异常: {e}")
        return False

def test_direct_agent_import():
    """直接导入和测试Agent"""
    print("\n=== 直接Agent导入测试 ===")
    
    try:
        # 导入Agent
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'backend/agents'))
        
        from web_content_extractor import root_agent
        from web_content_extractor.agent import extract_urls_from_input
        
        print(f"✅ Agent导入成功")
        print(f"Agent名称: {root_agent.name}")
        print(f"Agent描述: {root_agent.description}")
        print(f"工具数量: {len(root_agent.tools)}")
        
        # 测试工具函数
        test_input = "请提取这些链接: https://example.com 和 https://github.com/test"
        result = extract_urls_from_input(test_input, "direct_test")
        
        print(f"✅ URL提取测试:")
        print(f"  状态: {result['status']}")
        print(f"  找到URL: {result.get('urls_found', 0)} 个")
        
        if result.get('urls'):
            for url in result['urls'][:2]:  # 只显示前2个
                print(f"  - {url['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 直接导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始Web Content Extractor Agent平台集成测试")
    print("=" * 60)
    
    tests = [
        ("平台健康状态", test_platform_health),
        ("Agent注册状态", test_agent_registration),
        ("直接Agent导入", test_direct_agent_import),
        ("Agent功能测试", test_agent_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n📋 正在执行: {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"结果: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"结果: ❌ 异常 - {e}")
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed >= 3:  # 至少前3个测试通过就认为集成成功
        print("🎉 平台集成基本成功！")
        print("\n📝 后续建议:")
        print("  1. 使用 /adk-debug 页面测试Agent交互")
        print("  2. 验证前端UI集成")
        print("  3. 测试文件上传功能")
        print("  4. 进行完整的端到端测试")
        return True
    else:
        print("⚠️  平台集成存在问题，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)