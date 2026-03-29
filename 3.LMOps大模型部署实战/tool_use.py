from openai import OpenAI
import json
import sys

def get_server_status(server_id):
    """
    本地执行函数 (Harness)
    模拟查询服务器状态
    """
    print(f"\n⚙️  [本地系统执行] 查询服务器 {server_id}...")
    # 这里可以连接真实的服务器 API
    return f"服务器 {server_id} 状态正常，CPU 45%，内存 62%"

def test_tool_use():
    """
    测试 Tool Use 功能
    """
    try:
        # 初始化 OpenAI 客户端
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='local',
            timeout=120
        )
        
        # 定义工具 Schema
        tools = [{
            "type": "function",
            "function": {
                "name": "get_server_status",
                "description": "获取指定服务器的当前运行状态",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "server_id": {
                            "type": "string",
                            "description": "服务器唯一标识符"
                        }
                    },
                    "required": ["server_id"]
                }
            }
        }]
        
        print("=" * 60)
        print("Agent Tool Use 实验")
        print("=" * 60)
        
        # Agent 思考
        print("\n🤖 Agent 正在思考...")
        user_query = "帮我查一下 server-102 的运行状态。"
        print(f"用户查询: {user_query}")
        
        response = client.chat.completions.create(
            model="qwen3.5:9b",
            messages=[{"role": "user", "content": user_query}],
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # 解析并执行
        if message.tool_calls:
            print(f"\n📋 模型请求调用 {len(message.tool_calls)} 个工具")
            
            for tool_call in message.tool_calls:
                print(f"\n🛠️  工具名称: {tool_call.function.name}")
                
                try:
                    func_args = json.loads(tool_call.function.arguments)
                    print(f"📊 调用参数: {func_args}")
                    
                    if tool_call.function.name == "get_server_status":
                        result = get_server_status(server_id=func_args.get("server_id"))
                        print(f"✅ 执行结果: {result}")
                    else:
                        print(f"⚠️  未知工具: {tool_call.function.name}")
                        
                except json.JSONDecodeError:
                    print(f"❌ 参数解析失败: {tool_call.function.arguments}")
                except Exception as e:
                    print(f"❌ 工具执行失败: {str(e)}")
        else:
            print("\n💬 模型未调用工具，直接回复:")
            print(message.content)
        
        print("\n" + "=" * 60)
        print("实验完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_tool_use()
