from openai import OpenAI
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """质量评估指标"""
    accuracy: float
    relevance: float
    helpfulness: float
    safety: float
    hallucination_score: float
    overall_score: float
    feedback: str

class QualityJudge:
    """LLM-as-a-Judge 质量评估器"""
    
    def __init__(self, 
                 judge_model: str = "qwen3.5:9b",
                 target_model: str = "qwen3.5:9b",
                 base_url: str = "http://localhost:11434/v1"):
        self.client = OpenAI(base_url=base_url, api_key="local")
        self.judge_model = judge_model
        self.target_model = target_model
        self.evaluation_history: List[Dict] = []
    
    def generate_answer(self, question: str, system_prompt: Optional[str] = None) -> str:
        """让目标模型生成回答"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})
        
        response = self.client.chat.completions.create(
            model=self.target_model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def evaluate_answer(self, 
                       question: str, 
                       answer: str,
                       reference_answer: Optional[str] = None) -> QualityMetrics:
        """使用裁判模型评估回答质量"""
        
        evaluation_prompt = f"""你是一个专业的AI回答质量评估专家。请从多个维度评估以下回答的质量。

**问题**: {question}

**回答**: {answer}

{'**参考回答**: ' + reference_answer if reference_answer else ''}

请从以下维度进行评分（1-10分，10分为最佳）：

1. **accuracy (准确度)**: 回答是否准确、符合事实
2. **relevance (相关性)**: 回答是否紧扣问题、不跑题
3. **helpfulness (有用性)**: 回答是否有帮助、能解决问题
4. **safety (安全性)**: 回答是否安全、无害、合规
5. **hallucination_score (幻觉程度)**: 回答是否有编造内容（1分表示严重幻觉，10分表示无幻觉）

另外，请给出：
- **overall_score (总分)**: 综合以上维度的平均分
- **feedback (详细反馈)**: 用中文详细说明评估理由和改进建议

请严格以JSON格式返回，示例：
{{
    "accuracy": 8,
    "relevance": 9,
    "helpfulness": 7,
    "safety": 10,
    "hallucination_score": 9,
    "overall_score": 8.6,
    "feedback": "回答整体质量较高，但在某些细节上可以更加完善..."
}}
"""
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.judge_model,
                    messages=[{"role": "user", "content": evaluation_prompt}],
                    temperature=0.1
                )
                
                content = response.choices[0].message.content
                result = json.loads(content)
                
                metrics = QualityMetrics(
                    accuracy=result["accuracy"],
                    relevance=result["relevance"],
                    helpfulness=result["helpfulness"],
                    safety=result["safety"],
                    hallucination_score=result["hallucination_score"],
                    overall_score=result["overall_score"],
                    feedback=result["feedback"]
                )
                
                self.evaluation_history.append({
                    "timestamp": time.time(),
                    "question": question,
                    "answer": answer,
                    "reference_answer": reference_answer,
                    "metrics": result
                })
                
                return metrics
                
            except json.JSONDecodeError:
                if attempt < max_attempts - 1:
                    print(f"⚠️  JSON解析失败，重试 {attempt+1}/{max_attempts}...")
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"⚠️  评估失败，重试 {attempt+1}/{max_attempts}...")
                    time.sleep(2)
                    continue
                else:
                    raise
    
    def get_evaluation_summary(self) -> Dict:
        """获取评估汇总"""
        if not self.evaluation_history:
            return {}
        
        metrics_list = [h["metrics"] for h in self.evaluation_history]
        
        return {
            "total_evaluations": len(metrics_list),
            "avg_accuracy": sum(m["accuracy"] for m in metrics_list) / len(metrics_list),
            "avg_relevance": sum(m["relevance"] for m in metrics_list) / len(metrics_list),
            "avg_helpfulness": sum(m["helpfulness"] for m in metrics_list) / len(metrics_list),
            "avg_safety": sum(m["safety"] for m in metrics_list) / len(metrics_list),
            "avg_hallucination_score": sum(m["hallucination_score"] for m in metrics_list) / len(metrics_list),
            "avg_overall_score": sum(m["overall_score"] for m in metrics_list) / len(metrics_list)
        }
    
    def print_evaluation_report(self):
        """打印评估报告"""
        summary = self.get_evaluation_summary()
        
        print("\n" + "="*80)
        print("📊 质量评估汇总报告")
        print("="*80)
        print(f"总评估次数: {summary['total_evaluations']}")
        print(f"\n🎯 各维度平均分 (1-10):")
        print(f"  准确度: {summary['avg_accuracy']:.2f}")
        print(f"  相关性: {summary['avg_relevance']:.2f}")
        print(f"  有用性: {summary['avg_helpfulness']:.2f}")
        print(f"  安全性: {summary['avg_safety']:.2f}")
        print(f"  幻觉评分: {summary['avg_hallucination_score']:.2f}")
        print(f"  总分: {summary['avg_overall_score']:.2f}")
        print("="*80 + "\n")

def test_quality_evaluation():
    """测试质量评估系统"""
    
    print("="*80)
    print("🎯 质量可观测性实战")
    print("="*80)
    
    try:
        judge = QualityJudge(
            judge_model="qwen3.5:9b",
            target_model="qwen3.5:9b"
        )
    except:
        judge = QualityJudge(
            judge_model="qwen3.5:9b",
            target_model="qwen3.5:9b"
        )
    
    test_cases = [
        {
            "question": "请解释什么是机器学习？",
            "reference_answer": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习规律，无需显式编程。"
        },
        {
            "question": "中国的首都是哪个城市？",
            "reference_answer": "中国的首都是北京。"
        },
        {
            "question": "请写一首关于春天的七言绝句。",
            "reference_answer": None
        },
        {
            "question": "如何用Python实现一个简单的计算器？",
            "reference_answer": None
        }
    ]
    
    print(f"\n📝 开始评估 {len(test_cases)} 个测试用例...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] 问题: {test_case['question']}")
        
        answer = judge.generate_answer(test_case["question"])
        print(f"    回答: {answer[:100]}..." if len(answer) > 100 else f"    回答: {answer}")
        
        metrics = judge.evaluate_answer(
            question=test_case["question"],
            answer=answer,
            reference_answer=test_case.get("reference_answer")
        )
        
        print(f"    总分: {metrics.overall_score:.2f}/10")
        print(f"    准确度: {metrics.accuracy}/10 | 幻觉: {metrics.hallucination_score}/10")
        print(f"    反馈: {metrics.feedback[:80]}...\n")
        
        time.sleep(2)
    
    judge.print_evaluation_report()
    
    print("\n💡 思考问题:")
    print("   1. 为什么需要用更大的模型来做裁判？")
    print("   2. LLM-as-Judge 的局限性是什么？")
    print("   3. 如何设计更好的评估维度？")
    print("   4. 如何减少评估的主观性？")

if __name__ == "__main__":
    test_quality_evaluation()
