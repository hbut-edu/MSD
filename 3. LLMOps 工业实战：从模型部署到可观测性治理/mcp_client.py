from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
import json
import asyncio

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    print("=" * 70)
    print("MCP 架构工具调用")
    print("=" * 70)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools_response = await session.list_tools()
            
            print("\n📡 动态发现的工具：")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            llm_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in tools_response.tools
            ]
            
            client = OpenAI(base_url='http://localhost:11434/v1', api_key='local')
            
            query = "现在几点了？计算 256 * 1024"
            print(f"\n📝 用户查询: {query}")
            
            response = client.chat.completions.create(
                model="qwen3.5:9b",
                messages=[{"role": "user", "content": query}],
                tools=llm_tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    print(f"\n🔧 调用工具: {func_name}")
                    print(f"📊 参数: {func_args}")
                    
                    result = await session.call_tool(
                        func_name,
                        arguments=func_args
                    )
                    
                    result_text = result.content[0].text
                    print(f"✅ 执行结果: {result_text}")
            else:
                print(f"💬 直接回复: {message.content}")

if __name__ == "__main__":
    asyncio.run(main())
