#!/usr/bin/env python3
"""
Qwen3.5-9B 本地部署完整测试脚本
按照文档进行完整的部署和测试验证
"""

import requests
import time
import sys
import json
from typing import Dict, Any, List

class DeploymentTester:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.test_results = []
        
    def log(self, message: str, status: str = "INFO"):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_1_ollama_service(self) -> bool:
        """测试1: 检查Ollama服务状态"""
        self.log("=" * 60)
        self.log("测试1: 检查Ollama服务状态")
        self.log("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.log("✓ Ollama服务运行正常", "SUCCESS")
                self.test_results.append(("Ollama服务状态", True))
                return True
            else:
                self.log(f"✗ Ollama服务响应异常: {response.status_code}", "ERROR")
                self.test_results.append(("Ollama服务状态", False))
                return False
        except Exception as e:
            self.log(f"✗ 无法连接Ollama服务: {e}", "ERROR")
            self.test_results.append(("Ollama服务状态", False))
            return False
    
    def test_2_list_models(self) -> List[str]:
        """测试2: 列出已下载的模型"""
        self.log("\n" + "=" * 60)
        self.log("测试2: 列出已下载的模型")
        self.log("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                if models:
                    self.log(f"✓ 找到 {len(models)} 个已下载的模型:", "SUCCESS")
                    for model in models:
                        self.log(f"  - {model}")
                else:
                    self.log("⚠ 没有已下载的模型", "WARNING")
                self.test_results.append(("列出模型", True))
                return models
            else:
                self.log(f"✗ 获取模型列表失败: {response.status_code}", "ERROR")
                self.test_results.append(("列出模型", False))
                return []
        except Exception as e:
            self.log(f"✗ 获取模型列表异常: {e}", "ERROR")
            self.test_results.append(("列出模型", False))
            return []
    
    def test_3_generate_api(self, model_name: str = "qwen3.5:9b") -&gt; bool:
        """测试3: 测试generate API"""
        self.log("\n" + "=" * 60)
        self.log(f"测试3: 测试Generate API (模型: {model_name})")
        self.log("=" * 60)
        
        payload = {
            "model": model_name,
            "prompt": "你好，请用一句话介绍你自己",
            "stream": False,
            "options": {
                "num_predict": 100
            }
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Generate API调用成功 ({elapsed:.2f}秒)", "SUCCESS")
                self.log(f"响应: {data.get('response', '')[:100]}...")
                self.test_results.append(("Generate API", True))
                return True
            else:
                self.log(f"✗ Generate API调用失败: {response.status_code}", "ERROR")
                self.log(f"响应: {response.text}")
                self.test_results.append(("Generate API", False))
                return False
        except Exception as e:
            self.log(f"✗ Generate API调用异常: {e}", "ERROR")
            self.test_results.append(("Generate API", False))
            return False
    
    def test_4_chat_api(self, model_name: str = "qwen3.5:9b") -&gt; bool:
        """测试4: 测试Chat API"""
        self.log("\n" + "=" * 60)
        self.log(f"测试4: 测试Chat API (模型: {model_name})")
        self.log("=" * 60)
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业的Python程序员。"},
                {"role": "user", "content": "写一个Hello World程序"}
            ],
            "stream": False
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Chat API调用成功 ({elapsed:.2f}秒)", "SUCCESS")
                message = data.get("message", {})
                self.log(f"响应: {message.get('content', '')[:100]}...")
                self.test_results.append(("Chat API", True))
                return True
            else:
                self.log(f"✗ Chat API调用失败: {response.status_code}", "ERROR")
                self.log(f"响应: {response.text}")
                self.test_results.append(("Chat API", False))
                return False
        except Exception as e:
            self.log(f"✗ Chat API调用异常: {e}", "ERROR")
            self.test_results.append(("Chat API", False))
            return False
    
    def print_summary(self):
        """打印测试总结"""
        self.log("\n" + "=" * 60)
        self.log("测试总结")
        self.log("=" * 60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✓ 通过" if result else "✗ 失败"
            self.log(f"{test_name}: {status}")
        
        self.log(f"\n总计: {passed}/{total} 测试通过")
        
        if passed == total:
            self.log("\n🎉 所有测试通过！部署成功！", "SUCCESS")
        else:
            self.log(f"\n⚠ 有 {total - passed} 个测试失败，请检查", "WARNING")
    
    def run_full_test(self):
        """运行完整测试"""
        self.log("Qwen3.5-9B 本地部署完整测试")
        self.log("=" * 60)
        
        # 测试1: Ollama服务
        if not self.test_1_ollama_service():
            self.log("\n✗ Ollama服务未运行，无法继续测试", "ERROR")
            return
        
        # 测试2: 列出模型
        models = self.test_2_list_models()
        
        # 选择测试模型
        test_model = None
        if models:
            test_model = models[0]
            self.log(f"\n使用模型: {test_model} 进行测试")
        else:
            self.log("\n⚠ 没有已下载的模型，跳过API测试", "WARNING")
            self.test_results.append(("Generate API", False))
            self.test_results.append(("Chat API", False))
            self.print_summary()
            return
        
        # 测试3: Generate API
        self.test_3_generate_api(test_model)
        
        # 测试4: Chat API
        self.test_4_chat_api(test_model)
        
        # 打印总结
        self.print_summary()

if __name__ == "__main__":
    tester = DeploymentTester()
    tester.run_full_test()
