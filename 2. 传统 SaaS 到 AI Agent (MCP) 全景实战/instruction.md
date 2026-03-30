# 现代软件开发技术上机实验手册：传统 SaaS 到 AI Agent (MCP) 全景实战

# 实验主题

传统 SaaS 到 AI Agent (MCP) 全景实战

# 实验目标

1. 理解传统 SaaS 架构与 AI Agent 架构的核心差异
2. 掌握 Dense 与 MoE 模型架构的特点和适用场景
3. 学会构建原子化业务工具库（Atomic Tools）
4. 掌握 MCP (Model Context Protocol) 工具定义规范
5. 理解 Agent 核心调度器的工作原理
6. 学会实现多工具链式调用（Chain of Actions）
7. 掌握自然语言界面（LUI）的构建方法
8. 建立 AI 时代软件工程的新思维

# 📅 课程概览 (Total: 240 Mins)

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :--- | :--- | :--- | :--- |
| **0-30** | **模块一：理论导入** | 理解 SaaS 与 Agent 架构差异，掌握 Dense vs MoE 架构特点。 | 理论讲授、架构图解 |
| **30-70** | **模块二：环境准备与工具构建** | 完成 Ollama 本地部署，下载模型，构建原子化业务工具库。 | Ollama, Python, pip, 函数式编程 |
| **70-110** | **模块三：SaaS 对照组实现** | 实现传统 SaaS 巨石架构控制器，理解硬编码局限性。 | 面向对象编程, 耦合设计 |
| **110-150** | **模块四：MCP 工具定义与 Agent 调度器** | 掌握 MCP 工具 Schema，实现 Agent 核心调度器。 | JSON Schema, OpenAI API, 链式调用 |
| **150-190** | **模块五：双轨对比 UI 与实验观察** | 构建对比实验 UI，观测 Dense 与 MoE 模型的表现差异。 | Gradio, 实验设计, 性能观测 |
| **190-240** | **模块六：综合实战与结课** | 完成综合实验，建立 AI 时代软件工程新思维。 | 项目实战, 工程化思维 |

---

## ⚠️ 实验安全注意事项

在开始实验之前，请仔细阅读并遵守以下安全规定：

### 1. 实验目的限制
* 本实验仅用于学术研究和教学目的
* 禁止将实验中涉及的技术用于任何恶意用途
* 实验内容仅供学习，不得用于生产环境

### 2. 数据安全
* 不要在实验中使用真实的敏感数据（密码、密钥、个人信息等）
* 实验使用模拟数据，请勿连接真实生产数据库
* 实验完成后，请清理所有临时文件和日志

### 3. 资源使用
* 注意监控系统资源使用情况，避免系统过载
* 如果内存不足，请关闭其他应用程序
* 合理控制模型调用频率，避免系统资源耗尽

### 4. 本地模型使用规范
* 仅使用授权的模型进行实验
* 不要将下载的模型文件分享给他人
* 注意模型文件大小，确保磁盘空间充足

---

## 🔧 环境准备与验证

### 1. 系统要求
* **操作系统**：Windows 10/11、macOS 或 Linux
* **Python 版本**：Python 3.10+
* **内存**：建议 16GB 以上（运行 qwen3.5:35b-a3b 建议 32GB 以上）
* **磁盘空间**：至少 20GB 可用空间（用于存储模型文件）
* **网络**：稳定的互联网连接（用于下载模型）

### 2. 安装 Ollama

#### Windows 安装
1. 访问 Ollama 官网：https://ollama.com/
2. 下载 Windows 安装包
3. 运行安装程序，按照提示完成安装
4. 安装完成后，打开新的终端窗口

#### macOS 安装
```bash
# 使用 Homebrew 安装
brew install ollama

# 或使用官方安装脚本
curl -fsSL https://ollama.com/install.sh | sh
```

#### Linux 安装
```bash
# 使用官方安装脚本
curl -fsSL https://ollama.com/install.sh | sh
```

### 3. 验证 Ollama 安装
```bash
# 检查 Ollama 版本
ollama --version

# 检查 Ollama 服务状态
ollama ps
```

**预期输出：**
```
ollama version 0.1.x
```

### 4. 下载模型
```bash
# 下载 qwen3.5:9b (Dense 模型，约 6GB)
ollama pull qwen3.5:9b

# 下载 qwen3.5:35b-a3b (MoE 模型，约 12GB)
ollama pull qwen3.5:35b-a3b

# 查看已下载的模型
ollama list
```

**预期输出：**
```
NAME              ID              SIZE      MODIFIED
qwen3.5:9b        ...             6.2 GB    2 minutes ago
qwen3.5:35b-a3b   ...             12.1 GB   1 minute ago
```

### 5. 测试本地模型
```bash
# 测试 qwen3.5:9b
ollama run qwen3.5:9b "你好，请用一句话介绍自己。"

# 测试 qwen3.5:35b-a3b
ollama run qwen3.5:35b-a3b "你好，请用一句话介绍自己。"
```

### 6. 验证 Python 环境
```bash
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version
```

**预期输出：**
```
Python 3.10.x
pip 23.x.x from ... (python 3.10)
```

### 7. 安装依赖
```bash
# 安装项目依赖
pip install gradio openai

# 验证安装
pip list | findstr "gradio openai"
```

**预期输出：**
```
gradio               4.x.x
openai               1.x.x
```

