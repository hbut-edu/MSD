# 《现代软件开发技术》上机实验手册：多 Agent 状态机协作与工作流编排

## 实验主题

本实验从单 Agent 进入多 Agent 协作。系统不再让一个模型一次性完成全部任务，而是将任务拆分为“程序员 Agent”“审查员 Agent”“测试员 Agent”等角色，通过状态机控制流转、重试和终止条件，形成可解释的轻量级工作流。

## 实验目标

完成本实验后，同学们应能够：

1. 理解多 Agent 协作与普通多轮对话的区别。
2. 使用状态机描述工作流节点、边和终止条件。
3. 编写一个不依赖复杂框架的内存级多 Agent 协作原型。
4. 实现“生成 -> 审查 -> 修改 -> 通过/失败”的有限重试闭环。
5. 记录每一步状态转移日志，分析多 Agent 系统的可观测性。
6. 理解为什么多 Agent 系统必须有最大重试次数和失败出口。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：多 Agent 理论导入** | 理解角色拆分与状态流转 | Agent Workflow |
| **25-55'** | **模块二：任务与状态定义** | 定义节点、状态、事件、终止条件 | State Machine |
| **55-95'** | **模块三：程序员 Agent** | 生成候选代码或方案 | Python Function |
| **95-135'** | **模块四：审查员 Agent** | 检查候选结果并给出修改意见 | Rule-based Review |
| **135-180'** | **模块五：状态机调度器** | 实现有限重试和流转日志 | Workflow Engine |
| **180-220'** | **模块六：测试员与扩展节点** | 加入测试节点，观察复杂度变化 | Test Agent |
| **220-240'** | **模块七：总结与扩展** | 对比 LangGraph 等框架思想 | 工程复盘 |

## 实验安全注意事项

1. 本实验默认使用规则函数模拟 Agent，不需要真实模型。
2. 如果接入大模型，模型生成的代码不要自动执行，必须经过审查和测试。
3. 工作流必须设置最大重试次数，避免无限循环。
4. 日志中不要记录真实密钥、隐私数据或不可公开代码。

## 环境准备与验证

```bash
mkdir multi_agent_state_lab
cd multi_agent_state_lab
python -m venv .venv
```

建议文件结构：

```text
multi_agent_state_lab/
├── state.py
├── agents.py
├── workflow.py
├── main.py
└── logs/
```

本实验只使用 Python 标准库。

## 第一阶段：定义任务状态

创建 `state.py`：

```python
from dataclasses import dataclass, field


@dataclass
class WorkflowState:
    requirement: str
    draft: str = ""
    review_passed: bool = False
    review_feedback: str = ""
    tests_passed: bool = False
    attempts: int = 0
    max_attempts: int = 3
    history: list[dict] = field(default_factory=list)

    def log(self, node: str, message: str) -> None:
        self.history.append({
            "step": len(self.history) + 1,
            "node": node,
            "message": message,
        })
```

### 讲解

状态对象是多 Agent 协作的共享黑板。每个节点只读写必要字段，调度器根据字段决定下一步。

## 第二阶段：实现程序员 Agent

创建 `agents.py` 的第一部分：

```python
from state import WorkflowState


def programmer_agent(state: WorkflowState) -> WorkflowState:
    state.attempts += 1
    if state.attempts == 1:
        state.draft = "def add(a, b):\n    return a - b\n"
    else:
        state.draft = "def add(a, b):\n    return a + b\n"
    state.log("programmer", f"生成第 {state.attempts} 版代码")
    return state
```

本示例故意让第一版代码写错，便于观察审查回路。

## 第三阶段：实现审查员 Agent

继续编辑 `agents.py`：

```python
def reviewer_agent(state: WorkflowState) -> WorkflowState:
    if "return a + b" in state.draft:
        state.review_passed = True
        state.review_feedback = "代码逻辑符合加法需求。"
    else:
        state.review_passed = False
        state.review_feedback = "当前代码使用了减法，不符合 add 函数需求。"
    state.log("reviewer", state.review_feedback)
    return state
```

