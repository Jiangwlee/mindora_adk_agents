#!/usr/bin/env python3
"""
简单的功能测试脚本：验证Web Content Extractor Agent的基本功能
"""

import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_url_extraction():
    """测试URL提取功能"""
    print("\n=== 测试URL提取功能 ===")
    
    from tools.document_processor import extract_urls_from_text, validate_urls
    
    # 测试文本
    test_text = """
    请访问我们的官网 https://example.com 了解更多信息。
    也可以查看项目页面 https://github.com/test/repo 获取代码。
    联系我们：www.contact.com 或 http://support.test.org
    """
    
    try:
        # 提取URL
        urls = extract_urls_from_text(test_text)
        print(f"提取到 {len(urls)} 个URL:")
        for url in urls:
            print(f"  - {url['url']} (来源: {url['source']})")
        
        # 验证URL
        validated = validate_urls(urls)
        print(f"验证后有效URL数量: {len(validated)}")
        
        return len(validated) > 0
    except Exception as e:
        print(f"URL提取测试失败: {e}")
        return False

def test_web_crawling():
    """测试网页爬取功能"""
    print("\n=== 测试网页爬取功能 ===")
    
    from tools.web_crawler import crawl_multiple_urls
    
    # 测试URL
    test_urls = [
        {"url": "https://example.com", "source": "test", "index": 1},
        {"url": "https://httpbin.org/html", "source": "test", "index": 2}
    ]
    
    try:
        results = crawl_multiple_urls(test_urls, max_concurrent=2)
        print(f"爬取结果数量: {len(results)}")
        
        for result in results:
            status = result.get('status', 'unknown')
            url = result.get('url', 'unknown')
            print(f"  - {url}: {status}")
            
            if status == 'success':
                title = result.get('title', 'No title')
                word_count = result.get('word_count', 0)
                print(f"    标题: {title}")
                print(f"    字数: {word_count}")
        
        successful_count = len([r for r in results if r.get('status') == 'success'])
        return successful_count > 0
    except Exception as e:
        print(f"网页爬取测试失败: {e}")
        return False

def test_content_formatting():
    """测试内容格式化功能"""
    print("\n=== 测试内容格式化功能 ===")
    
    from tools.content_formatter import format_extraction_results, generate_statistics_report
    
    # 模拟数据
    test_data = {
        "source": "test",
        "results": [
            {
                "url": "https://example.com",
                "status": "success",
                "title": "测试页面1",
                "content": "这是测试内容1" * 20,
                "word_count": 120,
                "processing_time_ms": 1500,
                "timestamp": 1234567890
            },
            {
                "url": "https://test2.com",
                "status": "success", 
                "title": "测试页面2",
                "content": "这是测试内容2" * 15,
                "word_count": 90,
                "processing_time_ms": 1200,
                "timestamp": 1234567891
            },
            {
                "url": "https://error.com",
                "status": "error",
                "error_message": "连接失败",
                "timestamp": 1234567892
            }
        ]
    }
    
    try:
        # 格式化结果
        formatted = format_extraction_results(test_data)
        print("格式化结果包含的字段:")
        for key in formatted.keys():
            print(f"  - {key}")
        
        # 生成统计报告
        stats = generate_statistics_report(test_data["results"])
        print(f"统计信息:")
        print(f"  - 成功率: {stats.get('success_rate', 0)}%")
        print(f"  - 总字数: {stats.get('total_words_extracted', 0)}")
        print(f"  - 平均处理时间: {stats.get('average_processing_time_ms', 0)}ms")
        
        # 验证JSON可序列化
        json_str = json.dumps(formatted, ensure_ascii=False, indent=2)
        return len(json_str) > 0
    except Exception as e:
        print(f"内容格式化测试失败: {e}")
        return False

def test_agent_functions():
    """测试Agent主要功能"""
    print("\n=== 测试Agent主要功能 ===")
    
    from agent import extract_urls_from_input, extract_web_content, format_final_output
    
    test_input = """
    请帮我提取以下网站的内容：
    - 官方网站: https://example.com
    - 文档页面: https://httpbin.org/html
    - 联系页面: www.contact-test.com
    """
    
    try:
        print("步骤1: 提取URL")
        url_result = extract_urls_from_input(test_input, "function_test")
        print(f"  提取状态: {url_result['status']}")
        print(f"  URL数量: {url_result.get('urls_found', 0)}")
        
        if url_result['status'] != 'success':
            print("  URL提取失败，跳过后续测试")
            return False
        
        print("步骤2: 提取网页内容")
        content_result = extract_web_content(url_result)
        print(f"  处理状态: {content_result['status']}")
        print(f"  处理总数: {content_result.get('total_processed', 0)}")
        print(f"  成功数量: {content_result.get('successful_extractions', 0)}")
        
        print("步骤3: 格式化输出")
        final_result = format_final_output(content_result)
        print(f"  格式化完成，包含字段: {list(final_result.keys())}")
        
        # 显示最终统计
        proc_info = final_result.get('processing_info', {})
        print(f"  最终统计:")
        print(f"    总URL: {proc_info.get('total_urls', 0)}")
        print(f"    成功: {proc_info.get('successful_count', 0)}")
        print(f"    失败: {proc_info.get('failed_count', 0)}")
        print(f"    成功率: {proc_info.get('success_rate', 0)}%")
        
        return True
    except Exception as e:
        print(f"Agent功能测试失败: {e}")
        return False

def test_configuration():
    """测试配置文件"""
    print("\n=== 测试配置文件 ===")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("配置文件加载成功")
        print(f"  Agent名称: {config.get('name', 'unknown')}")
        print(f"  应用类型: {config.get('app_type', 'unknown')}")
        print(f"  能力数量: {len(config.get('capabilities', []))}")
        
        # 验证必需字段
        required_fields = ['name', 'description', 'app_type', 'capabilities']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"  警告: 缺少必需字段: {missing_fields}")
            return False
        
        return True
    except Exception as e:
        print(f"配置文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始Web Content Extractor Agent基础功能测试")
    print("=" * 60)
    
    tests = [
        ("配置文件", test_configuration),
        ("URL提取", test_url_extraction),
        ("网页爬取", test_web_crawling), 
        ("内容格式化", test_content_formatting),
        ("Agent功能", test_agent_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}测试: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}测试: ❌ 异常 - {e}")
    
    print("\n" + "=" * 60)
    print("测试总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Agent基础功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)