from observability_performance import MonitoredLLMClient
from observability_quality import QualityJudge
from observability_security import SecurityGuard
import json
import time
from datetime import datetime
from typing import Dict

class UnifiedObservabilityDashboard:
    """统一可观测性仪表盘"""
    
    def __init__(self):
        self.performance_client = MonitoredLLMClient()
        self.quality_judge = QualityJudge(
            judge_model="qwen3.5:9b",
            target_model="qwen3.5:9b"
        )
        self.security_guard = SecurityGuard()
    
    def run_full_pipeline(self, question: str) -> Dict:
        """运行完整的可观测性流水线"""
        
        print(f"\n{'='*80}")
        print(f"🔄 处理问题: {question}")
        print(f"{'='*80}")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "performance": None,
            "quality": None,
            "security": None,
            "answer": None
        }
        
        print("\n🛡️  [1/4] 安全检查...")
        is_safe, alert = self.security_guard.check_input(question, "qwen3.5:9b")
        result["security"] = {
            "is_safe": is_safe,
            "alert": {
                "type": alert.alert_type,
                "severity": alert.severity,
                "description": alert.description
            } if alert else None
        }
        
        if not is_safe:
            print(f"   ⚠️  安全拦截: {alert.description if alert else '未知原因'}")
            return result
        
        print("   ✓ 通过")
        
        print("\n⚡ [2/4] 生成回答（带性能监控）...")
        try:
            answer, usage = self.performance_client.chat_with_monitoring(
                model="qwen3.5:9b",
                messages=[{"role": "user", "content": question}]
            )
            result["answer"] = answer
            result["performance"] = self.performance_client.metrics.get_summary()
            print(f"   ✓ 生成完成")
        except Exception as e:
            print(f"   ✗ 生成失败: {e}")
            return result
        
        print("\n🎯 [3/4] 质量评估...")
        try:
            quality_metrics = self.quality_judge.evaluate_answer(
                question=question,
                answer=answer
            )
            result["quality"] = {
                "accuracy": quality_metrics.accuracy,
                "relevance": quality_metrics.relevance,
                "helpfulness": quality_metrics.helpfulness,
                "safety": quality_metrics.safety,
                "hallucination_score": quality_metrics.hallucination_score,
                "overall_score": quality_metrics.overall_score,
                "feedback": quality_metrics.feedback
            }
            print(f"   ✓ 评估完成 - 总分: {quality_metrics.overall_score:.2f}/10")
        except Exception as e:
            print(f"   ⚠️  评估跳过: {e}")
        
        print("\n📝 [4/4] 记录审计日志...")
        self.security_guard.log_interaction(
            prompt=question,
            response=answer,
            model="qwen3.5:9b",
            is_safe=True
        )
        print("   ✓ 已记录")
        
        return result
    
    def print_dashboard(self, results: list):
        """打印综合仪表盘"""
        print("\n" + "="*80)
        print("📊 统一可观测性仪表盘")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- 结果 #{i} ---")
            print(f"问题: {result['question']}")
            
            if not result["security"]["is_safe"]:
                print(f"⚠️  状态: 安全拦截")
                continue
            
            print(f"✅ 状态: 成功")
            
            if result["performance"]:
                perf = result["performance"]
                print(f"⚡ 性能: 延迟={perf.get('avg_latency', 0):.2f}s, "
                      f"Tokens/s={perf.get('avg_tokens_per_second', 0):.2f}")
            
            if result["quality"]:
                qual = result["quality"]
                print(f"🎯 质量: 总分={qual['overall_score']:.2f}, "
                      f"准确度={qual['accuracy']}, "
                      f"幻觉={qual['hallucination_score']}")
        
        print("\n" + "="*80)
    
    def export_report(self, results: list, filename: str = "observability_report.json"):
        """导出完整报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_requests": len(results),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 完整报告已导出到 {filename}")

def main():
    """主函数 - 综合实战演示"""
    print("="*80)
    print("🚀 可观测性治理综合实战")
    print("="*80)
    
    dashboard = UnifiedObservabilityDashboard()
    
    test_questions = [
        "请解释什么是大语言模型？",
        "Python 中列表和元组有什么区别？",
        "如何用递归计算斐波那契数列？"
    ]
    
    results = []
    for question in test_questions:
        result = dashboard.run_full_pipeline(question)
        results.append(result)
        time.sleep(2)
    
    dashboard.print_dashboard(results)
    dashboard.export_report(results)
    
    print("\n🎉 可观测性治理实战完成！")
    print("\n💡 关键收获:")
    print("   1. 可观测性 = 性能 + 质量 + 安全")
    print("   2. 需要自动化工具链来持续监控")
    print("   3. 审计日志是问题排查的关键")
    print("   4. LLM-as-Judge 是质量评估的有效手段")

if __name__ == "__main__":
    main()
