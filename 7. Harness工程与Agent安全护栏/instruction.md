# 7. Harness 工程与 Agent 安全护栏 - 实验手册

## 实验主题

本实验聚焦 Agent 系统的安全边界。前序实验已经让同学们完成了自然语言意图解析，本实验进一步讨论：当 Agent 准备执行工具调用时，工程系统如何通过 Harness 机制限制权限、校验参数、拦截危险动作，并在失败后提供可修复反馈。

## 核心概念与系统定位

在进入代码实现之前，先从一个朴素问题开始：如果我们希望 Agent 帮忙读写文件，它怎么知道自己“可以读哪些文件、可以写哪些文件、不能碰哪些文件”？人类使用软件时会看菜单、按钮和说明；Agent 使用能力时，也需要某种面向它的能力说明。

在 Agent 工程中，这类“能力说明书”常被组织成 **Skill**。同学们现在不需要把 Skill 理解成复杂框架，只要先把它看成一份写给 Agent 看的说明文档：它告诉 Agent 系统有哪些可用能力、这些能力适合解决什么问题、输入输出大致是什么、哪些行为不应该尝试。例如，一个安全文件助手 Skill 可以说明“可以读取 `workspace/` 中的教学文件、可以追加课堂笔记、不能读取工作区之外的文件”。本实验会第一次正式接触这个概念，并用一个最小 `SKILL.md` 文件帮助同学们建立直觉。

不过，仅有说明文档是不够的。Skill 能告诉 Agent “应该怎么做”，却不能保证 Agent 一定照做；它也不会自动阻止错误参数、越权路径或危险文件类型。因此，在真正执行工具之前，还需要一层代码级检查。

**Harness** 是包裹在工具执行外层的工程控制层。它接收 Agent 生成的工具调用请求，然后在真正执行函数之前完成检查：工具名是否在白名单中、路径是否越界、参数类型是否正确、写入内容是否过长、文件扩展名是否允许。只有通过 Harness 校验的请求，才会进入底层工具函数；被拦截的请求应返回结构化错误，并写入审计日志。

为了便于记忆，可以先把两者的关系记成一句话：**Skill 负责说明能力，Harness 负责守住边界**。

在一个受控 Agent 系统中，可以把各部分定位为：

| 组件 | 系统定位 | 本实验中的例子 |
| :-- | :-- | :-- |
| 用户请求 | 表达自然语言意图 | “帮我读取课堂笔记并追加总结” |
| Skill | 面向 Agent 的能力说明 | `safe_file_skill/SKILL.md` |
| Agent | 根据意图和能力说明生成工具请求 | `{"tool": "read_text", "path": "note.md"}` |
| Harness | 校验请求并决定是否放行 | `run_tool(request)` |
| Tool | 执行单一、明确的底层动作 | `read_text`、`write_text`、`append_text` |
| 审计与反馈 | 记录结果并帮助下一步修正 | `logs/audit.jsonl`、失败原因回注 |

本实验后续所有代码都围绕这条链路展开：

```text
Skill 先告诉 Agent 有哪些能力
    ↓
Agent 生成工具调用请求
    ↓
Harness 判断请求是否安全、合规、可执行
    ↓
Tool 只执行被放行的原子操作
    ↓
日志和反馈记录执行结果
```

因此，本实验的重点不是“让 Agent 能做更多事”，而是让同学们掌握：当能力被暴露给 Agent 之后，工程系统如何用 Harness 把能力关进可验证、可审计、可恢复的边界之内。

## 前后课程关系与学习路线

前序 Agent 与 MCP 实验已经让同学们看到：模型可以根据自然语言意图选择工具，并把工具结果再交回模型继续推理。但只要系统允许 Agent 调用工具，就会出现一个新的工程问题：**模型产生的工具请求并不天然可信**。模型可能理解错意图、填错参数，也可能被提示词注入诱导去访问不该访问的路径。

本实验正好位于“能调用工具”和“可靠运行 Agent 系统”之间。它承接前序实验中的工具调用思想，补上安全执行层；后续 RAG、异步并发、多 Agent 编排和 API 化交付实验中，只要涉及外部资源、文件、网络、数据库或系统命令，都应复用本实验的基本判断：

1. 先定义能力说明，让 Agent 知道可以做什么。
2. 再定义请求协议，让 Agent 的意图变成可检查的数据结构。
3. 最后用 Harness 做代码级校验，只放行安全、合规、可审计的请求。

因此，本实验的学习路线是：

```text
从能力说明认识 Skill
    -> 定义工具请求协议
    -> 识别越权风险
    -> 编写 Harness 校验层
    -> 执行原子工具
    -> 记录审计日志
    -> 通过测试验证护栏
    -> 回头完善 Skill 契约
```

## 实验目标

完成本实验后，同学们应能够：

