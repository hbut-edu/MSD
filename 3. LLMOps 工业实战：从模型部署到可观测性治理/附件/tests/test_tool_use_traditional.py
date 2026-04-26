import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestToolUseTraditional(unittest.TestCase):
    """测试传统工具调用脚本"""
    
    def test_import(self):
        """测试导入 tool_use_traditional 模块"""
        try:
            from tool_use_traditional import get_current_time, calculate
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    def test_get_current_time(self):
        """测试 get_current_time 函数"""
        from tool_use_traditional import get_current_time
        result = get_current_time()
        self.assertTrue(isinstance(result, str), "结果应该是字符串")
        self.assertTrue(len(result) > 0, "结果不应为空")
    
    def test_calculate_function(self):
        """测试 calculate 函数"""
        from tool_use_traditional import calculate
        
        test_cases = [
            ("2+3*4", "2+3*4 = 14"),
            ("(10+5)/3", "(10+5)/3 = 5.0"),
            ("100-20", "100-20 = 80"),
            ("10/0", None),
            ("invalid", "错误：表达式包含非法字符"),
        ]
        
        for expr, expected in test_cases:
            result = calculate(expr)
            if expected:
                self.assertEqual(result, expected, f"表达式: {expr}")

if __name__ == '__main__':
    unittest.main()
