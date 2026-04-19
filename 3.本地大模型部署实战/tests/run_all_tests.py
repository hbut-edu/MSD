#!/usr/bin/env python3
"""
运行所有测试的主文件
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_suite():
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 发现并加载所有测试
    suite.addTests(loader.discover(test_dir, pattern='test_*.py'))
    
    return suite

def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"  {title}".center(80))
    print("="*80)

def main():
    """主函数"""
    print_header("LLMOps 实验代码 - 完整测试套件")
    
    suite = create_test_suite()
    
    print(f"\n📋 发现 {suite.countTestCases()} 个测试用例\n")
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    
    # 打印总结
    print_header("测试总结")
    
    print(f"\n📊 运行总数: {result.testsRun}")
    print(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"⚠️  错误: {len(result.errors)}")
    print(f"⏭️  跳过: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败！")
        return 1

if __name__ == '__main__':
    sys.exit(main())
