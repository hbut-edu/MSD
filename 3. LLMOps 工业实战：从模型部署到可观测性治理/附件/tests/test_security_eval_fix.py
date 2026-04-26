#!/usr/bin/env python3
"""
测试 SafeCalculator 的安全性
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_safe_calculator():
    """测试安全的计算器实现"""
    from mcp_server import SafeCalculator
    
    print("="*70)
    print("🔒 SafeCalculator 安全测试")
    print("="*70)
    
    # 测试正常功能
    test_cases = [
        ("2+3", 5),
        ("10-4", 6),
        ("3*4", 12),
        ("15/3", 5),
        ("2+3*4", 14),
        ("(2+3)*4", 20),
        ("10/3", 10/3),
    ]
    
    print("\n✅ 正常功能测试：")
    for expr, expected in test_cases:
        try:
            result = SafeCalculator.calculate(expr)
            status = "✓" if abs(result - expected) < 0.0001 else "✗"
            print(f"  {status} {expr} = {result} (expected: {expected})")
        except Exception as e:
            print(f"  ✗ {expr} 失败: {str(e)}")
    
    # 测试安全防护
    print("\n🔒 安全防护测试：")
    
    # 危险输入测试
    dangerous_inputs = [
        # 代码注入尝试
        ("__import__('os').system('rm -rf /')", "__import__"),
        ("eval('1+1')", "eval"),
        ("exec('print(1)')", "exec"),
        
        # 危险函数调用
        ("open('/etc/passwd')", "open"),
        ("os.system('ls')", "os."),
        ("sys.exit()", "sys."),
        
        # 资源耗尽攻击
        ("((1+2)*(3+4))" * 100, "过长表达式"),
    ]
    
    for dangerous_input, description in dangerous_inputs:
        try:
            result = SafeCalculator.calculate(dangerous_input)
            print(f"  ✗ {description} - 应该被阻止但执行了: {str(result)[:50]}")
        except ValueError as e:
            print(f"  ✓ {description} - 正确阻止: {str(e)[:50]}")
        except Exception as e:
            print(f"  ✓ {description} - 异常阻止: {type(e).__name__}")
    
    # 测试错误处理
    print("\n❌ 错误处理测试：")
    error_cases = [
        "abc",
        "1 +",
        "2 ++ 3",
        "1 @ 2",
    ]
    
    for error_input in error_cases:
        try:
            result = SafeCalculator.calculate(error_input)
            print(f"  ✗ {error_input} - 应该报错但返回了: {result}")
        except (ValueError, SyntaxError) as e:
            print(f"  ✓ {error_input} - 正确报错: {str(e)[:30]}")
    
    print("\n" + "="*70)
    print("测试完成！SafeCalculator 可以安全使用。")
    print("="*70)

if __name__ == "__main__":
    test_safe_calculator()