### 8. 验证 Ollama API 连接
```python
from openai import OpenAI

# 初始化 Ollama 客户端（使用 OpenAI 兼容接口）
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='local',
    timeout=120
)

# 测试连接
try:
    response = client.chat.completions.create(
        model="qwen3.5:9b",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ Ollama API 连接成功")
    print(f"模型回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Ollama API 连接失败: {e}")
```

**预期输出：**
```
✅ Ollama API 连接成功
模型回复: Hello! How can I help you today?
```

---

## 第一部分：理论基石与架构演进范式

在过去的二十年里，软件工程的核心是构建"确定性的指令流水线"；而随着大模型技术的爆发，核心正在转向构建"具备意图理解和自主规划能力的智能体网络"。

### 1. 传统 SaaS 架构的瓶颈 (巨石与强耦合)
传统 SaaS 奉行**"人适应机器"**的哲学。开发者在后端编写高度耦合的控制器（Controller），将数据库查询、业务计算、文件导出等步骤用 `if-else` 死死绑定。
*   **交互局限**：用户必须学习复杂的图形界面（GUI），并在固定的表单中输入严格格式的数据。
*   **扩展困境**：每增加一个新功能（例如新增导出 CSV），都需要从前端 UI、路由中间件到后端逻辑进行全链路重构。

### 2. AI Agent 与 MCP 架构的崛起 (解耦与意图驱动)
AI Agent 架构奉行**"机器适应人"**。软件不再提供固定的业务流水线，而是将核心能力剥离为一个个原子的、独立的**"工具 (Tools)"**。
*   **MCP (Model Context Protocol)**：扮演了标准化神经接口的角色。开发者只需编写一份 JSON 格式的"工具说明书 (Schema)"，大模型就能理解该工具的用途和参数要求。
*   **自然语言界面 (LUI)**：大模型作为中枢大脑，直接接收用户的模糊自然语言指令，自主拆解任务、规划路径，并按需调用底层 MCP 工具。

---

## 第二部分：Dense 模型与 MoE 模型的对比实验设计

在多工具编排（如：查数据 -> 算工资 -> 导出文件）这种长上下文、高逻辑依赖的场景中，基座模型的能力决定了 Agent 的上限。本实验特别设计了针对两种不同架构大模型的对比观察：

### 1. 稠密模型 (Dense Model)：以 `qwen3.5:9b` 为代表
*   **架构特点**：每次推理时，模型的所有参数（90 亿）都会被激活并参与计算。
*   **实验观察预期**：在单次、简单的工具调用中表现优异。但在"连续多步工具调用（Chain of Actions）"中，由于上下文视窗变长，可能会出现参数提取遗漏、格式幻觉，或者在执行到第三步时忘记了第一步获取的数据。

### 2. 混合专家模型 (MoE Model)：以 `qwen3.5:35b-a3b` 为代表
*   **架构特点**：总参数量更大（350 亿），但在每次推理时，只有部分"专家网络"（约 30 亿参数）被动态激活（Sparse Activation）。
*   **实验观察预期**：MoE 架构天生更擅长处理复杂的任务路由和逻辑分发。在多步链式推理中，它能极其稳定地维持"思考 -> 行动 -> 观察"的循环，精准地将上一个工具的输出 JSON 转换为下一个工具的输入参数，极大地降低逻辑断链的概率。

---

## 第三部分：实战演练 —— 循序渐进的代码实现

本环节将实现一个真实的财务业务流：**查询员工名单 -> 计算工资与五险一金 -> 导出 CSV 文件**。
我们将代码拆分为 6 个阶段，您可以将其按顺序拼接为一个完整的 `app.py` 运行。

### 阶段 1：环境初始化与底层数据构建
无论是传统软件还是 AI 智能体，底层的数据资产是永恒不变的。

```python
import gradio as gr
import json
import os
import time
import csv
import tempfile
import logging
from datetime import datetime
from openai import OpenAI

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 1. 初始化 Ollama 客户端（使用 OpenAI 兼容接口）
try:
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='local',
        timeout=120
    )
    print("✅ Ollama 客户端初始化成功")
except Exception as e:
    print(f"❌ Ollama 客户端初始化失败: {e}")
    raise

# 2. 模拟底层的核心关系型数据库 (花名册与薪资等级)
mock_employees = [
    {"id": "E01", "name": "张三", "level": "L1"},
    {"id": "E02", "name": "李四", "level": "L2"},
    {"id": "E03", "name": "王五", "level": "L3"}
]

mock_salary_levels = {"L1": 10000, "L2": 20000, "L3": 35000}
```

### 阶段 2：构建原子化业务工具库 (Atomic Tools)
将庞大的业务逻辑解构为纯粹的、无 UI 耦合的 Python 函数。这些就是未来挂载到 MCP 上的核心资产。

