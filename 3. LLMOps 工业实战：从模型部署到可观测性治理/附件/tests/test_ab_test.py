import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestABTest(unittest.TestCase):
    """测试 A/B 模型性能对比脚本"""
    
    def test_import(self):
        """测试导入 ab_test 模块"""
        try:
            from ab_test import test_model_performance
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    @patch('ab_test.OpenAI')
    def test_model_performance_function_exists(self, mock_openai):
        """测试 test_model_performance 函数存在"""
        from ab_test import test_model_performance
        self.assertTrue(callable(test_model_performance), "函数应该是可调用的")

if __name__ == '__main__':
    unittest.main()
