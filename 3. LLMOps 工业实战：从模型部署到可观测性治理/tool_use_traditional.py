from openai import OpenAI
import json
from datetime import datetime

def get_current_time() -> str:
    """获取当前时间"""
    now = datetime.now()
    return f"当前时间是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        return "错误：表达式包含非法字符"
    except Exception as e:
        return f"计算错误：{str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "数学表达式"}},
                "required": ["expression"]
            }
        }
    }
]

client = OpenAI(base_url='http://localhost:11434/v1', api_key='local')

def main():
    query = "现在几点了？计算 256 * 1024"
    print("=" * 70)
    print("传统方式工具调用")
    print("=" * 70)
    print(f"\n📝 用户查询: {query}")
    
    response = client.chat.completions.create(
        model="qwen3.5:9b",
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    if message.tool_calls:
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            print(f"\n🔧 调用工具: {func_name}")
            print(f"📊 参数: {func_args}")
            
            if func_name == "get_current_time":
                result = get_current_time()
            elif func_name == "calculate":
                result = calculate(**func_args)
            else:
                result = f"未知工具: {func_name}"
            
            print(f"✅ 执行结果: {result}")
    else:
        print(f"💬 直接回复: {message.content}")

if __name__ == "__main__":
    main()