```python
# 工具 A：仅负责查询全量员工基础数据
def get_employee_directory():
    """返回全公司员工的花名册 JSON"""
    try:
        if not mock_employees:
            return json.dumps({"error": "员工数据为空"}, ensure_ascii=False)
        return json.dumps(mock_employees, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

# 工具 B：仅负责算薪与扣税 (不关心数据从哪来，只负责处理传入的 JSON)
def calculate_payroll_and_tax(employees_json: str):
    """接收员工 JSON，计算五险一金和实发工资"""
    try:
        if not employees_json or not employees_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            employees = json.loads(employees_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        if not isinstance(employees, list):
            return json.dumps({"error": "输入数据格式错误，应为数组"}, ensure_ascii=False)
        
        if len(employees) == 0:
            return json.dumps({"error": "员工列表为空"}, ensure_ascii=False)
        
        results = []
        for emp in employees:
            if not isinstance(emp, dict):
                continue
            if "level" not in emp:
                emp_result = emp.copy()
                emp_result["error"] = "缺少 level 字段"
                results.append(emp_result)
                continue
            
            base_salary = mock_salary_levels.get(emp["level"], 0)
            if base_salary <= 0:
                emp_result = emp.copy()
                emp_result["error"] = f"无效的职级: {emp.get('level')}"
                results.append(emp_result)
                continue
            
            social_security = base_salary * 0.20
            tax = max(0, (base_salary - social_security) * 0.05)
            net_salary = base_salary - social_security - tax
            
            emp_result = emp.copy()
            emp_result.update({
                "应发工资": base_salary,
                "五险一金扣除": social_security,
                "个税扣除": tax,
                "实发工资": net_salary
            })
            results.append(emp_result)
        
        if not results:
            return json.dumps({"error": "没有有效的员工数据"}, ensure_ascii=False)
            
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"计算失败: {str(e)}"}, ensure_ascii=False)

# 工具 C：仅负责将传入的 JSON 写成物理 CSV 文件
def export_payroll_csv(payroll_json: str):
    """接收算好工资的 JSON，生成文件并返回系统路径"""
    try:
        if not payroll_json or not payroll_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            payroll_data = json.loads(payroll_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        if not isinstance(payroll_data, list) or len(payroll_data) == 0:
            return json.dumps({"error": "工资数据为空或格式错误"}, ensure_ascii=False)
        
        filepath = os.path.join(tempfile.gettempdir(), "payroll_report.csv")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=payroll_data[0].keys())
                writer.writeheader()
                writer.writerows(payroll_data)
        except IOError as e:
            return json.dumps({"error": f"文件写入失败: {str(e)}"}, ensure_ascii=False)
            
        return json.dumps({"status": "success", "file_path": filepath, "record_count": len(payroll_data)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"导出失败: {str(e)}"}, ensure_ascii=False)
```

### 阶段 3：构建 SaaS 对照组 (巨石控制器)
展示传统开发的"硬编码"特性：开发者必须规定死输入输出格式，一旦需求变更（例如用户不想导出文件），这套流水线就失效了。

```python
def saas_generate_payroll_api():
    """传统 SaaS 后端接口：硬编码的流水线，高度耦合"""
    try:
        time.sleep(1) # 模拟系统耗时
        
        # 步骤被严格固化，依次执行：查数据 -> 算工资 -> 导出
        emp_str = get_employee_directory()
        if "error" in emp_str:
            raise Exception(emp_str)
            
        payroll_str = calculate_payroll_and_tax(emp_str)
        if "error" in payroll_str:
            raise Exception(payroll_str)
            
        export_result = json.loads(export_payroll_csv(payroll_str))
        if "error" in export_result:
            raise Exception(export_result["error"])
        
        # 必须针对前端 UI 的表格组件进行特定的二维数组清洗
        payroll_data = json.loads(payroll_str)
        table_data = [[d["name"], d["level"], d["应发工资"], d["五险一金扣除"], d["实发工资"]] for d in payroll_data]
        
        # 严格返回元组，供前端强绑定渲染
        return table_data, export_result.get("file_path")
    except Exception as e:
        print(f"❌ SaaS 执行失败: {e}")
        return [[str(e), "", "", "", ""]], None
```

**📊 预期结果：**
执行成功后，将在表格中显示所有员工的工资信息，并生成 CSV 文件。

### 阶段 4：构建 Agent 的"神经接口" (MCP Schema)
这是大模型操控软件的唯一媒介。大模型依靠这段 JSON Schema 动态了解系统的能力边界。

```python
# MCP 标准定义：告诉大模型有哪些工具、如何传递参数
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_directory",
            "description": "第一步：获取全公司所有员工的基础数据（包含姓名和职级）。不需要参数。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_payroll_and_tax",
            "description": "第二步：接收员工基础数据 JSON，计算实发工资。必须在获取员工名单后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employees_json": {"type": "string", "description": "由 get_employee_directory 返回的 JSON 数据"}
                },
                "required": ["employees_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_payroll_csv",
            "description": "第三步：将工资详细信息的 JSON 数据导出为 CSV 文件。必须在计算完工资后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "payroll_json": {"type": "string", "description": "由 calculate_payroll_and_tax 返回的工资 JSON"}
                },
                "required": ["payroll_json"]
            }
        }
    }
]
```

### 阶段 5：Agent 核心调度器 (链式推理中枢)
本段代码是现代 AI 软件工程的灵魂所在。我们通过 `while True` 循环，赋予了大模型**"反思与继续执行"**的能力，让它能在 Dense 和 MoE 架构下展现真正的规划水平。

