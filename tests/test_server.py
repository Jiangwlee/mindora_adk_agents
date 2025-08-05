#!/usr/bin/env python3
"""
Mindora ADK Agents 服务器测试用例
用于验证所有 API 端点的功能
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
import requests
import logging
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKServerTester:
    """ADK 服务器测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # 测试数据
        self.test_user_id = "test_user"
        self.test_app_name = "adk_demo"
        self.test_session_id = None
        
    def test_health_check(self) -> Dict[str, Any]:
        """测试健康检查端点"""
        logger.info("🧪 测试健康检查端点 /health")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = {
                "test": "health_check",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": f"{self.base_url}/health"
            }
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    result["details"] = "服务器状态正常"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = f"服务器状态异常: {data.get('status')}"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "health_check",
                "status": "❌ 失败",
                "error": str(e),
                "details": "连接失败或服务器未启动"
            }
    
    def test_list_apps(self) -> Dict[str, Any]:
        """测试应用列表端点"""
        logger.info("🧪 测试应用列表端点 /list-apps")
        
        try:
            response = self.session.get(f"{self.base_url}/list-apps")
            result = {
                "test": "list_apps",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": f"{self.base_url}/list-apps"
            }
            
            if response.status_code == 200:
                apps = response.json()
                if isinstance(apps, list) and len(apps) > 0:
                    result["details"] = f"找到 {len(apps)} 个应用: {apps}"
                    # 检查是否包含预期应用
                    expected_apps = ["adk_demo", "assistant", "data_analyst"]
                    missing_apps = [app for app in expected_apps if app not in apps]
                    if missing_apps:
                        result["status"] = "⚠️ 警告"
                        result["details"] += f" | 缺少应用: {missing_apps}"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "应用列表为空或格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "list_apps",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_platform_apps(self) -> Dict[str, Any]:
        """测试平台应用端点"""
        logger.info("🧪 测试平台应用端点 /platform/apps")
        
        try:
            response = self.session.get(f"{self.base_url}/platform/apps")
            result = {
                "test": "platform_apps",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": f"{self.base_url}/platform/apps"
            }
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "apps" in data:
                    apps = data["apps"]
                    result["details"] = f"平台返回 {len(apps)} 个应用"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "响应格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "platform_apps",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_create_session(self) -> Dict[str, Any]:
        """测试会话创建端点"""
        logger.info(f"🧪 测试会话创建端点 /apps/{self.test_app_name}/users/{self.test_user_id}/sessions")
        
        try:
            url = f"{self.base_url}/apps/{self.test_app_name}/users/{self.test_user_id}/sessions"
            response = self.session.post(url)
            result = {
                "test": "create_session",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": url
            }
            
            if response.status_code == 200:
                session_data = response.json()
                if isinstance(session_data, dict) and "id" in session_data:
                    self.test_session_id = session_data["id"]
                    result["details"] = f"会话创建成功: {self.test_session_id}"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "会话响应格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "create_session",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_list_sessions(self) -> Dict[str, Any]:
        """测试会话列表端点"""
        logger.info(f"🧪 测试会话列表端点 /apps/{self.test_app_name}/users/{self.test_user_id}/sessions")
        
        try:
            url = f"{self.base_url}/apps/{self.test_app_name}/users/{self.test_user_id}/sessions"
            response = self.session.get(url)
            result = {
                "test": "list_sessions",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": url
            }
            
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list):
                    result["details"] = f"找到 {len(sessions)} 个会话"
                    if self.test_session_id:
                        session_ids = [s.get("id") for s in sessions if isinstance(s, dict) and "id" in s]
                        if self.test_session_id in session_ids:
                            result["details"] += f" | 包含测试会话: {self.test_session_id}"
                        else:
                            result["status"] = "⚠️ 警告"
                            result["details"] += f" | 未找到测试会话: {self.test_session_id}"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "会话列表格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "list_sessions",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_get_session(self) -> Dict[str, Any]:
        """测试获取会话详情端点"""
        if not self.test_session_id:
            return {
                "test": "get_session",
                "status": "⚠️ 跳过",
                "details": "没有可用的会话ID"
            }
        
        logger.info(f"🧪 测试获取会话详情端点 /apps/{self.test_app_name}/users/{self.test_user_id}/sessions/{self.test_session_id}")
        
        try:
            url = f"{self.base_url}/apps/{self.test_app_name}/users/{self.test_user_id}/sessions/{self.test_session_id}"
            response = self.session.get(url)
            result = {
                "test": "get_session",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": url
            }
            
            if response.status_code == 200:
                session_data = response.json()
                if isinstance(session_data, dict) and "id" in session_data:
                    result["details"] = f"会话详情获取成功: {session_data.get('id')}"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "会话详情格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "get_session",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_agent_run(self) -> Dict[str, Any]:
        """测试智能体运行端点"""
        if not self.test_session_id:
            return {
                "test": "agent_run",
                "status": "⚠️ 跳过",
                "details": "没有可用的会话ID"
            }
        
        logger.info(f"🧪 测试智能体运行端点 /run")
        
        try:
            request_data = {
                "appName": self.test_app_name,
                "userId": self.test_user_id,
                "sessionId": self.test_session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": "Hello, please introduce yourself"}]
                }
            }
            
            response = self.session.post(f"{self.base_url}/run", json=request_data)
            result = {
                "test": "agent_run",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": f"{self.base_url}/run"
            }
            
            if response.status_code == 200:
                events = response.json()
                if isinstance(events, list):
                    result["details"] = f"智能体运行成功，生成 {len(events)} 个事件"
                    # 检查事件类型
                    event_types = [e.get("author", "unknown") for e in events if isinstance(e, dict)]
                    result["details"] += f" | 事件作者: {event_types}"
                else:
                    result["status"] = "⚠️ 警告"
                    result["details"] = "响应格式不正确"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "agent_run",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_agent_run_sse(self) -> Dict[str, Any]:
        """测试智能体运行SSE端点"""
        if not self.test_session_id:
            return {
                "test": "agent_run_sse",
                "status": "⚠️ 跳过",
                "details": "没有可用的会话ID"
            }
        
        logger.info(f"🧪 测试智能体运行SSE端点 /run_sse")
        
        try:
            request_data = {
                "appName": self.test_app_name,
                "userId": self.test_user_id,
                "sessionId": self.test_session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": "What is 2+2?"}]
                },
                "streaming": True
            }
            
            response = self.session.post(f"{self.base_url}/run_sse", json=request_data, stream=True)
            result = {
                "test": "agent_run_sse",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "url": f"{self.base_url}/run_sse"
            }
            
            if response.status_code == 200:
                # 读取SSE流
                events = []
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            events.append(line[6:])  # 移除 'data: ' 前缀
                
                result["details"] = f"SSE流连接成功，收到 {len(events)} 个事件"
                result["response"] = events[:3] if events else []  # 显示前3个事件
            else:
                result["details"] = f"HTTP {response.status_code}"
                result["response"] = response.text
                
            return result
            
        except Exception as e:
            return {
                "test": "agent_run_sse",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_debug_trace_session(self) -> Dict[str, Any]:
        """测试调试追踪端点"""
        if not self.test_session_id:
            return {
                "test": "debug_trace_session",
                "status": "⚠️ 跳过",
                "details": "没有可用的会话ID"
            }
        
        logger.info(f"🧪 测试调试追踪端点 /debug/trace/session/{self.test_session_id}")
        
        try:
            url = f"{self.base_url}/debug/trace/session/{self.test_session_id}"
            response = self.session.get(url)
            result = {
                "test": "debug_trace_session",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": url
            }
            
            if response.status_code == 200:
                trace_data = response.json()
                if isinstance(trace_data, list):
                    result["details"] = f"追踪数据获取成功，包含 {len(trace_data)} 个span"
                else:
                    result["details"] = "追踪数据获取成功"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "debug_trace_session",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def test_artifacts(self) -> Dict[str, Any]:
        """测试制品端点"""
        if not self.test_session_id:
            return {
                "test": "artifacts",
                "status": "⚠️ 跳过",
                "details": "没有可用的会话ID"
            }
        
        logger.info(f"🧪 测试制品端点 /apps/{self.test_app_name}/users/{self.test_user_id}/sessions/{self.test_session_id}/artifacts")
        
        try:
            url = f"{self.base_url}/apps/{self.test_app_name}/users/{self.test_user_id}/sessions/{self.test_session_id}/artifacts"
            response = self.session.get(url)
            result = {
                "test": "artifacts",
                "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "url": url
            }
            
            if response.status_code == 200:
                artifacts = response.json()
                if isinstance(artifacts, list):
                    result["details"] = f"制品列表获取成功，包含 {len(artifacts)} 个制品"
                else:
                    result["details"] = "制品列表获取成功"
            else:
                result["details"] = f"HTTP {response.status_code}"
                
            return result
            
        except Exception as e:
            return {
                "test": "artifacts",
                "status": "❌ 失败",
                "error": str(e),
                "details": "请求失败"
            }
    
    def run_all_tests(self) -> None:
        """运行所有测试"""
        logger.info("🚀 开始运行所有测试用例")
        logger.info("=" * 60)
        
        tests = [
            self.test_health_check,
            self.test_list_apps,
            self.test_platform_apps,
            self.test_create_session,
            self.test_list_sessions,
            self.test_get_session,
            self.test_agent_run,
            self.test_agent_run_sse,
            self.test_debug_trace_session,
            self.test_artifacts
        ]
        
        results = []
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
                logger.info(f"✅ {result['test']}: {result['status']}")
                if 'details' in result:
                    logger.info(f"   详情: {result['details']}")
            except Exception as e:
                logger.error(f"❌ 测试 {test_func.__name__} 失败: {e}")
                results.append({
                    "test": test_func.__name__,
                    "status": "❌ 失败",
                    "error": str(e)
                })
        
        # 输出测试结果摘要
        logger.info("=" * 60)
        logger.info("📊 测试结果摘要")
        logger.info("=" * 60)
        
        passed = sum(1 for r in results if r['status'] == '✅ 通过')
        failed = sum(1 for r in results if r['status'] == '❌ 失败')
        warnings = sum(1 for r in results if r['status'] == '⚠️ 警告')
        skipped = sum(1 for r in results if r['status'] == '⚠️ 跳过')
        
        logger.info(f"✅ 通过: {passed}")
        logger.info(f"❌ 失败: {failed}")
        logger.info(f"⚠️ 警告: {warnings}")
        logger.info(f"⚠️ 跳过: {skipped}")
        logger.info(f"📈 总计: {len(results)}")
        
        # 输出详细结果
        logger.info("\n📋 详细测试结果:")
        for result in results:
            status_icon = "✅" if result['status'] == '✅ 通过' else "❌" if result['status'] == '❌ 失败' else "⚠️"
            logger.info(f"{status_icon} {result['test']}: {result['status']}")
            if 'details' in result:
                logger.info(f"   {result['details']}")
            if 'error' in result:
                logger.info(f"   错误: {result['error']}")
        
        # 保存结果到文件
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n💾 测试结果已保存到 test_results.json")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ADK 服务器测试工具')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='服务器URL (默认: http://localhost:8000)')
    parser.add_argument('--app', default='adk_demo', 
                       help='测试应用名称 (默认: adk_demo)')
    parser.add_argument('--user', default='test_user', 
                       help='测试用户ID (默认: test_user)')
    
    args = parser.parse_args()
    
    # 创建测试器实例
    tester = ADKServerTester(base_url=args.url)
    tester.test_app_name = args.app
    tester.test_user_id = args.user
    
    # 运行测试
    results = tester.run_all_tests()
    
    # 返回适当的退出码
    failed_tests = sum(1 for r in results if r['status'] == '❌ 失败')
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    exit(main())