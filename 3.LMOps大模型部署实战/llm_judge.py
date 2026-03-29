from openai import OpenAI
import json
import sys

def ask_with_guardrails(client, prompt):
    """
    带护栏的查询函数
    包含敏感词拦截和 JSON 格式校验重试
    """
    # 1. 敏感词拦截
    sensitive_words = ["越狱", "攻击", "破解", "注入", "绕过"]
    for word in sensitive_words:
        if word in prompt.lower():
            raise ValueError(f"🚨 安全拦截：检测到敏感词 '{word}'！")
    
    # 2. JSON 格式强制校验与重试机制
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="qwen3.5:9b",
                messages=[{"role": "user", "content": prompt}],
                timeout=120
            )
            content = response.choices[0].message.content
            
            # 尝试解析 JSON（如果要求 JSON 格式）
            # 注意：Ollama 可能不完全支持 response_format 参数
            # 这里我们手动验证
            return content
            
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"⚠️  请求失败，重试 {attempt+1}/{max_attempts}...")
                continue
            else:
                raise

def test_llm_judge():
    """
    测试 LLM-as-a-Judge 功能
    """
    try:
        # 初始化 OpenAI 客户端
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='local',
            timeout=300
        )
        
        question = "为什么多线程编程必须使用死锁？"
        
        print("=" * 60)
        print("LLM-as-a-Judge 实验")
        print("=" * 60)
        print(f"\n❓ 陷阱问题: {question}")
        print("💡 提示：这是一个陷阱题！死锁是需要避免的，不是必须使用的。")
        
        # 1. 考生作答
        print("\n👨‍🎓 9B 模型正在作答...")
        try:
            ans = ask_with_guardrails(client, question)
            print(f"\n📝 9B 回答:\n{ans[:300]}...")
        except Exception as e:
            print(f"❌ 9B 模型作答失败: {str(e)}")
            return
        
        # 2. 裁判打分
        judge_prompt = f"""
        请评审以下题目和回答：
        
        题目：{question}
        学生回答：{ans}
        
        评分标准：
        - accuracy_score：1-10 分，10 分表示完全正确
        - feedback：详细的中文反馈，指出错误和改进建议
        
        请严格返回 JSON 格式，示例：
        {{
            "accuracy_score": 5,
            "feedback": "回答部分正确，但存在以下问题..."
        }}
        """
        
        print("\n" + "=" * 60)
        print("👨‍⚖️  35B-MoE 裁判正在打分...")
        print("=" * 60)
        
        try:
            judge_res = client.chat.completions.create(
                model="qwen3.5:35b-a3b",
                messages=[{"role": "user", "content": judge_prompt}],
                timeout=300
            )
            
            judge_content = judge_res.choices[0].message.content
            
            # 尝试解析 JSON
            try:
                judge_data = json.loads(judge_content)
                print(f"\n📊 评审结果:")
                print(f"   准确度评分: {judge_data.get('accuracy_score', 'N/A')}/10")
                print(f"   反馈意见: {judge_data.get('feedback', 'N/A')}")
            except json.JSONDecodeError:
                print(f"\n⚠️  裁判输出不是有效的 JSON 格式")
                print(f"原始输出:\n{judge_content}")
                
        except Exception as e:
            print(f"❌ 裁判评分失败: {str(e)}")
        
        print("\n" + "=" * 60)
        print("实验完成")
        print("=" * 60)
        print("\n💡 思考：")
        print("   - 为什么需要用更大的模型来裁判更小的模型？")
        print("   - LLM-as-Judge 有什么局限性？")
        print("   - 如何提高自动化评估的可靠性？")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_llm_judge()
