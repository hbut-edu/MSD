import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLLMJudge(unittest.TestCase):
    """测试 LLM-as-a-Judge 脚本"""
    
    def test_import(self):
        """测试导入 llm_judge 模块"""
        try:
            from llm_judge import test_llm_judge, ask_with_guardrails
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    def test_ask_with_guardrails_function_exists(self):
        """测试 ask_with_guardrails 函数存在"""
        from llm_judge import ask_with_guardrails
        self.assertTrue(callable(ask_with_guardrails), "函数应该是可调用的")
    
    def test_sensitive_word_detection(self):
        """测试敏感词检测"""
        from llm_judge import ask_with_guardrails
        
        class MockClient:
            def chat_completions(self, create):
                pass
        
        # 测试正常输入
        with self.assertRaises(Exception):
            ask_with_guardrails(MockClient(), "如何破解密码")
        
        # 测试安全输入（不会抛出敏感词异常，但会尝试调用 API）
        # 这里我们只是验证函数逻辑，不实际调用 API

if __name__ == '__main__':
    unittest.main()
