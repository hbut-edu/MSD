from openai import OpenAI
import time
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
import psutil

class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics_history: List[Dict] = []
    
    def record_metric(self, 
                     model_name: str,
                     prompt_tokens: int,
                     completion_tokens: int,
                     total_tokens: int,
                     ttft: float,
                     tpot: float,
                     total_latency: float,
                     success: bool = True,
                     error_msg: Optional[str] = None):
        """记录单次请求的性能指标"""
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "ttft_seconds": ttft,
            "tpot_seconds": tpot,
            "total_latency_seconds": total_latency,
            "tokens_per_second": completion_tokens / total_latency if total_latency > 0 else 0,
            "success": success,
            "error_msg": error_msg,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
        
        self.metrics_history.append(metric)
        return metric
    
    def get_summary(self) -> Dict:
        """获取性能汇总统计"""
        if not self.metrics_history:
            return {}
        
        successful = [m for m in self.metrics_history if m["success"]]
        
        return {
            "total_requests": len(self.metrics_history),
            "successful_requests": len(successful),
            "failure_rate": 1 - len(successful) / len(self.metrics_history) if self.metrics_history else 0,
            "avg_ttft": sum(m["ttft_seconds"] for m in successful) / len(successful) if successful else 0,
            "avg_tpot": sum(m["tpot_seconds"] for m in successful) / len(successful) if successful else 0,
            "avg_latency": sum(m["total_latency_seconds"] for m in successful) / len(successful) if successful else 0,
            "avg_tokens_per_second": sum(m["tokens_per_second"] for m in successful) / len(successful) if successful else 0,
            "total_tokens": sum(m["total_tokens"] for m in successful),
            "total_prompt_tokens": sum(m["prompt_tokens"] for m in successful),
            "total_completion_tokens": sum(m["completion_tokens"] for m in successful)
        }
    
    def export_to_csv(self, filename: str = "performance_metrics.csv"):
        """导出指标到 CSV 文件"""
        if not self.metrics_history:
            return
        
        keys = self.metrics_history[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.metrics_history)
        print(f"✅ 性能指标已导出到 {filename}")
    
    def print_summary(self):
        """打印性能汇总报告"""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("📊 性能监控汇总报告")
        print("="*80)
        print(f"总请求数: {summary['total_requests']}")
        print(f"成功请求: {summary['successful_requests']}")
        print(f"失败率: {summary['failure_rate']:.2%}")
        print(f"\n⏱️  延迟指标:")
        print(f"  平均 TTFT (首 Token 时间): {summary['avg_ttft']:.3f}s")
        print(f"  平均 TPOT (每 Token 时间): {summary['avg_tpot']:.3f}s")
        print(f"  平均总延迟: {summary['avg_latency']:.3f}s")
        print(f"\n🔢 Token 指标:")
        print(f"  总 Token 消耗: {summary['total_tokens']:,}")
        print(f"  输入 Token: {summary['total_prompt_tokens']:,}")
        print(f"  输出 Token: {summary['total_completion_tokens']:,}")
        print(f"  平均生成速度: {summary['avg_tokens_per_second']:.2f} tokens/s")
        print("="*80 + "\n")

class MonitoredLLMClient:
    """带性能监控的 LLM 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str = "local"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.metrics = PerformanceMetrics()
    
    def chat_with_monitoring(self, 
                            model: str, 
                            messages: List[Dict],
                            **kwargs) -> tuple:
        """带监控的聊天调用"""
        
        start_time = time.time()
        ttft = None
        success = True
        error_msg = None
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                **kwargs
            )
            
            ttft = time.time() - start_time
            content = response.choices[0].message.content
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_tokens = response.usage.total_tokens
            
            total_latency = time.time() - start_time
            tpot = total_latency / completion_tokens if completion_tokens > 0 else 0
            
            self.metrics.record_metric(
                model_name=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                ttft=ttft,
                tpot=tpot,
                total_latency=total_latency,
                success=True
            )
            
            return content, response.usage
            
        except Exception as e:
            success = False
            error_msg = str(e)
            total_latency = time.time() - start_time
            
            self.metrics.record_metric(
                model_name=model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                ttft=ttft or total_latency,
                tpot=0,
                total_latency=total_latency,
                success=False,
                error_msg=error_msg
            )
            
            raise

def test_performance_monitoring():
    """测试性能监控系统"""
    
    print("="*80)
    print("🚀 性能可观测性实战")
    print("="*80)
    
    client = MonitoredLLMClient()
    
    test_prompts = [
        "请用一句话解释什么是人工智能。",
        "请用一句话解释什么是机器学习。",
        "请用一句话解释什么是深度学习。",
        "请用一句话解释什么是大语言模型。",
        "请用一句话解释什么是 Transformer。"
    ]
    
    print(f"\n📝 开始测试 {len(test_prompts)} 个请求...\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"[{i}/{len(test_prompts)}] 发送请求: {prompt[:50]}...")
        
        try:
            content, usage = client.chat_with_monitoring(
                model="qwen3.5:9b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            print(f"    ✓ 成功! 响应长度: {len(content)} 字符")
        except Exception as e:
            print(f"    ✗ 失败: {str(e)}")
        
        time.sleep(1)
    
    print("\n" + "="*80)
    client.metrics.print_summary()
    client.metrics.export_to_csv("performance_metrics.csv")
    
    print("\n💡 思考问题:")
    print("   1. TTFT 和 TPOT 分别代表什么？它们对用户体验有什么影响？")
    print("   2. 如何根据性能指标优化模型部署？")
    print("   3. 为什么需要监控 CPU 和内存使用率？")

if __name__ == "__main__":
    test_performance_monitoring()