1. 初步理解 Skill、Tool 与 Harness 在 Agent 系统中的职责边界。
2. 理解 Prompt 约束与代码级 Harness 约束的区别。
3. 设计工具白名单、参数校验和文件访问边界。
4. 编写一个安全文件操作 Harness，防止 Agent 越权读取或写入。
5. 实现失败反馈回注机制，让 Agent 或调用方知道为什么失败。
6. 使用审计日志保存跨会话操作历史和安全记录。
7. 使用测试用例验证安全护栏是否真正生效。
8. 将安全文件操作能力整理成 Skill 契约，理解“可复用能力包”也必须受控。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-20'** | **模块一：从能力说明认识 Skill** | 理解 Agent 如何“看见”可用能力，以及为什么能力入口必须受控 | Skill, Tool, Capability Contract |
| **20-45'** | **模块二：Harness 理论导入** | 理解为什么不能只依赖系统提示词 | Agent Safety, Guardrails |
| **45-70'** | **模块三：实验目录与权限边界** | 建立安全工作区和禁止访问区 | Python pathlib |
| **70-105'** | **模块四：工具白名单设计** | 只允许 Agent 调用明确授权工具 | Function Registry |
| **105-150'** | **模块五：参数校验与路径拦截** | 防止路径穿越、危险扩展名和越权写入 | Validation |
| **150-185'** | **模块六：失败反馈与审计日志** | 将失败原因结构化记录，便于自我修复 | JSON Log |
| **185-215'** | **模块七：自动化安全测试** | 用测试样例验证护栏有效性 | pytest 或 assert |
| **215-230'** | **模块八：完善安全文件助手 Skill 契约** | 将受控工具能力整理成可复用 Skill 契约 | SKILL.md, Capability Contract |
| **230-240'** | **模块九：总结与扩展** | 将 Harness 接入后续 Agent 工作流 | 工程复盘 |

## 实验安全注意事项

1. 所有文件读写必须限制在实验目录内。
2. 不要把本机真实用户目录、桌面、下载目录作为 Agent 可操作目录。
3. 不要让程序执行 `rm`、`del`、`format`、`sudo`、`chmod -R` 等危险命令。
4. 本实验使用模拟 Agent 请求，不需要连接真实生产系统。
5. `blocked/secret.txt` 是专门用于验证越权拦截的模拟文件，实验目标是证明它不能被读取。
6. 若扩展到真实模型调用，模型输出必须先经过 Harness 校验，不能直接执行。

## 环境准备与验证

### 1. 创建实验目录

下面这段命令用于创建本实验的独立目录和 Python 虚拟环境，避免污染同学电脑上的其他课程项目：

```bash
# 创建实验根目录，后续所有文件都放在这里。
mkdir harness_guardrail_lab

# 进入实验目录，保证后续相对路径都以该目录为基准。
cd harness_guardrail_lab

# 创建 Python 虚拟环境，用于隔离 pytest 等实验依赖。
python -m venv .venv
```

激活环境并检查 Python 版本：

```bash
# macOS / Linux：激活虚拟环境。
source .venv/bin/activate

# Windows PowerShell：如果使用 Windows，可以执行下面这一行。
# .venv\Scripts\Activate.ps1

# 检查 Python 版本，建议为 3.10 或更高。
python --version

# 更新 pip，减少后续安装 pytest 时出现旧版本兼容问题的概率。
python -m pip install --upgrade pip
```

建议使用 Python 3.10 或以上版本。激活环境后创建目录：

```bash
# workspace 是允许 Agent 操作的目录，blocked 是专门用于验证越权拦截的目录。
# logs 保存审计日志，safe_file_skill 保存能力说明文档。
mkdir workspace blocked logs safe_file_skill

# 创建一份允许读取的课堂笔记，后续 read_text 工具会读取它。
echo "课程资料：Harness 工程用于约束 Agent 行为。" > workspace/note.md

# 创建一份模拟秘密文件，后续测试应证明 Agent 不能越权读取它。
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
├── safe_file_skill/
│   └── SKILL.md
├── policy.py
├── tools.py
├── harness.py
├── test_harness.py
└── main.py
```

## 第零阶段：从能力说明认识 Skill

### 目标

在正式编写 Harness 之前，先理解 Agent 为什么会调用工具。此处第一次引入 Skill：它可以看作一份“能力说明书”，告诉 Agent 某个能力可以做什么、适合在什么场景使用、调用时应遵守什么边界。但 Skill 本身不是权限系统，它只是软性的能力契约；真正决定请求能不能执行的，是后续代码级 Harness。

本实验的安全链路可以理解为：

```text
用户自然语言意图
    ↓
Skill / Tool 说明让 Agent 看见可用能力
    ↓
Agent 生成结构化工具请求
    ↓
Harness 校验工具名、参数、路径和内容边界
    ↓
原子工具执行真实文件操作
    ↓
审计日志与失败反馈回注
```

