"""传统 SaaS 与 AI Agent 双轨对比实验应用。

本文件故意把同一组 HR 工资业务拆成两种实现方式：
1. 传统 SaaS 控制器：由程序员预先写死“查询员工 -> 计算工资 -> 导出 CSV”的流程。
2. AI Agent 调度器：由大模型根据自然语言请求自行决定何时调用哪些工具。

课堂阅读建议：
- 先看模拟数据和三个工具函数，理解业务能力的最小闭环。
- 再看 `saas_generate_payroll_api`，观察传统后端如何串联固定流程。
- 最后看 `agent_orchestrator`，观察模型 tool calling 如何把工具结果回注给模型继续推理。
"""

import json
import os
import time
import csv
import tempfile
import logging
from datetime import datetime

# OpenAI Python SDK 可以直接调用 Ollama 暴露的 OpenAI 兼容接口。
# 如果同学只想运行单元测试而尚未安装 openai，也允许业务函数继续被测试。
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ==================== 日志配置 ====================
# 日志同时写入文件和终端，便于课堂观察 Agent 的每一轮决策过程。
# `agent_orchestrator.log` 是后续分析“模型为何调用某个工具”的主要证据。
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 初始化客户端 ====================
# Ollama 默认监听 http://localhost:11434，并提供 /v1 兼容 OpenAI 的 Chat Completions API。
# api_key 对本地 Ollama 没有真实鉴权意义，但 OpenAI SDK 要求该字段存在。
client = None
if OpenAI is not None:
    try:
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='local',
            timeout=120
        )
        print("✅ Ollama 客户端初始化成功")
    except Exception as e:
        print(f"❌ Ollama 客户端初始化失败: {e}")
else:
        print("⚠️ OpenAI 模块不可用，仅测试业务逻辑")

# ==================== 模拟数据 ====================
# 为了让实验可离线、可复现，这里不连接真实数据库，而是使用内存中的假员工数据。
# 每个员工只保留最小字段：员工编号、姓名、职级。职级会在工资计算阶段映射为基础工资。
mock_employees = [
    {"id": "E01", "name": "张三", "level": "L1"},
    {"id": "E02", "name": "李四", "level": "L2"},
    {"id": "E03", "name": "王五", "level": "L3"}
]

# 职级到基础工资的映射表。真实系统通常会来自 HR 数据库或薪酬服务。
mock_salary_levels = {"L1": 10000, "L2": 20000, "L3": 35000}

# ==================== 工具函数 ====================
def get_employee_directory():
    """返回全公司员工的花名册 JSON。

    这个函数模拟“员工目录服务”。Agent 调用它时不需要参数，因此它适合作为工具链第一步。
    返回值统一使用 JSON 字符串，是为了和大模型 tool calling 的文本边界保持一致。
    """
    try:
        # 防御式检查：即使模拟数据被清空，也返回结构化错误，避免调用方拿到 None。
        if not mock_employees:
            return json.dumps({"error": "员工数据为空"}, ensure_ascii=False)

        # ensure_ascii=False 保留中文，方便前端和日志直接阅读。
        return json.dumps(mock_employees, ensure_ascii=False)
    except Exception as e:
        # 工具函数不向外抛异常，而是把错误封装为 JSON；这能让 Agent 把错误作为上下文继续处理。
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