```python
def agent_orchestrator(user_message, history, messages_state, selected_model):
    """
    Agent 的大脑调度器。接收用户指令，并根据选择的模型（qwen3.5:9b 或 qwen3.5:35b-a3b）进行推理。
    """
    try:
        logger.info(f"开始处理用户请求: {user_message}, 模型: {selected_model}")
        
        # 1. 严格的 System Prompt，框定 Agent 行为规范
        if not messages_state:
            messages_state = [{"role": "system", "content": "你是专业的 HR 助手。请自动规划工具调用链完成计算。输出最终结果时，请用 Markdown 表格展示，并附上文件下载路径。"}]
            logger.info("初始化系统提示词")
        
        messages_state.append({"role": "user", "content": user_message})
        history.append((user_message, f"🤖 [当前引擎: {selected_model}] 正在规划任务流..."))
        yield history, messages_state
        
        # 2. 开启无限循环：这是实现多工具接力 (Chain of Actions) 的核心机制
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始迭代 {iteration}/{max_iterations}")
            
            try:
                # 向所选模型发起请求，赋予其 tool_choice="auto" 的自主权
                logger.info(f"调用模型 {selected_model} 进行推理")
                response = client.chat.completions.create(
                    model=selected_model, 
                    messages=messages_state, 
                    tools=tools_schema, 
                    tool_choice="auto"
                )
                response_msg = response.choices[0].message
                messages_state.append(response_msg)
                
                # 3. 拦截判断：模型是否要求调用底层工具？
                if response_msg.tool_calls:
                    logger.info(f"模型请求调用 {len(response_msg.tool_calls)} 个工具")
                    
                    for tool_call in response_msg.tool_calls:
                        func_name = tool_call.function.name
                        logger.info(f"准备调用工具: {func_name}")
                        
                        # 解析模型推理出的参数
                        try:
                            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            logger.info(f"工具参数: {func_args}")
                        except json.JSONDecodeError as e:
                            logger.warning(f"工具参数解析失败: {e}")
                            func_args = {}
                        
                        # 在前端流式打印当前的执行进度
                        history[-1] = (user_message, history[-1][1] + f"\n\n> 🛠️ **触发节点**: `{func_name}`")
                        yield history, messages_state
                        
                        # 4. 动态路由：实际执行本地 Python 业务代码
                        start_time = time.time()
                        if func_name == "get_employee_directory":
                            tool_result = get_employee_directory()
                        elif func_name == "calculate_payroll_and_tax":
                            tool_result = calculate_payroll_and_tax(employees_json=func_args.get("employees_json", "[]"))
                        elif func_name == "export_payroll_csv":
                            tool_result = export_payroll_csv(payroll_json=func_args.get("payroll_json", "[]"))
                        else:
                            logger.error(f"未找到指定工具: {func_name}")
                            tool_result = json.dumps({"error": f"未找到指定工具: {func_name}"})
                        
                        execution_time = time.time() - start_time
                        logger.info(f"工具 {func_name} 执行完成，耗时: {execution_time:.2f}秒")
                        
                        # 5. 上下文回注：将物理世界的真实执行结果，作为 Context 塞回给大模型
                        messages_state.append({
                            "role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": tool_result
                        })
                        logger.info(f"工具结果已回注到上下文")
                    
                    # 【重点】遇到 continue 意味着当前循环不退出！大模型会带着新拿到的数据，进入下一轮判断
                    logger.info("继续下一轮迭代")
                    continue 

                else:
                    # 6. 出口条件：当大模型认为所有工具调用完毕，它会输出自然语言总结，此时退出循环
                    final_text = response_msg.content
                    logger.info(f"模型输出最终结果: {final_text[:100]}...")
                    
                    messages_state.append({"role": "assistant", "content": final_text})
                    history[-1] = (user_message, final_text)
                    yield history, messages_state
                    break 
                    
            except Exception as e:
                logger.error(f"迭代 {iteration} 执行失败: {str(e)}", exc_info=True)
                error_msg = f"❌ 迭代 {iteration} 执行失败: {str(e)}"
                history[-1] = (user_message, history[-1][1] + f"\n\n{error_msg}")
                yield history, messages_state
                break
                
        if iteration >= max_iterations:
            logger.warning(f"已达到最大迭代次数 {max_iterations}，任务可能未完成")
            history[-1] = (user_message, history[-1][1] + "\n\n⚠️ 已达到最大迭代次数，任务可能未完成")
            yield history, messages_state
            
        logger.info(f"用户请求处理完成，总迭代次数: {iteration}")
            
    except Exception as e:
        logger.error(f"Agent 调度器执行失败: {str(e)}", exc_info=True)
        error_msg = f"❌ Agent 调度器执行失败: {str(e)}"
        history.append((user_message, error_msg))
        yield history, messages_state
```

**📊 预期结果：**
- **qwen3.5:9b (Dense)**：在简单单步调用中表现良好，但在多步链式调用中可能出现参数遗漏或逻辑断链
- **qwen3.5:35b-a3b (MoE)**：在多步链式调用中表现稳定，能够精准维护上下文和逻辑链条

**💡 思考问题：**
* 为什么 MoE 模型在多步调用中表现更稳定？
* Dense 模型在什么情况下会出现逻辑断链？
* 如何提高 Agent 的执行稳定性？

### 阶段 6：双轨对比前端与实验 UI 组装
构建交互界面，将静态的 SaaS 流水线与动态的 Agent 编排并排展示，并提供模型架构的切换开关。