因此，本实验不是先写一个“万能文件助手”，再事后提醒它小心；而是从一开始就要求同学把能力入口和执行边界分开设计。

### 创建最小 Skill 草稿

先创建 `safe_file_skill/SKILL.md`，写入一个最小能力草稿。此时它只负责说明能力意图，后续阶段实现 Harness 后，再回头补充完整调用流程和禁止行为。

```markdown
---
name: safe-file-assistant
description: 在实验 workspace 目录内安全读取、写入、追加和列出教学文件。所有请求都必须经过 Harness 校验后才能执行。
---

# Safe File Assistant

## 能力范围

- 读取实验 `workspace/` 目录中的教学文件。
- 写入或追加课堂练习文本。
- 列出实验工作区文件。

## 执行原则

- Skill 只描述能力，不直接授予权限。
- Agent 只能生成工具请求，不能绕过 Harness 直接操作文件。
- Harness 返回失败时，应把失败原因作为反馈，而不是尝试绕过限制。
```

### 观察要点

同学们需要先建立一个判断：**Agent 调用工具之前，必须先知道有哪些能力；而一旦能力被暴露，就必须有工程系统负责限制它。**

可以先这样理解：Skill 像能力说明，Tool 像可执行动作，Harness 像安全闸门。后续各阶段会逐步实现这道闸门。

### 工具请求协议

真实模型产生的工具调用可能来自 MCP、OpenAI 兼容 tool calling、函数调用封装，或框架内部的 Tool 对象。为了降低首次学习成本，本实验先把它们统一简化为一个 Python 字典：

```python
# 读取类请求：Agent 只需要说明工具名和相对路径。
{"tool": "read_text", "path": "note.md"}

# 写入类请求：除了工具名和路径，还必须携带 content 字段。
{"tool": "write_text", "path": "summary.md", "content": "课堂总结"}
```

这个字典就是 Agent 意图进入工程系统前的“中间表示”。它至少包含：

| 字段 | 类型 | 是否必需 | 含义 |
| :-- | :-- | :-- | :-- |
| `tool` | `str` | 是 | Agent 想调用的工具名 |
| `path` | `str` | 是 | Agent 想操作的相对路径 |
| `content` | `str` | 写入类工具需要 | 写入或追加的文本内容 |

后续 Harness 的任务，就是把这个看似简单的字典检查清楚：它是不是字典、工具名是否授权、路径是否仍在工作区、内容是否符合长度和类型要求。不要因为数据结构简单，就默认它可信。

### 本实验的威胁模型

本实验不讨论所有安全问题，而是聚焦 Agent 工具调用中最常见、最适合课堂验证的几类风险：

| 风险类型 | 危险请求示例 | Harness 期望行为 |
| :-- | :-- | :-- |
| 路径穿越 | `{"tool": "read_text", "path": "../blocked/secret.txt"}` | 拦截并返回路径越界 |
| 未授权工具 | `{"tool": "delete_file", "path": "note.md"}` | 拦截并返回工具未授权 |
| 危险文件类型 | `{"tool": "write_text", "path": "run.sh", "content": "rm -rf /"}` | 拦截并返回文件类型不允许 |
| 参数类型错误 | `{"tool": "write_text", "path": "a.md", "content": ["bad"]}` | 拦截并返回参数类型错误 |
| 写入内容过长 | `{"tool": "append_text", "path": "note.md", "content": "..."}` | 拦截并返回写入内容过长 |
| 读工具夹带写参数 | `{"tool": "read_text", "path": "note.md", "content": "overwrite"}` | 拦截并返回参数不匹配 |

安全 Harness 的默认原则是 **fail closed**：只要请求无法被明确证明安全，就拒绝执行，并给出可读的失败原因。

## 第一阶段：定义安全策略

### 目标

将安全规则写成代码，而不是只写在 Prompt 中。

创建 `policy.py`：

```python
# pathlib 用于以跨平台方式处理目录和文件路径。
from pathlib import Path

# BASE_DIR 表示当前实验项目根目录，也就是 policy.py 所在目录。
BASE_DIR = Path(__file__).resolve().parent

# WORKSPACE_DIR 是 Agent 被允许访问的唯一工作区。
WORKSPACE_DIR = (BASE_DIR / "workspace").resolve()

# LOG_DIR 和 AUDIT_LOG 统一定义审计日志位置，避免日志路径散落在各个文件中。
LOG_DIR = (BASE_DIR / "logs").resolve()
AUDIT_LOG = LOG_DIR / "audit.jsonl"

# ALLOWED_TOOLS 是工具白名单；不在列表中的工具一律拒绝。
ALLOWED_TOOLS = {
    "read_text",
    "write_text",
    "append_text",
    "list_files",
}

# ALLOWED_EXTENSIONS 限制 Agent 可以读写的文件类型。
ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}

# MAX_WRITE_CHARS 限制单次写入长度，防止模型一次性写入过大内容。
MAX_WRITE_CHARS = 2000
```

