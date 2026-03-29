from openai import OpenAI
import time
import sys

def test_model_performance():
    """
    测试不同模型的性能表现
    包含完整的异常处理机制
    """
    try:
        # 初始化 OpenAI 客户端（Ollama 使用特殊的 base_url 和 api_key='local'）
        # 注意：Ollama 的 OpenAI 兼容接口使用 api_key='local' 作为占位符
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='local',
            timeout=300  # 设置 5 分钟超时
        )
        
        models = ["qwen3.5:9b", "qwen3.5:35b-a3b"]
        test_prompt = "请用面向对象的思想设计一个电梯调度系统，给出核心代码。"
        
        print("=" * 60)
        print("开始 A/B 模型性能对比测试")
        print("=" * 60)
        
        for model_name in models:
            print(f"\n🚀 开始测试模型: {model_name}")
            print("-" * 60)
            
            try:
                start_time = time.time()
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": test_prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )
                
                duration = time.time() - start_time
                content = response.choices[0].message.content
                
                print(f"✅ 模型 {model_name} 测试完成")
                print(f"⏱️  耗时: {duration:.2f} 秒")
                print(f"📄 回复预览:\n{content[:200]}...")
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ 模型 {model_name} 测试失败")
                print(f"错误信息: {str(e)}")
                print("-" * 60)
                continue
        
        print("\n" + "=" * 60)
        print("所有模型测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_model_performance()