```python
# 使用 Gradio 构建现代且极简的 Web UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 💸 现代软件架构实验：SaaS 巨石架构 vs Agent 动态编排")
    
    with gr.Row():
        # ================= 控制组：传统 SaaS 面板 =================
        with gr.Column(scale=1):
            gr.Markdown("### 🏢 控制组：SaaS (硬编码)")
            gr.Markdown("> 极度高效，但极度死板。开发者提前锁死了业务流。")
            
            saas_btn = gr.Button("🚀 一键执行：生成工资单并下载", variant="primary")
            saas_table = gr.Dataframe(headers=["姓名", "职级", "应发", "五险一金", "实发"])
            saas_file = gr.File(label="导出的物理文件")
            
            # 事件绑定：点击按钮即触发巨石函数
            saas_btn.click(fn=saas_generate_payroll_api, inputs=None, outputs=[saas_table, saas_file])
            
        # ================= 实验组：AI Agent 面板 =================
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 实验组：Agent (意图驱动)")
            
            # 【实验核心变量控制】允许动态切换 Dense 和 MoE 模型进行观察
            model_selector = gr.Dropdown(
                choices=["qwen3.5:9b", "qwen3.5:35b-a3b"], 
                value="qwen3.5:35b-a3b", 
                label="🧪 核心变量：选择底层大模型架构 (Dense vs MoE)"
            )
            
            messages_state = gr.State([]) 
            chatbot = gr.Chatbot(label="Agent 神经推理中枢日志", height=450)
            chat_input = gr.Textbox(label="自然语言指令", placeholder="输入测试用例：帮我查一下全公司的工资，算好扣税，然后给我个 CSV 文件")
            
            # 事件绑定：将用户输入和选择的模型参数一并传入智能调度器
            chat_input.submit(
                fn=agent_orchestrator, 
                inputs=[chat_input, chatbot, messages_state, model_selector], 
                outputs=[chatbot, messages_state]
            ).then(lambda: "", None, chat_input)

if __name__ == "__main__":
    demo.launch()
```

---

## 实验总结与教学启发

通过这份完整的代码实现，我们能够清晰地得出以下工程视角的结论：

1.  **架构维度的降维打击**：SaaS 时代的开发者在编写"功能"；而 Agent 时代的开发者在编写"能力边界"。当您在实验中输入"我不想导出文件，只看李四的工资"时，SaaS 只能全量跑完并报错，而 Agent 会自主阻断工具 C 的调用，展现出极高的**系统柔韧度**。
2.  **模型维度的深刻对比**：在切换 `qwen3.5:9b` (Dense) 和 `qwen3.5:35b-a3b` (MoE) 运行上述多步骤指令时，您可以直观监测到 MoE 架构在处理长距离逻辑依赖（从第一步查字典，到第三步写文件）时，其动态路由专家的机制能显著降低参数丢失和幻觉产生的概率，这也是为什么当今业界复杂的顶层 Agent 应用均偏向于采用超大参数的 MoE 基座模型。

---

## 🐛 故障排除指南

### 问题 1：Ollama 服务未启动
**症状**：运行时出现连接错误
**解决方案**：
1. 检查 Ollama 服务是否正在运行
2. Windows：检查系统托盘中是否有 Ollama 图标
3. macOS/Linux：运行 `ollama serve` 启动服务
4. 重启 Ollama 服务

### 问题 2：模型未找到
**症状**：调用模型时出现"model not found"错误
**解决方案**：
1. 检查模型是否已下载：`ollama list`
2. 下载模型：`ollama pull qwen3.5:9b` 或 `ollama pull qwen3.5:35b-a3b`
3. 确认模型名称拼写正确（使用冒号 `qwen3.5:9b`）

### 问题 3：内存不足
**症状**：模型加载失败或系统卡死
**解决方案**：
1. 关闭其他应用程序释放内存
2. 使用较小的模型（qwen3.5:9b 而不是 qwen3.5:35b-a3b）
3. 增加系统虚拟内存
4. 考虑使用 INT4 量化版本的模型

### 问题 4：Agent 执行中断
**症状**：Agent 在多步调用中出现逻辑断链
**解决方案**：
1. 切换到 MoE 模型（qwen3.5:35b-a3b）
2. 检查 System Prompt 是否清晰明确
3. 增加最大迭代次数限制
4. 优化工具描述，使其更清晰

### 问题 5：CSV 文件导出失败
**症状**：无法生成 CSV 文件
**解决方案**：
1. 检查临时目录权限
2. 验证输入的 JSON 格式是否正确
3. 检查数据是否为空

---

## 🧹 环境清理步骤

实验完成后，请按照以下步骤清理环境：

### 1. 停止应用程序
```bash
# 按 Ctrl+C 停止 Gradio 服务
# 或者关闭终端窗口
```

### 2. 停止 Ollama 服务（可选）
```bash
# Windows：在系统托盘右键点击 Ollama 图标，选择退出
# macOS/Linux：按 Ctrl+C 停止 ollama serve 进程
```

### 3. 清理临时文件
```python
import os
import tempfile

# 清理临时 CSV 文件
csv_path = os.path.join(tempfile.gettempdir(), "payroll_report.csv")
if os.path.exists(csv_path):
    os.remove(csv_path)
    print(f"✅ 已清理临时文件: {csv_path}")
```

### 4. 删除模型（可选）
```bash
# 查看已下载的模型
ollama list

# 删除模型
ollama rm qwen3.5:9b
ollama rm qwen3.5:35b-a3b
```

### 5. 卸载依赖（可选）
```bash
# 卸载项目依赖
pip uninstall -y gradio openai
```

### 6. 卸载 Ollama（可选）
```bash
# Windows：通过控制面板卸载
# macOS：brew uninstall ollama
# Linux：根据安装方式选择相应的卸载方法
```

---

## � 实验总结