def calculate_payroll_and_tax(employees_json: str):
    """接收员工 JSON，计算五险一金、个税和实发工资。

    Args:
        employees_json: `get_employee_directory` 返回的员工列表 JSON 字符串。

    Returns:
        JSON 字符串。成功时为工资明细列表；失败时为 `{"error": "..."}`。
    """
    try:
        # 工具调用参数来自模型生成，必须先做空值校验，不能默认模型永远传对。
        if not employees_json or not employees_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            # 将模型传入的字符串恢复为 Python 对象。解析失败时给出可读错误。
            employees = json.loads(employees_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        # 本工具只接受员工数组；如果模型传入对象或文本，直接拒绝。
        if not isinstance(employees, list):
            return json.dumps({"error": "输入数据格式错误，应为数组"}, ensure_ascii=False)
        
        if len(employees) == 0:
            return json.dumps({"error": "员工列表为空"}, ensure_ascii=False)
        
        results = []
        for emp in employees:
            # 容错处理：列表中如果混入非字典值，跳过该项，避免整个批处理失败。
            if not isinstance(emp, dict):
                continue

            # 每个员工必须有 level 字段，否则无法映射基础工资。
            if "level" not in emp:
                emp_result = emp.copy()
                emp_result["error"] = "缺少 level 字段"
                results.append(emp_result)
                continue
            
            # 根据职级找到基础工资。未知职级返回 0，并被视为业务错误。
            base_salary = mock_salary_levels.get(emp["level"], 0)
            if base_salary <= 0:
                emp_result = emp.copy()
                emp_result["error"] = f"无效的职级: {emp.get('level')}"
                results.append(emp_result)
                continue
            
            # 简化版薪酬规则：
            # - 五险一金按基础工资 20% 扣除
            # - 个税按扣除五险一金后金额的 5% 计算，且不允许出现负数
            social_security = base_salary * 0.20
            tax = max(0, (base_salary - social_security) * 0.05)
            net_salary = base_salary - social_security - tax
            
            # 保留原始员工字段，再追加工资计算字段，方便导出 CSV 时完整展示。
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
        # 任何未预期异常也转为 JSON，保持工具调用协议稳定。
        return json.dumps({"error": f"计算失败: {str(e)}"}, ensure_ascii=False)

def export_payroll_csv(payroll_json: str):
    """接收工资明细 JSON，生成 CSV 文件并返回系统路径。

    真实生产系统通常会把文件上传到对象存储或生成下载链接；
    本实验写入系统临时目录，便于跨 Windows/macOS/Linux 本地运行。
    """
    try:
        # 与上一个工具相同，先检查模型传来的参数是否为空。
        if not payroll_json or not payroll_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            # 将工资 JSON 反序列化为 Python 列表，供 csv.DictWriter 写入。
            payroll_data = json.loads(payroll_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        # CSV 导出至少需要一条记录，否则无法确定表头字段。
        if not isinstance(payroll_data, list) or len(payroll_data) == 0:
            return json.dumps({"error": "工资数据为空或格式错误"}, ensure_ascii=False)
        
        # 使用 tempfile 保证学生机器上无需手动配置输出目录。
        filepath = os.path.join(tempfile.gettempdir(), "payroll_report.csv")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # 以第一条记录的键作为 CSV 表头，要求上游工具输出字段保持一致。
                writer = csv.DictWriter(f, fieldnames=payroll_data[0].keys())
                writer.writeheader()
                writer.writerows(payroll_data)
        except IOError as e:
            return json.dumps({"error": f"文件写入失败: {str(e)}"}, ensure_ascii=False)
            
        return json.dumps({"status": "success", "file_path": filepath, "record_count": len(payroll_data)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"导出失败: {str(e)}"}, ensure_ascii=False)

# ==================== SaaS 控制器 ====================
def saas_generate_payroll_api():
    """传统 SaaS 后端接口：硬编码的流水线，高度耦合。

    这个函数展示“传统软件”最典型的确定性流程：
    1. 先查询员工目录；
    2. 再计算工资；
    3. 最后导出 CSV。

    优点是稳定、可预测；缺点是流程被写死，用户无法用自然语言改变执行策略。
    """
    try:
        # 模拟传统后端接口的处理耗时，让前端更容易观察“一键流水线”的执行过程。
        time.sleep(1)
        
        # 第一步：查询员工。这里通过字符串中是否包含 error 做简化错误判断。
        emp_str = get_employee_directory()
        if "error" in emp_str:
            raise Exception(emp_str)

        # 第二步：把员工数据传入工资计算工具。
        payroll_str = calculate_payroll_and_tax(emp_str)
        if "error" in payroll_str:
            raise Exception(payroll_str)

        # 第三步：将工资结果导出为本地 CSV 文件。
        export_result = json.loads(export_payroll_csv(payroll_str))
        if "error" in export_result:
            raise Exception(export_result["error"])
        
        # Gradio Dataframe 需要二维列表，因此把 JSON 对象转换为表格行。
        payroll_data = json.loads(payroll_str)
        table_data = [[d["name"], d["level"], d["应发工资"], d["五险一金扣除"], d["实发工资"]] for d in payroll_data]
        
        return table_data, export_result.get("file_path")
    except Exception as e:
        # 前端仍然返回表格形态，避免 Gradio 输出组件因异常类型不匹配而崩溃。
        print(f"❌ SaaS 执行失败: {e}")
        return [[str(e), "", "", "", ""]], None

# ==================== MCP Schema ====================
# 这里使用 OpenAI/Ollama tool calling 的 JSON Schema 形式描述本地工具。
# 对模型来说，这相当于一份“工具菜单”：模型只能看到函数名、说明和参数结构，看不到函数内部代码。
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

# ==================== Agent 调度器 ====================
def agent_orchestrator(user_message, history, messages_state, selected_model):
    """
    Agent 的大脑调度器。接收用户指令，并根据选择的模型（qwen3.6:27b 或 qwen3.6:35b-a3b）进行推理。

    Args:
        user_message: 用户在 Gradio 文本框输入的自然语言任务。
        history: Gradio Chatbot 的可见消息历史，使用 Gradio 6 的 messages 格式。
        messages_state: 发送给模型的完整上下文，包含 system/user/assistant/tool 消息。
        selected_model: 当前选中的 Ollama 模型名称。

    Yields:
        `(history, messages_state)`，用于流式更新前端和保留后续轮次上下文。
    """
    # Gradio 初次调用时可能传入 None，这里统一转换为空列表，便于后续追加消息。
    history = history or []
    messages_state = messages_state or []

    try:
        logger.info(f"开始处理用户请求: {user_message}, 模型: {selected_model}")
        
        # system prompt 是 Agent 的全局角色和行为边界，只在新会话第一次调用时写入。
        if not messages_state:
            messages_state = [{"role": "system", "content": "你是专业的 HR 助手。请自动规划工具调用链完成计算。输出最终结果时，请用 Markdown 表格展示，并附上文件下载路径。"}]
            logger.info("初始化系统提示词")
        
        # 模型上下文记录用户真实输入；前端历史则额外加入一条“正在规划”的可见状态。
        messages_state.append({"role": "user", "content": user_message})
        history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": f"🤖 [当前引擎: {selected_model}] 正在规划任务流..."}
        ]
        yield history, messages_state
        
        # 限制最大推理轮次，避免模型不断请求工具导致无限循环。
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始迭代 {iteration}/{max_iterations}")
            
            try:
                logger.info(f"调用模型 {selected_model} 进行推理")
                # tool_choice="auto" 让模型自主判断：是直接回答，还是先调用本地工具。
                response = client.chat.completions.create(
                    model=selected_model, 
                    messages=messages_state, 
                    tools=tools_schema, 
                    tool_choice="auto"
                )
                response_msg = response.choices[0].message
                messages_state.append(response_msg)
                
                # 如果模型返回 tool_calls，说明它还不准备最终回答，而是需要执行一个或多个工具。
                if response_msg.tool_calls:
                    logger.info(f"模型请求调用 {len(response_msg.tool_calls)} 个工具")
                    
                    for tool_call in response_msg.tool_calls:
                        func_name = tool_call.function.name
                        logger.info(f"准备调用工具: {func_name}")
                        
                        try:
                            # 模型生成的 arguments 是 JSON 字符串，必须先解析为 Python 字典。
                            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            logger.info(f"工具参数: {func_args}")
                        except json.JSONDecodeError as e:
                            # 参数解析失败时不让程序崩溃，而是用空参数继续走错误分支。
                            logger.warning(f"工具参数解析失败: {e}")
                            func_args = {}
                        
                        # 先把工具名称显示到前端，让同学们观察 Agent 正在触发哪个节点。
                        history[-1]["content"] += f"\n\n> 🛠️ **触发节点**: `{func_name}`"
                        yield history, messages_state
                        
                        # 根据模型选择的函数名进行本地路由。这里就是 MCP/Tool Use 的执行边界。
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
                        
                        # 工具结果必须以 role=tool 回注，并带上 tool_call_id，模型才能把结果对应回刚才的调用。
                        messages_state.append({
                            "role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": tool_result
                        })
                        logger.info(f"工具结果已回注到上下文")
                    
                    # 继续下一轮：模型会看到刚才的工具结果，再决定是否继续调用工具或最终回答。
                    logger.info("继续下一轮迭代")
                    continue 

                else:
                    # 没有 tool_calls 表示模型认为任务已经完成，可以把自然语言总结展示给用户。
                    final_text = response_msg.content or "任务已完成，但模型没有返回文本结果。"
                    logger.info(f"模型输出最终结果: {final_text[:100]}...")
                    
                    messages_state.append({"role": "assistant", "content": final_text})
                    history[-1] = {"role": "assistant", "content": final_text}
                    yield history, messages_state
                    break 
                    
            except Exception as e:
                # 单轮推理失败时保留已经产生的前端历史，方便同学从日志定位问题。
                logger.error(f"迭代 {iteration} 执行失败: {str(e)}", exc_info=True)
                error_msg = f"❌ 迭代 {iteration} 执行失败: {str(e)}"
                history[-1]["content"] += f"\n\n{error_msg}"
                yield history, messages_state
                break
                
        if iteration >= max_iterations:
            # 达到轮次上限通常意味着模型没有形成终止条件，属于 Agent 编排中的常见风险。
            logger.warning(f"已达到最大迭代次数 {max_iterations}，任务可能未完成")
            history[-1]["content"] += "\n\n⚠️ 已达到最大迭代次数，任务可能未完成"
            yield history, messages_state
            
        logger.info(f"用户请求处理完成，总迭代次数: {iteration}")
            
    except Exception as e:
        # 外层兜底保护覆盖初始化、前端参数异常等非单轮推理错误。
        logger.error(f"Agent 调度器执行失败: {str(e)}", exc_info=True)
        error_msg = f"❌ Agent 调度器执行失败: {str(e)}"
        history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": error_msg}
        ]
        yield history, messages_state