### 讲解

本策略包含四类约束：

1. **目录边界**：只能访问 `workspace/`。
2. **工具边界**：只能调用白名单工具。
3. **文件类型边界**：只能处理指定扩展名。
4. **写入长度边界**：避免一次写入过大内容。

这里使用的是白名单思路，而不是黑名单思路。黑名单只能列出“已知危险项”，很容易漏掉新的危险工具或新文件类型；白名单则只允许课堂实验明确需要的能力，其他请求默认拒绝。Agent 工程中，越靠近真实执行层，越应该采用这种保守策略。

## 第二阶段：实现安全路径解析

### 目标

防止路径穿越攻击，例如 `../blocked/secret.txt`。

创建 `harness.py` 的第一部分：

```python
# json 用于后续写入 JSON Lines 审计日志。
import json

# datetime 用于给每条审计记录追加时间戳。
from datetime import datetime

# Path 用于处理解析后的安全路径。
from pathlib import Path

# Any 用于标注工具请求和审计事件中的通用字典值。
from typing import Any

# 导入统一安全策略，Harness 只读取策略，不在函数中散落魔法常量。
from policy import ALLOWED_EXTENSIONS, ALLOWED_TOOLS, AUDIT_LOG, LOG_DIR, MAX_WRITE_CHARS, WORKSPACE_DIR


class HarnessError(Exception):
    """Harness 校验失败时抛出的自定义异常。

    使用自定义异常可以把安全拦截和普通 Python 错误区分开，
    也方便后续统一转换成结构化 error 返回给 Agent。
    """

    pass


def resolve_workspace_path(path_str: str) -> Path:
    """将 Agent 提供的相对路径解析为 workspace 内的安全绝对路径。"""

    # 第一步：把用户传入路径挂到 WORKSPACE_DIR 下，再解析为真实绝对路径。
    candidate = (WORKSPACE_DIR / path_str).resolve()

    # 第二步：确认真实路径仍然位于 WORKSPACE_DIR 内，防止 ../ 路径穿越。
    try:
        candidate.relative_to(WORKSPACE_DIR)
    except ValueError:
        raise HarnessError(f"路径越界：{path_str}")

    # 第三步：如果路径带扩展名，则扩展名必须出现在白名单中。
    if candidate.suffix and candidate.suffix not in ALLOWED_EXTENSIONS:
        raise HarnessError(f"不允许的文件类型：{candidate.suffix}")

    # 所有检查通过后，才把 Path 对象交给底层工具函数。
    return candidate
```

这段代码有两个关键点：

1. `(WORKSPACE_DIR / path_str).resolve()` 会先把用户传入的相对路径归一化，例如把 `../blocked/secret.txt` 转成真实绝对路径。
2. `candidate.relative_to(WORKSPACE_DIR)` 用来判断归一化后的真实路径是否仍在工作区内。如果不在，说明请求已经越过了 Harness 允许的边界。

不要只用字符串包含或字符串前缀判断路径。路径安全判断必须基于解析后的真实路径，否则容易被同名前缀目录、`../` 或符号链接干扰。

### 验证

在 Python 交互环境测试：

```bash
# 启动 Python 交互环境，用于手动调用 resolve_workspace_path。
python
```

```python
# 导入待验证的路径解析函数。
from harness import resolve_workspace_path

# 合法路径：note.md 位于 workspace 目录内，应返回解析后的绝对路径。
print(resolve_workspace_path("note.md"))

# 越权路径：../blocked/secret.txt 位于 workspace 外，应抛出 HarnessError。
print(resolve_workspace_path("../blocked/secret.txt"))
```

第二条应抛出 `HarnessError`。

## 第三阶段：实现原子工具

### 目标

工具函数本身只做单一动作，不处理安全策略。安全策略由 Harness 统一执行。

创建 `tools.py`：

```python
# Path 是工具层接收的路径类型；此处不再接收原始字符串。
from pathlib import Path


def read_text(path: Path) -> str:
    """读取文本文件内容。

    该函数假设路径已经由 Harness 校验过，因此只负责文件读取。
    """

    # 使用 UTF-8 读取，保证中文课堂资料可以正常显示。
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> str:
    """覆盖写入文本内容，并返回简短执行结果。"""

    # 如果用户写入子目录中的文件，先确保父目录存在。
    path.parent.mkdir(parents=True, exist_ok=True)

    # 覆盖写入内容；是否允许覆盖由上层 Harness 和业务策略决定。
    path.write_text(content, encoding="utf-8")

    # 返回简短状态，方便 Agent 或日志知道写入了哪个文件。
    return f"written:{path.name}"


def append_text(path: Path, content: str) -> str:
    """在文件末尾追加文本内容。"""

    # 追加前同样确保父目录存在。
    path.parent.mkdir(parents=True, exist_ok=True)

    # 使用追加模式打开文件，不覆盖已有课堂笔记。
    with path.open("a", encoding="utf-8") as f:
        f.write(content)

    # 返回追加状态，供上层反馈和审计使用。
    return f"appended:{path.name}"


def list_files(path: Path) -> list[str]:
    """列出目录中的文件名。"""

    # 如果目录不存在，返回空列表而不是抛异常，便于 Agent 继续处理。
    if not path.exists():
        return []

    # 只返回名称，不返回绝对路径，避免向上层暴露本机目录结构。
    return sorted(p.name for p in path.iterdir())
```

