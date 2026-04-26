# 《现代软件开发技术》上机实验手册：Harness 工程与 Agent 安全护栏

## 实验主题

本实验聚焦 Agent 系统的安全边界。前序实验已经让同学们完成了自然语言意图解析，本实验进一步讨论：当 Agent 准备执行工具调用时，工程系统如何通过 Harness 机制限制权限、校验参数、拦截危险动作，并在失败后提供可修复反馈。

## 实验目标

完成本实验后，同学们应能够：

1. 理解 Prompt 约束与代码级 Harness 约束的区别。
2. 设计工具白名单、参数校验和文件访问边界。
3. 编写一个安全文件操作 Harness，防止 Agent 越权读取或写入。
4. 实现失败反馈回注机制，让 Agent 或调用方知道为什么失败。
5. 设计跨会话状态文件，保存操作历史和安全审计记录。
6. 使用测试用例验证安全护栏是否真正生效。
7. 将安全文件操作能力整理成 Skill 契约，理解“可复用能力包”也必须受控。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：Harness 理论导入** | 理解为什么不能只依赖系统提示词 | Agent Safety, Guardrails |
| **25-55'** | **模块二：实验目录与权限边界** | 建立安全工作区和禁止访问区 | Python pathlib |
| **55-95'** | **模块三：工具白名单设计** | 只允许 Agent 调用明确授权工具 | Function Registry |
| **95-140'** | **模块四：参数校验与路径拦截** | 防止路径穿越、危险扩展名和越权写入 | Validation |
| **140-180'** | **模块五：失败反馈与审计日志** | 将失败原因结构化记录，便于自我修复 | JSON Log |
| **180-210'** | **模块六：自动化安全测试** | 用测试样例验证护栏有效性 | pytest 或 assert |
| **210-230'** | **模块七：安全文件助手 Skill 设计** | 将受控工具能力整理成可复用 Skill 契约 | SKILL.md, Capability Contract |
| **230-240'** | **模块八：总结与扩展** | 将 Harness 接入后续 Agent 工作流 | 工程复盘 |

## 实验安全注意事项

1. 所有文件读写必须限制在实验目录内。
2. 不要把本机真实用户目录、桌面、下载目录作为 Agent 可操作目录。
3. 不要让程序执行 `rm`、`del`、`format`、`sudo`、`chmod -R` 等危险命令。
4. 本实验使用模拟 Agent 请求，不需要连接真实生产系统。
5. 若扩展到真实模型调用，模型输出必须先经过 Harness 校验，不能直接执行。

## 环境准备与验证

### 1. 创建实验目录

```bash
mkdir harness_guardrail_lab
cd harness_guardrail_lab
python -m venv .venv
```

激活环境后创建目录：

```bash
mkdir workspace blocked logs
echo "课程资料：Harness 工程用于约束 Agent 行为。" > workspace/note.md
echo "禁止读取的模拟秘密" > blocked/secret.txt
```

### 2. 创建基础文件

建议文件结构：

```text
harness_guardrail_lab/
├── workspace/
│   └── note.md
├── blocked/
│   └── secret.txt
├── logs/
├── policy.py
├── tools.py
├── harness.py
├── test_harness.py
└── main.py
```

## 第一阶段：定义安全策略

### 目标

将安全规则写成代码，而不是只写在 Prompt 中。

创建 `policy.py`：

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = (BASE_DIR / "workspace").resolve()
LOG_DIR = (BASE_DIR / "logs").resolve()

ALLOWED_TOOLS = {
    "read_text",
    "write_text",
    "append_text",
    "list_files",
}

ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
MAX_WRITE_CHARS = 2000
```

### 讲解

本策略包含四类约束：

1. **目录边界**：只能访问 `workspace/`。
2. **工具边界**：只能调用白名单工具。
3. **文件类型边界**：只能处理指定扩展名。
4. **写入长度边界**：避免一次写入过大内容。

## 第二阶段：实现安全路径解析

### 目标

防止路径穿越攻击，例如 `../blocked/secret.txt`。

创建 `harness.py` 的第一部分：

```python
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from policy import ALLOWED_EXTENSIONS, ALLOWED_TOOLS, LOG_DIR, MAX_WRITE_CHARS, WORKSPACE_DIR


