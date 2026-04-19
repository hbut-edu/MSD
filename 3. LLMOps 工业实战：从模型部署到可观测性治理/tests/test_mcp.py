import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMCPServer(unittest.TestCase):
    """测试 MCP 服务器"""
    
    def test_import_server(self):
        """测试导入 mcp_server 模块"""
        try:
            import mcp_server
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    def test_server_tools_exist(self):
        """测试 MCP 服务器工具是否定义"""
        import mcp_server
        self.assertTrue(hasattr(mcp_server, 'get_current_time'), "get_current_time 应该存在")
        self.assertTrue(hasattr(mcp_server, 'calculate'), "calculate 应该存在")
    
    def test_get_current_time_function(self):
        """测试 get_current_time 函数"""
        import mcp_server
        result = mcp_server.get_current_time()
        self.assertTrue(isinstance(result, str), "结果应该是字符串")
        self.assertTrue(len(result) > 0, "结果不应为空")
    
    def test_calculate_function(self):
        """测试 calculate 函数"""
        import mcp_server
        
        test_cases = [
            ("2+3*4", "2+3*4 = 14"),
            ("(10+5)/3", "(10+5)/3 = 5.0"),
            ("100-20", "100-20 = 80"),
            ("invalid", "错误：表达式包含非法字符"),
        ]
        
        for expr, expected in test_cases:
            result = mcp_server.calculate(expr)
            self.assertEqual(result, expected, f"表达式: {expr}")

class TestMCPClient(unittest.TestCase):
    """测试 MCP 客户端"""
    
    def test_import_client(self):
        """测试导入 mcp_client 模块"""
        try:
            import mcp_client
            self.assertTrue(True, "导入成功")
        except Exception as e:
            self.fail(f"导入失败: {str(e)}")
    
    def test_main_function_exists(self):
        """测试 main 函数存在"""
        import mcp_client
        self.assertTrue(hasattr(mcp_client, 'main'), "main 函数应该存在")
        self.assertTrue(callable(mcp_client.main), "main 函数应该是可调用的")

if __name__ == '__main__':
    unittest.main()
