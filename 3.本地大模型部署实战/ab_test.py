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
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='local',
            timeout=300
        )
        
        models = ["qwen3.5:9b", "qwen3.5:35b-a3b"]
        test_prompt = "请用面向对象的思想设计一个电梯调度系统，给出核心代码。"
        
        print("=" * 60)
        print("开始 A/B 模型性能对比测试")
        print("=" * 60)
        print("\n💡 提示：两个模型依次测试，测试之间有冷却时间\n")
        
        results = []
        
        for i, model_name in enumerate(models):
            if i > 0:
                print("\n⏳ 冷却时间 (5秒)...")
                time.sleep(5)
            
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
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                print(f"✅ 模型 {model_name} 测试完成")
                print(f"⏱️  耗时: {duration:.2f} 秒")
                print(f"📊  Token: {prompt_tokens} + {completion_tokens} = {total_tokens}")
                print(f"📄 回复预览:\n{content[:200]}...")
                print("-" * 60)
                
                results.append({
                    "model": model_name,
                    "duration": duration,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                })
                
            except Exception as e:
                print(f"❌ 模型 {model_name} 测试失败")
                print(f"错误信息: {str(e)}")
                print("-" * 60)
                results.append({
                    "model": model_name,
                    "error": str(e)
                })
                continue
        
        print("\n" + "=" * 60)
        print("📊 结果汇总")
        print("=" * 60)
        for res in results:
            if "error" in res:
                print(f"{res['model']}: ❌ 失败: {res['error']}")
            else:
                print(f"{res['model']}: ⏱️ {res['duration']:.2f}s, 📊 {res['total_tokens']} tokens")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_model_performance()
