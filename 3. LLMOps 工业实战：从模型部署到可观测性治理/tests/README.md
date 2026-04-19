# 测试套件

本目录包含 LLMOps 实验所有代码的单元测试。

## 📋 测试文件列表

| 测试文件 | 测试内容 |
|---------|---------|
| `test_ab_test.py` | A/B 模型性能对比测试 |
| `test_prompt_injection.py` | 提示词注入攻击测试 |
| `test_tool_use_traditional.py` | 传统工具调用测试 |
| `test_mcp.py` | MCP 服务器和客户端测试 |
| `test_llm_judge.py` | LLM-as-a-Judge 测试 |
| `test_observability.py` | 可观测性模块测试 |

## 🚀 运行测试

### 方式一：运行所有测试

```bash
cd tests
python run_all_tests.py
```

### 方式二：运行单个测试文件

```bash
cd tests
python -m unittest test_ab_test.py
python -m unittest test_observability.py
```

### 方式三：使用 pytest（如果已安装）

```bash
pip install pytest
pytest tests/ -v
```

## 📊 测试覆盖

| 模块 | 测试覆盖率 | 说明 |
|------|-----------|------|
| ab_test.py | 基础测试 | 导入和函数存在性测试 |
| prompt_injection.py | 功能测试 | JSON 清理函数测试 |
| tool_use_traditional.py | 功能测试 | 工具函数测试 |
| mcp_server.py | 功能测试 | MCP 工具函数测试 |
| mcp_client.py | 基础测试 | 导入和函数存在性测试 |
| llm_judge.py | 基础测试 | 导入和函数存在性测试 |
| observability_performance.py | 功能测试 | 性能指标收集器测试 |
| observability_quality.py | 功能测试 | 质量评估器测试 |
| observability_security.py | 功能测试 | 安全护栏测试 |
| observability_dashboard.py | 基础测试 | 仪表盘初始化测试 |

## 🔧 注意事项

1. 部分测试需要 Ollama 服务运行
2. 集成测试需要网络连接
3. 建议在虚拟环境中运行测试