### 观察要点

审查员 Agent 不直接修改代码，只给出反馈。这种角色边界有助于降低系统混乱度。

## 第四阶段：实现测试员 Agent

继续编辑 `agents.py`：

```python
def tester_agent(state: WorkflowState) -> WorkflowState:
    namespace = {}
    try:
        exec(state.draft, namespace)
        result = namespace["add"](2, 3)
        state.tests_passed = result == 5
        message = "测试通过" if state.tests_passed else f"测试失败：add(2, 3)={result}"
    except Exception as e:
        state.tests_passed = False
        message = f"测试异常：{e}"
    state.log("tester", message)
    return state
```

### 安全提醒

这里使用 `exec` 是为了课堂演示，且执行的是本实验中可控字符串。真实系统中不要直接执行模型生成代码，应放入沙箱或容器。

## 第五阶段：状态机调度器

创建 `workflow.py`：

```python
from agents import programmer_agent, reviewer_agent, tester_agent
from state import WorkflowState


def run_workflow(requirement: str) -> WorkflowState:
    state = WorkflowState(requirement=requirement)
    state.log("start", requirement)

    while state.attempts < state.max_attempts:
        state = programmer_agent(state)
        state = reviewer_agent(state)

        if not state.review_passed:
            state.log("router", "审查未通过，返回程序员节点")
            continue

        state = tester_agent(state)
        if state.tests_passed:
            state.log("router", "测试通过，工作流结束")
            return state

        state.log("router", "测试未通过，返回程序员节点")

    state.log("router", "达到最大重试次数，工作流失败")
    return state
```

## 第六阶段：运行与观察日志

创建 `main.py`：

```python
import json

from workflow import run_workflow


state = run_workflow("实现一个 add(a, b) 函数，返回两个数字之和。")

print("final draft:")
print(state.draft)
print("review_passed:", state.review_passed)
print("tests_passed:", state.tests_passed)
print("=" * 80)
print(json.dumps(state.history, ensure_ascii=False, indent=2))
```

运行：

```bash
python main.py
```

预期日志中至少出现一次：

```text
程序员生成错误代码 -> 审查员驳回 -> 程序员修正 -> 审查通过 -> 测试通过
```

## 第七阶段：工作流图理解

本实验的状态机可表示为：

```text
START
  |
programmer
  |
reviewer --未通过--> programmer
  |
通过
  |
tester --未通过--> programmer
  |
通过
  |
END
```

关键约束：

1. 每个节点职责单一。
2. 路由逻辑集中在调度器。
3. 工作流必须有最大重试次数。
4. 每一步都写入 `history`。

## 第八阶段：扩展练习

同学们可以选择一个方向扩展：

1. 增加 `security_reviewer_agent`，检查代码是否包含危险函数。
2. 增加 `doc_agent`，为通过测试的代码生成说明文档。
3. 将 `history` 写入 `logs/workflow.json`。
4. 将程序员 Agent 替换为真实大模型调用。
5. 使用 LangGraph 重写相同工作流，对比框架版本与手写版本差异。

## 故障排除 FAQ

### Q1: 多 Agent 是否一定比单 Agent 好？

**A:** 不一定。多 Agent 增加了可解释性和角色分工，但也会增加延迟、成本和调度复杂度。

### Q2: 为什么需要最大重试次数？

**A:** 如果没有最大重试次数，程序员和审查员可能无限循环，导致系统卡死或 API 成本失控。

### Q3: 审查员 Agent 可以直接改代码吗？

**A:** 可以，但初学阶段建议保持角色边界清晰。审查员负责反馈，程序员负责修改。

### Q4: 为什么要保存 history？

**A:** history 是 AgentOps 观测的基础，可以帮助定位系统在哪个节点失败。

### Q5: 可以使用 LangGraph 吗？

**A:** 可以作为扩展。本实验先手写状态机，是为了让同学们理解框架背后的基本思想。

## 参考资源

- LangGraph: https://langchain-ai.github.io/langgraph/
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- State Machine: https://en.wikipedia.org/wiki/Finite-state_machine