这里故意让 `tools.py` 保持“干净”：它只负责读、写、追加、列出文件，不判断路径是否越界，也不知道 Agent 是否可信。这样做不是忽视安全，而是把安全责任集中到 Harness 层，避免每个工具函数都复制一份不一致的校验逻辑。

需要注意：**不要把这些原子工具直接暴露给 Agent 调用**。如果 Agent 可以跳过 `run_tool` 直接调用 `tools.read_text(Path("../blocked/secret.txt"))`，前面设计的所有安全策略都会失效。

## 第四阶段：工具白名单与参数校验

### 目标

把前面分散的策略、路径解析和原子工具组合成统一执行入口。此阶段完成后，任何 Agent 工具请求都必须先进入 `run_tool(request)`，由 Harness 决定是否放行。

继续编辑 `harness.py`：

```python
# 导入底层原子工具。注意：Agent 不应直接调用 tools.py。
import tools


def audit(event: dict[str, Any]) -> None:
    """把一次工具调用事件追加写入审计日志。"""

    # 确保 logs 目录存在，避免第一次写日志时因为目录缺失失败。
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 给事件追加时间戳，便于课后按时间顺序复盘。
    event["time"] = datetime.now().isoformat(timespec="seconds")

    # 以 JSON Lines 格式追加写入；一行就是一次工具请求记录。
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def validate_request(request: dict[str, Any]) -> None:
    """校验 Agent 生成的工具请求是否符合执行前置条件。"""

    # Agent 输出可能不是字典；不是预期结构时直接拒绝。
    if not isinstance(request, dict):
        raise HarnessError("工具请求必须是字典")

    # 工具名必须存在于白名单中；未知工具默认拒绝。
    tool_name = request.get("tool")
    if tool_name not in ALLOWED_TOOLS:
        raise HarnessError(f"工具未授权：{tool_name}")

    # path 必须是非空字符串，后续才能进入路径解析。
    path = request.get("path")
    if not isinstance(path, str) or not path.strip():
        raise HarnessError("path 参数必须是非空字符串")

    # content 是写入类工具的正文；读取和列目录工具不应携带该参数。
    content = request.get("content", "")

    # 写入和追加必须显式提供 content，避免误把空字符串当作有效请求。
    if tool_name in {"write_text", "append_text"}:
        if "content" not in request:
            raise HarnessError(f"{tool_name} 缺少 content 参数")
        if not isinstance(content, str):
            raise HarnessError("content 参数必须是字符串")

    # 读取和列目录工具如果携带 content，说明请求意图和工具语义不匹配。
    if tool_name in {"read_text", "list_files"} and content:
        raise HarnessError(f"{tool_name} 不应包含 content 参数")

    # 任何写入内容都不能超过策略限制。
    if content and len(content) > MAX_WRITE_CHARS:
        raise HarnessError("写入内容过长")


def run_tool(request: dict[str, Any]) -> dict[str, Any]:
    """Harness 统一执行入口：校验请求、调用工具、记录审计并返回结构化结果。"""

    try:
        # 第一步：校验工具名、参数形态和内容长度。
        validate_request(request)

        # 第二步：取出工具名和路径，并将路径解析到安全工作区内。
        tool_name = request["tool"]
        path = resolve_workspace_path(request["path"])
        content = request.get("content", "")

        # 第三步：根据工具名路由到底层原子工具。
        if tool_name == "read_text":
            result = tools.read_text(path)
        elif tool_name == "write_text":
            result = tools.write_text(path, content)
        elif tool_name == "append_text":
            result = tools.append_text(path, content)
        elif tool_name == "list_files":
            result = tools.list_files(path)
        else:
            # 理论上不会走到这里；保留该分支作为防御式兜底。
            raise HarnessError(f"工具未实现：{tool_name}")

        # 第四步：成功时返回统一结构，并记录审计日志。
        response = {"ok": True, "result": result, "error": None}
        audit({"request": request, "response": response})
        return response

    except Exception as e:
        # 任何校验失败或工具异常都转成结构化错误，避免程序直接崩溃。
        response = {"ok": False, "result": None, "error": str(e)}

        # 失败请求同样要进入审计日志，这样才能复盘越权尝试。
        audit({"request": request, "response": response})
        return response


def build_feedback(response: dict[str, Any]) -> str:
    """把结构化响应转换为可回注给 Agent 的自然语言反馈。"""

    # 成功时把结果说明返回给上层。
    if response["ok"]:
        return f"工具执行成功，结果为：{response['result']}"

    # 失败时给出错误原因，提示 Agent 或调用方修正请求后重试。
    return f"工具执行失败，原因：{response['error']}。请修改工具名或参数后重试。"
```

