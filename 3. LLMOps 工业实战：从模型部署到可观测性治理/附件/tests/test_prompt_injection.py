import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPromptInjection(unittest.TestCase):
    """测试提示词注入脚本"""
    
    def test_import(self):
        """测试导入 prompt_injection 模块"""
        try:
            from prompt_injection import test_prompt_injection, clean_json_output
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    def test_clean_json_output_function(self):
        """测试 clean_json_output 函数"""
        from prompt_injection import clean_json_output
        
        test_cases = [
            ('```json{"test": "value"}```', '{"test": "value"}'),
            ('{"test": "value"}', '{"test": "value"}'),
            ('  {"test": "value"}  ', '{"test": "value"}'),
            ('```{"test": "value"}```', '{"test": "value"}'),
        ]
        
        for input_text, expected in test_cases:
            result = clean_json_output(input_text)
            self.assertEqual(result, expected, f"输入: {input_text}")

if __name__ == '__main__':
    unittest.main()