### 1. 核心收获

通过本次实验，您应该已经掌握了以下关键知识：

**架构理解：**
- 传统 SaaS 架构与 AI Agent 架构的本质区别
- Dense 模型与 MoE 模型的架构特点和性能差异
- MCP 协议在 AI Agent 中的核心作用

**工程实践：**
- 原子化业务工具的设计原则
- Agent 调度器的实现机制
- 多工具链式调用的工作原理
- 自然语言界面（LUI）的构建方法

**思维转变：**
- 从"功能开发"到"能力边界定义"的思维转变
- 从"硬编码流程"到"意图驱动"的设计理念
- 从"单体应用"到"分布式智能体"的架构演进

### 2. 关键观察

在实验过程中，您可能观察到以下现象：

**SaaS 架构：**
- ✅ 执行效率高，响应速度快
- ❌ 灵活性差，难以应对变更需求
- ❌ 扩展性受限，新增功能需要全链路修改

**AI Agent 架构：**
- ✅ 灵活性强，能够理解自然语言意图
- ✅ 扩展性好，新增工具只需添加 Schema
- ❌ 执行效率相对较低，存在推理开销
- ❌ 对模型能力依赖较高

**Dense 模型（qwen3.5:9b）：**
- ✅ 单次调用表现良好
- ✅ 资源占用相对较小
- ❌ 多步链式调用容易出现逻辑断链
- ❌ 上下文维护能力有限

**MoE 模型（qwen3.5:35b-a3b）：**
- ✅ 多步链式调用表现稳定
- ✅ 上下文维护能力强
- ✅ 复杂任务路由能力优秀
- ❌ 资源占用较大
- ❌ 单次调用开销相对较高

### 3. 思考问题

请思考以下问题：

1. **架构选择**：在什么场景下应该选择传统 SaaS 架构？在什么场景下应该选择 AI Agent 架构？

2. **模型选择**：如何根据业务需求选择合适的模型架构（Dense vs MoE）？

3. **成本效益**：如何平衡 AI Agent 的灵活性和执行效率？

4. **可靠性**：如何提高 AI Agent 系统的可靠性和稳定性？

5. **安全性**：AI Agent 架构存在哪些安全风险？如何防范？

---

## ❓ 常见问题 FAQ

### Q1: 为什么我的 Agent 总是调用错误的工具？

**A:** 可能的原因和解决方案：
- 检查 System Prompt 是否清晰明确
- 优化工具描述（tools_schema），确保功能描述准确
- 检查参数定义是否完整和准确
- 尝试使用更强大的模型（如 qwen3.5:35b-a3b）

### Q2: 如何提高 Agent 的执行速度？

**A:** 可以尝试以下方法：
- 使用较小的模型（如 qwen3.5:9b）
- 优化 System Prompt，减少不必要的约束
- 实现工具调用缓存机制
- 增加并发处理能力
- 使用模型量化技术减少推理时间

### Q3: Agent 出现幻觉怎么办？

**A:** 可以采取以下措施：
- 优化 System Prompt，增加约束条件
- 增加工具调用结果的验证机制
- 实现多轮确认机制
- 使用更强大的模型
- 增加示例（Few-shot learning）

### Q4: 如何添加更多的业务工具？

**A:** 添加新工具的步骤：
1. 实现工具函数（遵循原子化原则）
2. 在 tools_schema 中添加工具描述
3. 在 agent_orchestrator 中添加工具调用路由
4. 更新 System Prompt（可选）

### Q5: 如何实现多 Agent 协作？

**A:** 实现多 Agent 协作的方法：
1. 定义不同角色的 Agent（如：规划 Agent、执行 Agent、验证 Agent）
2. 实现 Agent 之间的通信机制
3. 设计任务分配和协调策略
4. 实现结果汇总和验证机制

---

## 🚀 扩展性思考

### 1. 功能扩展

**业务功能扩展：**
- 新增员工管理工具（增删改查）
- 实现考勤管理功能
- 添加绩效评估系统
- 实现报表生成和数据分析

**系统功能扩展：**
- 实现用户权限管理
- 添加操作审计日志
- 实现数据持久化存储
- 添加任务队列和异步处理

### 2. 性能优化

**模型性能优化：**
- 实现模型缓存机制
- 使用模型量化技术
- 优化提示词工程
- 实现批量处理能力

**系统性能优化：**
- 实现工具调用缓存
- 添加并发处理能力
- 优化数据库查询
- 使用消息队列解耦

### 3. 安全加固

**输入安全：**
- 实现输入验证和过滤
- 添加敏感信息检测
- 实现 SQL 注入防护
- 添加 XSS 防护

**输出安全：**
- 实现输出审查机制
- 添加敏感信息过滤
- 实现代码沙箱执行
- 添加结果验证机制

**访问安全：**
- 实现身份认证
- 添加权限控制
- 实现 API 限流
- 添加日志审计

### 4. 架构演进

**从单 Agent 到多 Agent：**
- 实现 Agent 角色分工
- 设计 Agent 通信协议
- 实现任务分配机制
- 添加结果验证和汇总

**从本地部署到云原生：**
- 实现容器化部署
- 添加服务编排
- 实现自动扩缩容
- 添加监控和告警

**从单机到分布式：**
- 实现服务拆分
- 添加服务发现
- 实现负载均衡
- 添加容错机制

---

## 🧪 单元测试示例