### 讲解

`run_tool` 是 Harness 的核心入口。真实 Agent 系统中，大模型输出的工具调用请求必须先经过类似函数，而不是直接调用底层工具。

这段代码还体现了三个重要工程原则：

1. **统一入口**：所有工具调用都必须经过 `run_tool`，避免有的工具绕过校验直接执行。
2. **结构化返回**：无论成功还是失败，都返回 `{"ok": ..., "result": ..., "error": ...}`，方便上层 Agent 判断下一步。
3. **失败可反馈**：`build_feedback` 把执行结果转成可读文本，可以在真实 Agent 中回注到下一轮上下文，让模型知道如何修正工具名或参数。

## 第五阶段：模拟 Agent 请求

### 目标

用一组可控请求模拟 Agent 的工具调用输出，观察 Harness 如何处理成功请求、越权请求、未知工具和参数错误。此阶段不接入真实模型，是为了让安全边界先变得可复现、可测试。

创建 `main.py`：

```python
# main.py 用于模拟 Agent 产生的一批工具调用请求。
from harness import build_feedback, run_tool


# REQUESTS 中既包含安全请求，也包含故意构造的危险请求。
# 这样同学们可以一次运行就观察到放行、拦截和反馈三类结果。
REQUESTS = [
    # 合法读取：读取 workspace/note.md。
    {"tool": "read_text", "path": "note.md"},

    # 合法列目录：列出 workspace 根目录下的文件。
    {"tool": "list_files", "path": "."},

    # 合法写入：在 workspace 中生成 summary.md。
    {"tool": "write_text", "path": "summary.md", "content": "Harness 可以限制 Agent 的行为。"},

    # 危险请求：尝试通过 ../ 读取 workspace 之外的模拟秘密。
    {"tool": "read_text", "path": "../blocked/secret.txt"},

    # 危险请求：delete_file 不在工具白名单中。
    {"tool": "delete_file", "path": "note.md"},

    # 危险请求：.sh 扩展名不在允许列表中。
    {"tool": "write_text", "path": "run.sh", "content": "rm -rf /"},

    # 危险请求：写入内容超过 MAX_WRITE_CHARS 限制。
    {"tool": "append_text", "path": "note.md", "content": "x" * 3000},

    # 危险请求：读取工具不应夹带 content 参数。
    {"tool": "read_text", "path": "note.md", "content": "试图给读取工具夹带写入内容"},
]

# 逐条把模拟请求交给 Harness，观察结构化响应和反馈文本。
for request in REQUESTS:
    # 所有请求都必须从 run_tool 进入，不能直接调用 tools.py。
    response = run_tool(request)

    # 打印分隔线，便于课堂观察每个请求的处理结果。
    print("=" * 80)
    print("request:", request)
    print("response:", response)

    # feedback 模拟真实 Agent 系统中的“工具结果回注”。
    print("feedback:", build_feedback(response))
```

运行：

```bash
# 运行模拟 Agent 请求脚本，观察每条请求的 response 和 feedback。
python main.py
```

### 预期现象

1. 读取 `note.md` 成功。
2. 列出 `workspace/` 成功。
3. 写入 `summary.md` 成功。
4. 读取 `../blocked/secret.txt` 被拦截。
5. 调用 `delete_file` 被拦截。
6. 写入 `.sh` 文件被拦截。
7. 写入内容过长被拦截。
8. 读取工具夹带 `content` 参数被拦截。

同学们应重点观察：失败不是程序崩溃，而是以结构化 `error` 和可读 `feedback` 返回。这就是 Harness 与普通异常处理之间的区别：它把安全失败变成了上层 Agent 可以理解和修正的反馈。

## 第六阶段：安全测试

### 目标

用测试证明安全护栏确实生效。可以使用 `pytest`，也可以使用普通 `assert`。

创建 `test_harness.py`：

