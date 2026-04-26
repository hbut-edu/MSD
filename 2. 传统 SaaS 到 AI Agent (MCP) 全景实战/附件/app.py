import json
import os
import time
import csv
import tempfile
import logging
from datetime import datetime
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ==================== 日志配置 ====================
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
mock_employees = [
    {"id": "E01", "name": "张三", "level": "L1"},
    {"id": "E02", "name": "李四", "level": "L2"},
    {"id": "E03", "name": "王五", "level": "L3"}
]

mock_salary_levels = {"L1": 10000, "L2": 20000, "L3": 35000}

# ==================== 工具函数 ====================
def get_employee_directory():
    """返回全公司员工的花名册 JSON"""
    try:
        if not mock_employees:
            return json.dumps({"error": "员工数据为空"}, ensure_ascii=False)
        return json.dumps(mock_employees, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

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

# ==================== SaaS 控制器 ====================
def saas_generate_payroll_api():
    """传统 SaaS 后端接口：硬编码的流水线，高度耦合"""
    try:
        time.sleep(1)
        
        emp_str = get_employee_directory()
        if "error" in emp_str:
            raise Exception(emp_str)
            
        payroll_str = calculate_payroll_and_tax(emp_str)
        if "error" in payroll_str:
            raise Exception(payroll_str)
            
        export_result = json.loads(export_payroll_csv(payroll_str))
        if "error" in export_result:
            raise Exception(export_result["error"])
        
        payroll_data = json.loads(payroll_str)
        table_data = [[d["name"], d["level"], d["应发工资"], d["五险一金扣除"], d["实发工资"]] for d in payroll_data]
        
        return table_data, export_result.get("file_path")
    except Exception as e:
        print(f"❌ SaaS 执行失败: {e}")
        return [[str(e), "", "", "", ""]], None

# ==================== MCP Schema ====================
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
    Agent 的大脑调度器。接收用户指令，并根据选择的模型（qwen3.5:9b 或 qwen3.5:35b-a3b）进行推理。
    """
    try:
        logger.info(f"开始处理用户请求: {user_message}, 模型: {selected_model}")
        
        if not messages_state:
            messages_state = [{"role": "system", "content": "你是专业的 HR 助手。请自动规划工具调用链完成计算。输出最终结果时，请用 Markdown 表格展示，并附上文件下载路径。"}]
            logger.info("初始化系统提示词")
        
        messages_state.append({"role": "user", "content": user_message})
        history.append((user_message, f"🤖 [当前引擎: {selected_model}] 正在规划任务流..."))
        yield history, messages_state
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始迭代 {iteration}/{max_iterations}")
            
            try:
                logger.info(f"调用模型 {selected_model} 进行推理")
                response = client.chat.completions.create(
                    model=selected_model, 
                    messages=messages_state, 
                    tools=tools_schema, 
                    tool_choice="auto"
                )
                response_msg = response.choices[0].message
                messages_state.append(response_msg)
                
                if response_msg.tool_calls:
                    logger.info(f"模型请求调用 {len(response_msg.tool_calls)} 个工具")
                    
                    for tool_call in response_msg.tool_calls:
                        func_name = tool_call.function.name
                        logger.info(f"准备调用工具: {func_name}")
                        
                        try:
                            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            logger.info(f"工具参数: {func_args}")
                        except json.JSONDecodeError as e:
                            logger.warning(f"工具参数解析失败: {e}")
                            func_args = {}
                        
                        history[-1] = (user_message, history[-1][1] + f"\n\n> 🛠️ **触发节点**: `{func_name}`")
                        yield history, messages_state
                        
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
                        
                        messages_state.append({
                            "role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": tool_result
                        })
                        logger.info(f"工具结果已回注到上下文")
                    
                    logger.info("继续下一轮迭代")
                    continue 

                else:
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
