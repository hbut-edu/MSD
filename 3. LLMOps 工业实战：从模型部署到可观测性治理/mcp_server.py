from mcp.server.fastmcp import FastMCP
from datetime import datetime
import ast
import operator
import re

mcp = FastMCP("ToolServer")

@mcp.tool()
def get_current_time() -> str:
    """
    获取当前时间
    
    返回格式化的当前时间字符串
    """
    now = datetime.now()
    return f"当前时间是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

class SafeCalculator:
    """安全的数学表达式计算器"""
    
    # 支持的操作符映射
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    
    @staticmethod
    def validate_expression(expression: str) -> bool:
        """
        验证表达式是否只包含允许的字符
        
        Args:
            expression: 数学表达式
            
        Returns:
            bool: 是否有效
        """
        # 只允许数字、运算符、括号和空格
        pattern = r'^[\d\s+\-*/().]+$'
        if not re.match(pattern, expression):
            return False
        
        # 检查是否包含危险模式
        dangerous_patterns = [
            '__',      # dunder 方法
            'import',  # import 语句
            'exec',    # exec 函数
            'eval',    # eval 函数
            'open',    # 文件操作
            'os.',     # os 模块
            'sys.',    # sys 模块
        ]
        
        expression_lower = expression.lower()
        for pattern in dangerous_patterns:
            if pattern in expression_lower:
                return False
        
        return True
    
    @staticmethod
    def safe_eval(node):
        """
        安全地递归计算 AST 节点
        
        Args:
            node: AST 节点
            
        Returns:
            计算结果
            
        Raises:
            ValueError: 无效的表达式
        """
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("只支持数字常量")
        
        elif isinstance(node, ast.BinOp):
            left = SafeCalculator.safe_eval(node.left)
            right = SafeCalculator.safe_eval(node.right)
            op_type = type(node.op)
            if op_type in SafeCalculator.operators:
                return SafeCalculator.operators[op_type](left, right)
            raise ValueError(f"不支持的操作符: {op_type.__name__}")
        
        elif isinstance(node, ast.UnaryOp):
            operand = SafeCalculator.safe_eval(node.operand)
            op_type = type(node.op)
            if op_type in SafeCalculator.operators:
                return SafeCalculator.operators[op_type](operand)
            raise ValueError(f"不支持的一元操作符: {op_type.__name__}")
        
        elif isinstance(node, ast.Expression):
            return SafeCalculator.safe_eval(node.body)
        
        elif isinstance(node, ast.Call):
            raise ValueError("不允许调用函数")
        
        elif isinstance(node, ast.Name):
            raise ValueError("不允许使用变量")
        
        elif isinstance(node, ast.Attribute):
            raise ValueError("不允许访问属性")
        
        else:
            raise ValueError(f"不支持的表达式类型: {type(node).__name__}")
    
    @classmethod
    def calculate(cls, expression: str) -> float:
        """
        计算数学表达式的值
        
        Args:
            expression: 数学表达式，例如 "2+3*4" 或 "(10+5)/3"
            
        Returns:
            计算结果
            
        Raises:
            ValueError: 表达式无效或包含不支持的操作
        """
        # 去除空白字符
        expression = expression.strip()
        
        # 验证字符安全性
        if not cls.validate_expression(expression):
            raise ValueError("表达式包含非法字符")
        
        # 检查表达式长度（防止过大的表达式）
        if len(expression) > 200:
            raise ValueError("表达式过长")
        
        # 使用 AST 安全解析
        try:
            tree = ast.parse(expression, mode='eval')
            result = cls.safe_eval(tree)
            return result
        except SyntaxError as e:
            raise ValueError(f"语法错误: {str(e)}")
        except ValueError as e:
            raise ValueError(f"计算错误: {str(e)}")

@mcp.tool()
def calculate(expression: str) -> str:
    """
    执行数学计算（安全版本）
    
    Args:
        expression: 数学表达式，例如 "2+3*4" 或 "(10+5)/3"
    
    Returns:
        计算结果的字符串形式
    """
    try:
        result = SafeCalculator.calculate(expression)
        return f"{expression} = {result}"
    except ValueError as e:
        return f"错误：{str(e)}"
    except Exception as e:
        return f"计算错误：{str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