class HarnessError(Exception):
    pass


def resolve_workspace_path(path_str: str) -> Path:
    candidate = (WORKSPACE_DIR / path_str).resolve()
    if not str(candidate).startswith(str(WORKSPACE_DIR)):
        raise HarnessError(f"路径越界：{path_str}")
    if candidate.suffix and candidate.suffix not in ALLOWED_EXTENSIONS:
        raise HarnessError(f"不允许的文件类型：{candidate.suffix}")
    return candidate
```

### 验证

在 Python 交互环境测试：

```bash
python
```

```python
from harness import resolve_workspace_path
print(resolve_workspace_path("note.md"))
print(resolve_workspace_path("../blocked/secret.txt"))
```

第二条应抛出 `HarnessError`。

## 第三阶段：实现原子工具

### 目标

工具函数本身只做单一动作，不处理安全策略。安全策略由 Harness 统一执行。

创建 `tools.py`：

```python
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"written:{path.name}"


def append_text(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)
    return f"appended:{path.name}"


def list_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(p.name for p in path.iterdir())
```

## 第四阶段：工具白名单与参数校验

继续编辑 `harness.py`：

```python
import tools


def audit(event: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event["time"] = datetime.now().isoformat(timespec="seconds")
    log_file = LOG_DIR / "audit.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def validate_request(request: dict[str, Any]) -> None:
    tool_name = request.get("tool")
    if tool_name not in ALLOWED_TOOLS:
        raise HarnessError(f"工具未授权：{tool_name}")

    if "path" not in request:
        raise HarnessError("缺少 path 参数")

    content = request.get("content", "")
    if content and len(content) > MAX_WRITE_CHARS:
        raise HarnessError("写入内容过长")


def run_tool(request: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_request(request)
        tool_name = request["tool"]
        path = resolve_workspace_path(request["path"])
        content = request.get("content", "")

        if tool_name == "read_text":
            result = tools.read_text(path)
        elif tool_name == "write_text":
            result = tools.write_text(path, content)
        elif tool_name == "append_text":
            result = tools.append_text(path, content)
        elif tool_name == "list_files":
            result = tools.list_files(path)
        else:
            raise HarnessError(f"工具未实现：{tool_name}")

        response = {"ok": True, "result": result, "error": None}
        audit({"request": request, "response": response})
        return response

    except Exception as e:
        response = {"ok": False, "result": None, "error": str(e)}
        audit({"request": request, "response": response})
        return response
```

### 讲解

`run_tool` 是 Harness 的核心入口。真实 Agent 系统中，大模型输出的工具调用请求必须先经过类似函数，而不是直接调用底层工具。

## 第五阶段：模拟 Agent 请求

创建 `main.py`：

```python
from harness import run_tool


REQUESTS = [
    {"tool": "read_text", "path": "note.md"},
    {"tool": "write_text", "path": "summary.md", "content": "Harness 可以限制 Agent 的行为。"},
    {"tool": "read_text", "path": "../blocked/secret.txt"},
    {"tool": "delete_file", "path": "note.md"},
    {"tool": "write_text", "path": "run.sh", "content": "rm -rf /"},
]

for request in REQUESTS:
    print("=" * 80)
    print("request:", request)
    print("response:", run_tool(request))
```

运行：

```bash
python main.py
```

### 预期现象

1. 读取 `note.md` 成功。
2. 写入 `summary.md` 成功。
3. 读取 `../blocked/secret.txt` 被拦截。
4. 调用 `delete_file` 被拦截。
5. 写入 `.sh` 文件被拦截。

## 第六阶段：安全测试

### 目标

用测试证明安全护栏确实生效。可以使用 `pytest`，也可以使用普通 `assert`。

创建 `test_harness.py`：

```python
from harness import run_tool


def test_allowed_read():
    result = run_tool({"tool": "read_text", "path": "note.md"})
    assert result["ok"] is True


def test_block_path_traversal():
    result = run_tool({"tool": "read_text", "path": "../blocked/secret.txt"})
    assert result["ok"] is False
    assert "路径越界" in result["error"]


def test_block_unknown_tool():
    result = run_tool({"tool": "delete_file", "path": "note.md"})
    assert result["ok"] is False
    assert "工具未授权" in result["error"]


def test_block_extension():
    result = run_tool({"tool": "write_text", "path": "run.sh", "content": "echo hi"})
    assert result["ok"] is False
    assert "不允许的文件类型" in result["error"]
```

安装并运行：

```bash
pip install pytest
pytest -q
```

如果不想安装 `pytest`，可以直接在 `main.py` 中观察拦截结果。

## 第七阶段：审计日志观察

查看日志：

```bash
cat logs/audit.jsonl
```

同学们应观察每条记录是否包含：

1. 原始请求。
2. 执行结果。
3. 错误原因。
4. 时间戳。

审计日志的价值在于：当 Agent 出错时，系统可以把错误原因重新交给模型，让模型调整下一步动作。

## 第八阶段：扩展为反馈回注

在真实 Agent 中，失败反馈可以这样组织：

```python
def build_feedback(response: dict) -> str:
    if response["ok"]:
        return f"工具执行成功，结果为：{response['result']}"
    return f"工具执行失败，原因：{response['error']}。请修改工具名或参数后重试。"
```

同学们可以把 `build_feedback` 的输出作为下一轮模型上下文的一部分，实现“失败 -> 解释 -> 修正 -> 再执行”的闭环。

## 第九阶段：安全文件助手 Skill 设计

### 目标

Skill 不是“给 Agent 开后门”，而是把一组能力、使用边界和操作流程封装成可复用说明。本阶段将前面实现的安全文件操作 Harness 整理为一个 Skill 契约，让后续 Agent 或同学自己都能清楚知道：这个能力可以做什么、不能做什么、失败时如何处理。

### 目录结构

在实验目录中创建：

```text
safe_file_skill/
└── SKILL.md
```

### 示例 `SKILL.md`

```markdown
---
name: safe-file-assistant
description: 在实验 workspace 目录内安全读取、写入、追加和列出教学文件。仅用于课程实验中的受控文件操作；当请求涉及路径越界、危险扩展名、删除文件或系统命令时必须拒绝。
---

# Safe File Assistant

## 能力范围

- 读取 `workspace/` 内的 `.txt`、`.md`、`.json`、`.csv` 文件。
- 写入或追加不超过 2000 字符的教学文本。
- 列出 `workspace/` 内文件。

## 禁止行为

- 不读取 `workspace/` 之外的文件。
- 不执行系统命令。
- 不删除文件。
- 不处理 `.sh`、`.exe`、`.bat` 等危险扩展名。

## 调用流程

1. 将用户请求转换为工具请求字典。
2. 交给 Harness 的 `run_tool(request)`。
3. 如果返回 `ok=false`，把 `error` 作为反馈说明，不绕过 Harness。
```

### 观察要点

同学们需要理解三层边界：

1. **Skill 文档边界**：告诉 Agent 能力范围。
2. **MCP/工具接口边界**：规定工具名和参数格式。
3. **Harness 执行边界**：真正负责拦截越权行为。

其中最硬的边界是 Harness。Skill 写得再清楚，也不能替代代码级校验。

## 故障排除 FAQ

### Q1: 为什么 Prompt 里写“不要越权”还不够？

**A:** Prompt 是软约束，模型可能忽略或误解。Harness 是代码级硬约束，只要请求不符合规则，就不会执行。

### Q2: 路径校验为什么要用 `.resolve()`？

**A:** `.resolve()` 可以把 `../`、符号链接等路径归一化，便于判断真实访问位置是否仍在工作区内。

### Q3: 为什么工具函数不直接写安全判断？

**A:** 将安全策略集中放在 Harness 层，可以避免每个工具重复实现安全判断，也便于统一审计。

### Q4: 是否应该允许 Agent 删除文件？

**A:** 初学阶段不建议开放删除工具。即使要开放，也应先实现回收站、二次确认、路径白名单和审计日志。

### Q5: 审计日志是否需要保存模型原始输出？

**A:** 建议保存，但要注意脱敏。日志中不应记录真实密码、Token 或个人隐私信息。

## 参考资源

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python pathlib: https://docs.python.org/3/library/pathlib.html
- pytest: https://docs.pytest.org/
- OpenAI Safety Best Practices: https://platform.openai.com/docs/guides/safety-best-practices