为了确保系统的可靠性和稳定性，建议编写单元测试。以下是一些测试示例：

### 1. 工具函数测试

```python
import unittest
import json
from your_app_file import get_employee_directory, calculate_payroll_and_tax, export_payroll_csv

class TestTools(unittest.TestCase):
    def test_get_employee_directory(self):
        result = get_employee_directory()
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
    
    def test_calculate_payroll_and_tax_with_valid_data(self):
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L1"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("应发工资", data[0])
        self.assertIn("实发工资", data[0])
    
    def test_calculate_payroll_and_tax_with_empty_data(self):
        result = calculate_payroll_and_tax("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_invalid_json(self):
        result = calculate_payroll_and_tax("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_export_payroll_csv_with_valid_data(self):
        payroll_data = json.dumps([
            {"id": "E01", "name": "张三", "level": "L1", "应发工资": 10000, "实发工资": 8000}
        ])
        result = export_payroll_csv(payroll_data)
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("file_path", data)

if __name__ == "__main__":
    unittest.main()
```

### 2. Agent 调度器测试

```python
import unittest
from unittest.mock import Mock, patch
from your_app_file import agent_orchestrator

class TestAgentOrchestrator(unittest.TestCase):
    @patch("your_app_file.client")
    def test_agent_orchestrator_with_simple_query(self, mock_client):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "这是测试回复"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        
        history = []
        messages_state = []
        
        for result in agent_orchestrator("测试问题", history, messages_state, "qwen3.5:9b"):
            updated_history, updated_messages = result
        
        self.assertEqual(len(updated_history), 1)
        self.assertIn("测试回复", updated_history[0][1])
    
    @patch("your_app_file.client")
    def test_agent_orchestrator_with_tool_call(self, mock_client):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function = Mock()
        mock_response.choices[0].message.tool_calls[0].function.name = "get_employee_directory"
        mock_response.choices[0].message.tool_calls[0].function.arguments = "{}"
        mock_client.chat.completions.create.return_value = mock_response
        
        history = []
        messages_state = []
        
        for result in agent_orchestrator("查询员工", history, messages_state, "qwen3.5:9b"):
            updated_history, updated_messages = result
        
        self.assertGreater(len(updated_messages), 0)

if __name__ == "__main__":
    unittest.main()
```

### 3. 集成测试

```python
import unittest
import subprocess
import time
import requests

class TestIntegration(unittest.TestCase):
    def test_gradio_launch(self):
        process = subprocess.Popen(["python", "your_app_file.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(5)
        
        try:
            response = requests.get("http://localhost:7860")
            self.assertEqual(response.status_code, 200)
        finally:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    unittest.main()
```

### 4. 性能测试

```python
import time
import json
from your_app_file import get_employee_directory, calculate_payroll_and_tax

def test_performance():
    print("开始性能测试...")
    
    # 测试 get_employee_directory
    start_time = time.time()
    for i in range(100):
        get_employee_directory()
    avg_time = (time.time() - start_time) / 100
    print(f"get_employee_directory 平均耗时: {avg_time:.4f} 秒")
    
    # 测试 calculate_payroll_and_tax
    employees = get_employee_directory()
    start_time = time.time()
    for i in range(100):
        calculate_payroll_and_tax(employees)
    avg_time = (time.time() - start_time) / 100
    print(f"calculate_payroll_and_tax 平均耗时: {avg_time:.4f} 秒")
    
    print("性能测试完成")

if __name__ == "__main__":
    test_performance()
```

---

## 📝 代码风格指南

为了保持代码的一致性和可维护性，请遵循以下代码风格指南：

### 1. 命名规范

**变量和函数：**
- 使用小写字母和下划线（snake_case）
- 命名应该具有描述性
- 避免使用单字符变量名（除了循环变量）

**常量：**
- 使用大写字母和下划线（UPPER_CASE）
- 在模块顶部定义

**类：**
- 使用驼峰命名法（CamelCase）
- 类名应该是名词或名词短语

### 2. 代码格式

**缩进：**
- 使用 4 个空格缩进
- 不要使用制表符（Tab）

**行长：**
- 每行不超过 80 个字符
- 长表达式应该适当换行

**空行：**
- 函数之间空两行
- 类方法之间空一行
- 逻辑块之间空一行

### 3. 注释规范

**文档字符串：**
- 所有公共模块、类、方法和函数都应该有文档字符串
- 使用三重双引号（`"""`）
- 包含功能描述、参数说明、返回值说明

**行内注释：**
- 用于解释复杂的逻辑
- 与代码保持适当距离
- 使用中文注释（便于中文开发者理解）

### 4. 导入规范

**导入顺序：**
1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入
- 各组之间空一行

**导入方式：**
- 避免使用 `from module import *`
- 使用绝对导入

### 5. 异常处理

**不要捕获所有异常：**
- 只捕获预期的异常
- 避免使用裸 `except:`

**异常信息：**
- 提供有意义的错误消息
- 记录异常栈追踪

**资源清理：**
- 使用 `try-finally` 或 `with` 语句确保资源清理

---

## 🎓 教学建议

### 对于教师

1. **实验前准备：**
   - 确保所有学生的环境配置正确
   - 提前下载好模型文件
   - 准备好示例代码和演示

2. **实验过程中：**
   - 鼓励学生自己动手实践
   - 引导学生观察和思考
   - 及时解答学生的问题
   - 鼓励学生之间的讨论和交流