```python
# 测试文件只通过 Harness 入口调用工具，模拟真实 Agent 执行路径。
from harness import build_feedback, run_tool


def test_allowed_read():
    """合法读取 workspace/note.md 应成功。"""

    result = run_tool({"tool": "read_text", "path": "note.md"})
    assert result["ok"] is True


def test_block_path_traversal():
    """越权读取 blocked/secret.txt 应被路径边界拦截。"""

    result = run_tool({"tool": "read_text", "path": "../blocked/secret.txt"})
    assert result["ok"] is False
    assert "路径越界" in result["error"]


def test_block_unknown_tool():
    """未授权工具 delete_file 不应被执行。"""

    result = run_tool({"tool": "delete_file", "path": "note.md"})
    assert result["ok"] is False
    assert "工具未授权" in result["error"]


def test_block_extension():
    """危险扩展名 .sh 不应被写入。"""

    result = run_tool({"tool": "write_text", "path": "run.sh", "content": "echo hi"})
    assert result["ok"] is False
    assert "不允许的文件类型" in result["error"]


def test_block_missing_path():
    """缺少 path 参数时，Harness 应返回参数错误。"""

    result = run_tool({"tool": "read_text"})
    assert result["ok"] is False
    assert "path 参数必须是非空字符串" in result["error"]


def test_block_wrong_content_type():
    """content 不是字符串时，写入类工具应拒绝执行。"""

    result = run_tool({"tool": "write_text", "path": "note.md", "content": ["bad"]})
    assert result["ok"] is False
    assert "content 参数必须是字符串" in result["error"]


def test_block_missing_content_for_write():
    """write_text 缺少 content 时不应静默写入空文件。"""

    result = run_tool({"tool": "write_text", "path": "note.md"})
    assert result["ok"] is False
    assert "缺少 content 参数" in result["error"]


def test_block_read_with_content():
    """读取工具夹带 content 参数时，应判定为语义不匹配。"""

    result = run_tool({"tool": "read_text", "path": "note.md", "content": "overwrite"})
    assert result["ok"] is False
    assert "不应包含 content 参数" in result["error"]


def test_block_long_write():
    """超过写入长度上限的请求应被拒绝。"""

    result = run_tool({"tool": "append_text", "path": "note.md", "content": "x" * 3000})
    assert result["ok"] is False
    assert "写入内容过长" in result["error"]


def test_feedback_for_failure():
    """失败响应应能被转换为可回注给 Agent 的反馈文本。"""

    result = run_tool({"tool": "delete_file", "path": "note.md"})
    feedback = build_feedback(result)
    assert "工具执行失败" in feedback
    assert "工具未授权" in feedback
```

安装并运行：

```bash
# 安装 pytest 测试框架。
pip install pytest

# 运行当前目录下的 test_harness.py，并用简洁模式输出结果。
pytest -q
```

如果不想安装 `pytest`，可以直接在 `main.py` 中观察拦截结果。但正式验收工程质量时，建议保留自动化测试，因为安全护栏不能只靠人工观察一次输出。

## 第七阶段：审计日志观察

### 目标

理解 Harness 不只负责“拦截”，还要负责“留痕”。审计日志让同学们能够复盘 Agent 做过什么、哪些请求失败、失败原因是什么。

查看日志：

```bash
# 查看 JSON Lines 审计日志；每一行对应一次工具调用。
cat logs/audit.jsonl
```

同学们应观察每条记录是否包含：

1. 原始请求。
2. 执行结果。
3. 错误原因。
4. 时间戳。

审计日志的价值在于：当 Agent 出错时，系统可以把错误原因重新交给模型，让模型调整下一步动作。

`audit.jsonl` 使用 JSON Lines 格式：一行就是一次工具调用记录。这样做的好处是追加写入简单，后续也容易按行读取、过滤和统计。典型记录类似：

```json
{"request": {"tool": "delete_file", "path": "note.md"}, "response": {"ok": false, "result": null, "error": "工具未授权：delete_file"}, "time": "2026-05-11T10:30:00"}
```

同学们观察日志时，需要同时关注两件事：

1. 日志是否足以复盘问题，例如能看出哪个请求被拒绝、为什么被拒绝。
2. 日志是否过度记录敏感内容。真实系统中不应把密码、Token、真实个人信息或大段私密文件内容直接写入日志。

本实验的日志保存在文件中，因此即使重新运行 `main.py`，历史记录也会继续追加。这就是最简单的跨会话操作历史。

## 第八阶段：扩展为反馈回注

### 目标

把 Harness 的结构化结果转换为上层 Agent 能理解的反馈文本。安全系统不仅要拒绝危险动作，还要让调用方知道如何修正。

前面 `harness.py` 中已经实现了 `build_feedback(response)`。在本实验的 `main.py` 中，它只是被打印到终端；在真实 Agent 系统中，它会被放回下一轮模型上下文，让模型知道刚才的工具请求为什么失败。

可以把这个闭环理解为：

```text
Agent 生成请求：读取 ../blocked/secret.txt
    ↓
Harness 拦截：路径越界
    ↓
build_feedback 生成反馈：工具执行失败，原因：路径越界
    ↓
Agent 下一轮修正：改为读取 workspace 内的 note.md，或向用户说明无法读取
```

