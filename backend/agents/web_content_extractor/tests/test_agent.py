"""
测试文件：Web Content Extractor Agent 核心功能测试
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from agent import (
    extract_urls_from_input,
    extract_web_content, 
    format_final_output
)

class TestWebContentExtractorAgent(unittest.TestCase):
    """Web Content Extractor Agent 测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.sample_text = """
        请访问我们的官网 https://example.com 了解更多信息。
        也可以查看项目页面 https://github.com/test/repo 获取代码。
        联系我们：www.contact.com
        """
        
        self.sample_urls = [
            {"url": "https://example.com", "source": "test", "index": 1},
            {"url": "https://github.com/test/repo", "source": "test", "index": 2}
        ]
    
    def test_extract_urls_from_text_input(self):
        """测试从文本输入中提取URL"""
        result = extract_urls_from_input(self.sample_text, "test_source")
        
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["urls_found"], 0)
        self.assertIsInstance(result["urls"], list)
        
        # 验证提取到的URL
        extracted_urls = [url["url"] for url in result["urls"]]
        self.assertIn("https://example.com", extracted_urls)
        self.assertIn("https://github.com/test/repo", extracted_urls)
    
    def test_extract_urls_error_handling(self):
        """测试URL提取的错误处理"""
        # 测试空输入
        result = extract_urls_from_input("", "test")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["urls_found"], 0)
    
    def test_web_content_extraction(self):
        """测试网页内容提取"""
        urls_data = {
            "urls": self.sample_urls,
            "source": "test"
        }
        
        result = extract_web_content(urls_data)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_processed"], 2)
        self.assertIsInstance(result["results"], list)
        
        # 验证结果结构
        for res in result["results"]:
            self.assertIn("url", res)
            self.assertIn("status", res)
            if res["status"] == "success":
                self.assertIn("title", res)
                self.assertIn("content", res)
    
    def test_web_content_extraction_empty_urls(self):
        """测试空URL列表的处理"""
        urls_data = {"urls": [], "source": "test"}
        result = extract_web_content(urls_data)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("没有找到有效的URL", result["error_message"])
    
    def test_format_final_output(self):
        """测试最终输出格式化"""
        # 模拟提取结果数据
        extraction_data = {
            "source": "test",
            "results": [
                {
                    "url": "https://example.com",
                    "status": "success",
                    "title": "测试页面",
                    "content": "这是测试内容",
                    "word_count": 100,
                    "processing_time_ms": 1500,
                    "timestamp": 1234567890
                },
                {
                    "url": "https://error.com",
                    "status": "error",
                    "error_message": "连接失败",
                    "timestamp": 1234567890
                }
            ]
        }
        
        result = format_final_output(extraction_data)
        
        # 验证输出结构
        self.assertIn("timestamp", result)
        self.assertIn("processing_info", result)
        self.assertIn("results", result)
        self.assertIn("errors", result)
        self.assertIn("metadata", result)
        
        # 验证处理信息
        proc_info = result["processing_info"]
        self.assertEqual(proc_info["total_urls"], 2)
        self.assertEqual(proc_info["successful_count"], 1)
        self.assertEqual(proc_info["failed_count"], 1)
        self.assertEqual(proc_info["success_rate"], 50.0)
    
    def test_format_output_error_handling(self):
        """测试输出格式化的错误处理"""
        # 测试无效数据
        result = format_final_output({})
        
        self.assertIn("processing_info", result)
        self.assertEqual(result["processing_info"]["total_urls"], 0)
    
    def test_end_to_end_workflow(self):
        """测试端到端的工作流程"""
        # Step 1: 提取URL
        url_result = extract_urls_from_input(self.sample_text, "e2e_test")
        self.assertEqual(url_result["status"], "success")
        
        # Step 2: 提取网页内容
        content_result = extract_web_content(url_result)
        self.assertEqual(content_result["status"], "success")
        
        # Step 3: 格式化输出
        final_result = format_final_output(content_result)
        self.assertIn("processing_info", final_result)
        self.assertIn("results", final_result)
        
        # 验证最终结果可以序列化为JSON
        try:
            json_output = json.dumps(final_result, ensure_ascii=False, indent=2)
            self.assertIsInstance(json_output, str)
            self.assertGreater(len(json_output), 0)
        except Exception as e:
            self.fail(f"JSON序列化失败: {e}")

class TestAgentConfiguration(unittest.TestCase):
    """测试Agent配置"""
    
    def test_config_file_exists(self):
        """测试配置文件是否存在"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config.json"
        )
        self.assertTrue(os.path.exists(config_path), "配置文件不存在")
    
    def test_config_file_valid_json(self):
        """测试配置文件是否为有效JSON"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config.json"
        )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 验证必需字段
            required_fields = ["name", "description", "app_type"]
            for field in required_fields:
                self.assertIn(field, config, f"配置文件缺少必需字段: {field}")
                
            # 验证app_type
            self.assertEqual(config["app_type"], "custom")
            
        except Exception as e:
            self.fail(f"配置文件解析失败: {e}")

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)