def create_demo():
    """创建 Gradio 双轨对比 UI。

    左侧面板展示传统 SaaS 的固定流程，右侧面板展示 Agent 的动态工具编排。
    两个面板共享同一批底层业务函数，便于同学把“架构差异”与“业务能力”分开观察。
    """
    import gradio as gr

    with gr.Blocks() as demo:
        # 页面标题只负责说明实验主题，不承载业务逻辑。
        gr.Markdown("## 💸 现代软件架构实验：SaaS 巨石架构 vs Agent 动态编排")

        with gr.Row():
            with gr.Column(scale=1):
                # 控制组：点击按钮后只会执行固定的 SaaS 控制器。
                gr.Markdown("### 🏢 控制组：SaaS (硬编码)")
                gr.Markdown("> 极度高效，但极度死板。开发者提前锁死了业务流。")

                saas_btn = gr.Button("🚀 一键执行：生成工资单并下载", variant="primary")
                saas_table = gr.Dataframe(headers=["姓名", "职级", "应发", "五险一金", "实发"])
                saas_file = gr.File(label="导出的物理文件")

                # 事件绑定：按钮点击后，把后端返回值分别填入表格和文件组件。
                saas_btn.click(fn=saas_generate_payroll_api, inputs=None, outputs=[saas_table, saas_file])

            with gr.Column(scale=1):
                # 实验组：用户输入自然语言，由模型决定调用哪些工具。
                gr.Markdown("### 🤖 实验组：Agent (意图驱动)")

                # 下拉框是本实验的核心变量，用于对比 Dense 与 MoE 在工具调用中的稳定性。
                model_selector = gr.Dropdown(
                    choices=["qwen3.6:27b", "qwen3.6:35b-a3b"],
                    value="qwen3.6:35b-a3b",
                    label="🧪 核心变量：选择底层大模型架构 (Dense vs MoE)"
                )

                # messages_state 保存发给模型的完整上下文；chatbot 只保存用户可见的对话日志。
                messages_state = gr.State([])
                chatbot = gr.Chatbot(label="Agent 神经推理中枢日志", height=450)
                chat_input = gr.Textbox(
                    label="自然语言指令",
                    placeholder="输入测试用例：帮我查一下全公司的工资，算好扣税，然后给我个 CSV 文件"
                )

                # submit 触发 Agent 调度器；then 用于清空输入框，保持下一轮输入干净。
                chat_input.submit(
                    fn=agent_orchestrator,
                    inputs=[chat_input, chatbot, messages_state, model_selector],
                    outputs=[chatbot, messages_state]
                ).then(lambda: "", None, chat_input)

    return demo


demo = create_demo()


if __name__ == "__main__":
    # Gradio 6 将 theme 参数迁移到了 launch 阶段，因此这里设置主题，避免运行时迁移警告。
    demo.launch(theme="soft")