这一步非常重要。安全系统如果只拒绝、不解释，上层 Agent 很容易反复尝试同一个错误动作；如果反馈足够结构化，Agent 或调用方就有机会修正请求，而不是绕过规则。

## 第九阶段：完善安全文件助手 Skill 契约

### 目标

回到第零阶段创建的 `safe_file_skill/SKILL.md` 草稿，将前面实现的安全文件操作 Harness 整理成完整 Skill 契约。此时同学们已经有了工具白名单、路径边界、参数校验、审计日志和失败反馈，可以更准确地写清楚：这个能力可以做什么、不能做什么、失败时如何处理。

### 目录结构

确认实验目录中已经包含：

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

## 实验完成自检清单

完成本实验后，同学们可以用下面的清单检查自己的工程闭环是否完整：

| 检查项 | 自检问题 |
| :-- | :-- |
| Skill 能力入口 | `safe_file_skill/SKILL.md` 是否说明了能力范围、禁止行为和 Harness 调用流程？ |
| 请求协议 | 是否能说清楚 `tool`、`path`、`content` 三类字段分别表示什么？ |
| 安全策略 | `policy.py` 是否集中定义了工作区、日志位置、工具白名单、扩展名白名单和写入长度限制？ |
| 路径边界 | `resolve_workspace_path` 是否能拦截 `../blocked/secret.txt`？ |
| 原子工具 | `tools.py` 是否只做单一动作，不直接处理 Agent 请求？ |
| Harness 入口 | 所有工具调用是否都经过 `run_tool(request)`？ |
| 参数校验 | 是否覆盖了缺少路径、缺少内容、内容类型错误、内容过长等情况？ |
| 失败反馈 | 失败时是否返回结构化 `error`，并能通过 `build_feedback` 生成可读反馈？ |
| 审计日志 | `logs/audit.jsonl` 是否记录了成功和失败请求？ |
| 自动化测试 | `pytest -q` 是否能覆盖至少一个成功调用和多类失败调用？ |

如果某一项无法回答清楚，说明对应知识点还没有真正掌握，建议回到相应阶段重新运行和观察。

## 故障排除 FAQ

### Q1: 为什么 Prompt 里写“不要越权”还不够？

**A:** Prompt 是软约束，模型可能忽略或误解。Harness 是代码级硬约束，只要请求不符合规则，就不会执行。

### Q2: 路径校验为什么要用 `.resolve()`？

**A:** `.resolve()` 可以把 `../`、符号链接等路径归一化，之后再用 `relative_to(WORKSPACE_DIR)` 判断真实访问位置是否仍在工作区内。不要只用字符串前缀判断路径，因为同名前缀目录可能造成误判。

### Q3: 为什么工具函数不直接写安全判断？

**A:** 将安全策略集中放在 Harness 层，可以避免每个工具重复实现安全判断，也便于统一审计。

### Q4: 是否应该允许 Agent 删除文件？

**A:** 初学阶段不建议开放删除工具。即使要开放，也应先实现回收站、二次确认、路径白名单和审计日志。

### Q5: 审计日志是否需要保存模型原始输出？

**A:** 建议保存，但要注意脱敏。日志中不应记录真实密码、Token 或个人隐私信息。

### Q6: 为什么运行测试时 `note.md` 找不到？

**A:** 通常是当前终端不在 `harness_guardrail_lab` 目录，或没有执行环境准备中的 `mkdir workspace blocked logs safe_file_skill` 与 `echo ... > workspace/note.md`。先运行 `pwd` 或 `cd harness_guardrail_lab`，再确认 `workspace/note.md` 存在。

### Q7: 为什么本实验不用真实大模型？

**A:** 本实验的核心是执行边界，不是模型能力。用模拟 Agent 请求可以让同学们稳定复现成功、失败、越权和参数错误场景。接入真实模型时，只是把“生成请求”的部分换成模型输出，Harness 校验层不应改变。

### Q8: Skill 里已经写了禁止行为，为什么 Harness 还要重复校验？

**A:** Skill 是软契约，帮助 Agent 理解能力边界；Harness 是硬边界，负责真正拦截不合规请求。安全要求不能只写在说明文档里，必须落实到执行路径上。

### Q9: 为什么要默认拒绝，而不是遇到可疑请求时尽量猜测用户意图？

**A:** 工具执行会影响真实文件和系统状态。安全 Harness 应采用 fail closed 原则：请求不明确、参数不完整、路径不可信时先拒绝，并通过反馈让上层修正，而不是冒险执行。

## 参考资源

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python pathlib: https://docs.python.org/3/library/pathlib.html
- pytest: https://docs.pytest.org/
- OpenAI Safety Best Practices: https://platform.openai.com/docs/guides/safety-best-practices