3. **实验后：**
   - 组织学生分享实验心得
   - 引导学生思考架构选择的原则
   - 布置扩展性任务

### 对于学生

1. **实验前：**
   - 预习相关理论知识
   - 准备好实验环境
   - 阅读实验手册

2. **实验中：**
   - 认真完成每个步骤
   - 仔细观察实验现象
   - 记录实验过程和结果
   - 遇到问题及时请教

3. **实验后：**
   - 总结实验收获
   - 思考扩展性问题
   - 完成实验报告
   - 探索更多可能性

---

## 🔮 未来展望

随着大模型技术的不断发展，AI Agent 架构将会在更多领域得到应用：

### 1. 企业应用

- **智能客服**：能够理解复杂问题，自主调用后端工具解决问题
- **智能办公**：自动化处理文档、邮件、会议等办公任务
- **智能决策**：基于数据分析和业务规则提供决策建议

### 2. 行业应用

- **金融科技**：智能风控、智能投顾、智能理赔
- **医疗健康**：智能诊断、智能用药、智能健康管理
- **教育培训**：智能辅导、智能测评、个性化学习

### 3. 技术趋势

- **多模态 Agent**：结合文本、图像、音频、视频等多种模态
- **多 Agent 协作**：多个 Agent 分工协作，完成复杂任务
- **Agent 记忆机制**：实现长期记忆和知识积累
- **Agent 学习能力**：从经验中学习，不断优化行为

### 4. 挑战与机遇

**挑战：**
- 可靠性和稳定性
- 安全性和隐私保护
- 可解释性和透明度
- 成本和效率

**机遇：**
- 全新的产品形态
- 颠覆性的用户体验
- 巨大的市场潜力
- 广阔的应用场景

---

## 📚 扩展阅读

### 书籍推荐

- **《Building Agents with Large Language Models》** - 深入讲解 AI Agent 的设计和实现
- **《AI Agent Engineering》** - AI Agent 工程化实践指南
- **《Large Language Models in Production》** - 大模型在生产环境中的应用

### 论文推荐

- **"ReAct: Synergizing Reasoning and Acting in Language Models"** - 提出了 ReAct 框架
- **"Toolformer: Language Models Can Teach Themselves to Use Tools"** - 展示了模型如何自主学习使用工具
- **"AutoGPT: Building Autonomous Agents with GPT-4"** - AutoGPT 的实现原理和应用

### 开源项目

- **AutoGPT** - 最著名的 AI Agent 项目之一
- **LangChain** - 构建 LLM 应用的框架
- **LlamaIndex** - 数据索引和查询框架
- **CrewAI** - 多 Agent 协作框架

---

## 🙏 致谢

感谢以下组织和个人对本实验的支持：

- **Ollama 团队** - 提供了优秀的本地模型部署工具
- **Qwen 团队** - 提供了高质量的开源模型
- **Gradio 团队** - 提供了便捷的 Web UI 框架
- **所有参与实验的学生和教师**

---

## 📞 反馈与支持

如果您在实验过程中遇到问题或有任何建议，请通过以下方式联系：

- **邮箱**：liujinhang@hbut.edu.cn
- **GitHub**：https://github.com/hbut-edu/MSD
- **issue**：欢迎提交 Issue 和 Pull Request

---

**祝您实验愉快！希望本次实验能够帮助您建立 AI 时代软件工程的新思维！**

---

*最后更新时间：2026-03-30*

---

## �📚 参考资源

### 官方文档
* **Ollama 官方文档**：https://github.com/ollama/ollama
* **OpenAI API 文档**：https://platform.openai.com/docs/
* **Gradio 文档**：https://www.gradio.app/docs
* **Qwen 模型**：https://github.com/QwenLM/Qwen

### 技术文章
* **AI Agent 架构设计**：https://lilianweng.github.io/posts/2023-06-23-agent/
* **MoE 模型详解**：https://arxiv.org/abs/2211.15841
* **MCP 协议规范**：https://modelcontextprotocol.io/

### 学习资源
* **AI Agent 实战课程**：https://www.deeplearning.ai/short-courses/multi-ai-agent-systems/
* **大模型应用开发**：https://www.coursera.org/learn/llm-application-development

---

## ✅ 实验完成检查清单

在完成实验后，请确认您已经掌握以下内容：

- [ ] 理解传统 SaaS 架构与 AI Agent 架构的核心差异
- [ ] 掌握 Dense 与 MoE 模型架构的特点
- [ ] 能够安装和配置本地 Ollama 环境
- [ ] 能够下载和管理本地模型
- [ ] 能够构建原子化业务工具库
- [ ] 理解 MCP 工具定义规范
- [ ] 能够实现 Agent 核心调度器
- [ ] 掌握多工具链式调用的实现
- [ ] 能够观测和对比不同模型的表现
- [ ] 建立 AI 时代软件工程的新思维

---

## 🎯 扩展学习路径

对于学有余力的学生，可以继续探索以下方向：

1. **进阶功能开发**
   * 实现更多业务工具
   * 添加用户权限管理
   * 实现数据持久化存储

2. **性能优化**
   * 优化 Agent 调度策略
   * 实现工具调用缓存
   * 添加并发处理能力

3. **安全加固**
   * 实现输入验证
   * 添加敏感信息过滤
   * 实现审计日志功能

4. **架构演进**
   * 探索多 Agent 协作
   * 实现 Agent 记忆机制
   * 探索 Agent 学习能力
