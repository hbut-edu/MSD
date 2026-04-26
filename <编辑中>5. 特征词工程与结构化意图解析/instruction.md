# 《现代软件开发技术》上机实验手册：特征词工程与结构化意图解析

## 实验主题

本实验围绕“让大模型听懂业务意图”展开。前序实验已经让同学们完成了从传统 SaaS 到 AI Agent 的转变，本实验进一步把自然语言需求拆解为可计算、可验证、可路由的结构化任务，为后续 Harness 安全护栏、RAG 检索和多 Agent 工作流奠定输入基础。

## 实验目标

完成本实验后，同学们应能够：

1. 理解 Prompt Engineering 与特征词工程的区别。
2. 从冗长、含糊、夹杂干扰信息的业务需求中提取关键特征词。
3. 设计意图分类规则，将用户输入路由到不同业务动作。
4. 使用 JSON Schema 思想约束大模型或规则程序输出结构化结果。
5. 评估 Zero-shot、Few-shot、CoT 和特征词约束对输出稳定性的影响。
6. 编写一个轻量级“需求文本 -> 结构化任务单”的 Python 原型。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：理论导入** | 理解为什么 Agent 需要稳定的结构化输入 | Prompt Engineering, Feature Engineering |
| **25-55'** | **模块二：实验数据准备** | 构造带噪声的业务需求样本 | Python, JSON |
| **55-95'** | **模块三：特征词提取与降噪** | 从需求文本中提取对象、动作、约束、输出格式 | 正则表达式, 字典规则 |
| **95-135'** | **模块四：意图分类与任务路由** | 将自然语言映射到 `query`、`calculate`、`export` 等动作 | Rule-based Router |
| **135-185'** | **模块五：结构化输出约束** | 生成稳定 JSON 任务单并进行字段校验 | JSON, Schema Validation |
| **185-220'** | **模块六：提示词策略对比** | 比较 Zero-shot、Few-shot、CoT、特征词约束的稳定性 | Ollama 或规则模拟 |
| **220-240'** | **模块七：总结与扩展** | 梳理意图解析在 Agent 系统中的位置 | 实验复盘 |

## 实验安全注意事项

1. 本实验只处理教学用模拟文本，不要输入真实身份证号、手机号、密码、API Key、企业内部合同等敏感信息。
2. 如果使用在线大模型 API，请使用临时测试 Key，并通过环境变量读取，不要写入代码。
3. 如果本机没有可用模型，可以先使用规则程序完成结构化解析，再将模型调用作为扩展项。
4. 所有生成的 JSON 文件建议保存在本实验目录或 `附件/` 下，避免污染其他课程目录。

## 环境准备与验证

### 1. 基础环境

建议环境：

- Python 3.10+
- VS Code、PyCharm 或 Trae IDE
- 可选：Ollama 与本地模型 `qwen3.5:9b`

### 2. 创建实验目录

```bash
mkdir intent_parser_lab
cd intent_parser_lab
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

### 3. 验证 Python

```bash
python --version
```

期望看到 Python 3.10 或更高版本。

### 4. 可选：验证 Ollama

```bash
ollama list
ollama run qwen3.5:9b "请用一句话说明什么是意图识别。"
```

如果模型加载较慢，说明本地模型正在初始化，耐心等待即可。

## 第一阶段：建立实验样本

### 目标

构造一组贴近业务场景的自然语言需求。样本要故意包含口语、冗余、模糊表达和输出格式要求，方便后续观察解析效果。

### 操作步骤

创建 `samples.py`：

```python
SAMPLES = [
    {
        "id": "case_001",
        "text": "麻烦帮我看一下研发部这个月的工资，最好把应发、扣税、实发都列出来，不用导出文件。",
        "expected_intent": "calculate_salary",
    },
    {
        "id": "case_002",
        "text": "把全公司员工名单查出来，按照部门分组，最后给我一个 csv，文件名就叫 employees_by_dept.csv。",
        "expected_intent": "export_employee",
    },
    {
        "id": "case_003",
        "text": "我只想知道李四的五险一金是多少，不要整张表，直接告诉我结果。",
        "expected_intent": "calculate_benefit",
    },
    {
        "id": "case_004",
        "text": "先查销售部员工，再算工资，如果有人缺少职级字段，请标记出来，暂时不要导出。",
        "expected_intent": "multi_step_salary",
    },
]
```

### 观察要点

同学们需要注意，每条需求通常包含四类信息：

1. **动作**：查、算、导出、分组、标记。
2. **对象**：员工、工资、部门、五险一金、文件。
3. **约束**：只看某个人、不导出、按部门分组、缺字段标记。
4. **输出格式**：表格、CSV、直接回答、文件名。

## 第二阶段：特征词提取与降噪

### 目标

编写一个规则版特征词提取器，让同学们先理解“可解释的意图解析”如何工作。

### 操作步骤

创建 `feature_extractor.py`：

```python
import re
from typing import Dict, List


ACTION_KEYWORDS = {
    "query": ["查", "查询", "看一下", "列出来", "知道"],
    "calculate": ["算", "计算", "扣税", "五险一金", "应发", "实发"],
    "export": ["导出", "csv", "文件", "下载"],
    "group": ["分组", "按照部门", "按部门"],
    "validate": ["缺少", "标记", "检查"],
}

OBJECT_KEYWORDS = {
    "employee": ["员工", "名单", "李四"],
    "department": ["研发部", "销售部", "部门", "全公司"],
    "salary": ["工资", "应发", "扣税", "实发"],
    "benefit": ["五险一金"],
}


def match_keywords(text: str, keyword_map: Dict[str, List[str]]) -> List[str]:
    matched = []
    for label, words in keyword_map.items():
        if any(word in text for word in words):
            matched.append(label)
    return matched


def extract_filename(text: str) -> str | None:
    match = re.search(r"[\w\-]+\.csv", text, flags=re.IGNORECASE)
    return match.group(0) if match else None


def extract_features(text: str) -> dict:
    return {
        "actions": match_keywords(text, ACTION_KEYWORDS),
        "objects": match_keywords(text, OBJECT_KEYWORDS),
        "filename": extract_filename(text),
        "raw_text": text,
    }
```

创建 `run_extract.py`：

```python
from samples import SAMPLES
from feature_extractor import extract_features

for sample in SAMPLES:
    print("=" * 60)
    print(sample["id"], sample["text"])
    print(extract_features(sample["text"]))
```

运行：

```bash
python run_extract.py
```

### 验证要点

观察每条样本是否能提取出合理的 `actions` 与 `objects`。如果某条样本漏掉重要信息，优先改关键词表，而不是急着改复杂算法。

### 思考

规则系统虽然不够“智能”，但它有三个优点：

1. 输出稳定。
2. 逻辑可解释。
3. 失败原因容易定位。

这正是后续 Harness 工程的重要基础。

## 第三阶段：意图分类与任务路由

### 目标

将特征词转化为业务意图。Agent 调工具之前，必须先知道当前需求属于哪类任务。

### 操作步骤

创建 `intent_router.py`：

```python
def route_intent(features: dict) -> str:
    actions = set(features["actions"])
    objects = set(features["objects"])

    if "export" in actions and "employee" in objects:
        return "export_employee"

    if "calculate" in actions and "benefit" in objects:
        return "calculate_benefit"

    if "calculate" in actions and "salary" in objects and "query" in actions:
        return "multi_step_salary"

    if "calculate" in actions and "salary" in objects:
        return "calculate_salary"

    if "query" in actions and "employee" in objects:
        return "query_employee"

    return "unknown"
```

创建 `run_route.py`：

```python
from samples import SAMPLES
from feature_extractor import extract_features
from intent_router import route_intent

correct = 0

for sample in SAMPLES:
    features = extract_features(sample["text"])
    intent = route_intent(features)
    ok = intent == sample["expected_intent"]
    correct += int(ok)
    print(sample["id"], intent, "OK" if ok else f"EXPECTED={sample['expected_intent']}")

print(f"accuracy={correct}/{len(SAMPLES)}")
```

运行：

```bash
python run_route.py
```

### 调试建议

如果分类结果不符合预期，按以下顺序检查：

1. 特征词是否提取成功。
2. 意图判断规则是否顺序错误。
3. 是否存在多个意图同时命中的情况。
4. 是否需要新增 `priority` 规则。

## 第四阶段：结构化任务单生成

### 目标

把自然语言需求转成稳定 JSON。后续 Agent、工作流、API 都应该优先接收结构化输入，而不是直接吃原始口语文本。

### 任务单格式

本实验采用如下任务单结构：

```json
{
  "intent": "calculate_salary",
  "actions": ["query", "calculate"],
  "objects": ["department", "salary"],
  "constraints": {
    "department": "研发部",
    "person": null,
    "export": false
  },
  "output": {
    "format": "markdown",
    "filename": null
  },
  "raw_text": "原始需求"
}
```

创建 `task_builder.py`：

```python
def extract_constraints(text: str, features: dict) -> dict:
    department = None
    if "研发部" in text:
        department = "研发部"
    elif "销售部" in text:
        department = "销售部"
    elif "全公司" in text:
        department = "全公司"

    person = "李四" if "李四" in text else None
    export = "export" in features["actions"] and "不用导出" not in text and "不要导出" not in text

    return {
        "department": department,
        "person": person,
        "export": export,
    }


def build_task(text: str, features: dict, intent: str) -> dict:
    filename = features.get("filename")
    return {
        "intent": intent,
        "actions": features["actions"],
        "objects": features["objects"],
        "constraints": extract_constraints(text, features),
        "output": {
            "format": "csv" if filename else "markdown",
            "filename": filename,
        },
        "raw_text": text,
    }
```

创建 `run_task.py`：

```python
import json

from samples import SAMPLES
from feature_extractor import extract_features
from intent_router import route_intent
from task_builder import build_task

for sample in SAMPLES:
    features = extract_features(sample["text"])
    intent = route_intent(features)
    task = build_task(sample["text"], features, intent)
    print(json.dumps(task, ensure_ascii=False, indent=2))
```

## 第五阶段：字段校验与失败解释

### 目标

结构化输出不能只“看起来像 JSON”，还必须满足字段完整性要求。本阶段编写轻量校验器。

创建 `validator.py`：

```python
REQUIRED_TOP_LEVEL = ["intent", "actions", "objects", "constraints", "output", "raw_text"]


def validate_task(task: dict) -> tuple[bool, list[str]]:
    errors = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in task:
            errors.append(f"missing top-level field: {key}")

    if not isinstance(task.get("actions"), list):
        errors.append("actions must be a list")

    if task.get("intent") == "unknown":
        errors.append("intent is unknown")

    output = task.get("output", {})
    if output.get("format") == "csv" and not output.get("filename"):
        errors.append("csv output requires filename")

    constraints = task.get("constraints", {})
    if constraints.get("export") is False and output.get("format") == "csv":
        errors.append("export=false conflicts with csv output")

    return len(errors) == 0, errors
```

创建 `run_validate.py`：

```python
from samples import SAMPLES
from feature_extractor import extract_features
from intent_router import route_intent
from task_builder import build_task
from validator import validate_task

for sample in SAMPLES:
    features = extract_features(sample["text"])
    intent = route_intent(features)
    task = build_task(sample["text"], features, intent)
    ok, errors = validate_task(task)
    print(sample["id"], "VALID" if ok else "INVALID", errors)
```

### 观察要点

校验失败不是坏事。失败信息越清楚，后续 Agent 越容易自我修复。

## 第六阶段：提示词策略对比

### 目标

比较不同提示方式对结构化输出的影响。若本机没有模型，可将本阶段作为课堂演示或扩展练习。

### 对比维度

| 策略 | 特点 | 常见问题 |
| :-- | :-- | :-- |
| Zero-shot | 直接让模型解析 | 字段不稳定，容易漏约束 |
| Few-shot | 给模型几个示例 | 稳定性提高，但示例覆盖有限 |
| CoT | 让模型先分析再输出 | 解释更充分，但可能污染 JSON |
| 特征词约束 | 先提取特征，再生成 JSON | 稳定性最好，工程可控 |

### 推荐提示词模板

```text
你是一个业务需求解析器。请只输出 JSON，不要输出解释。

字段要求：
- intent: 字符串
- actions: 字符串数组
- objects: 字符串数组
- constraints: 对象，包含 department、person、export
- output: 对象，包含 format、filename
- raw_text: 原始输入

用户需求：
{text}
```

### 课堂建议

同学们可以用同一条输入分别测试四种提示词策略，记录是否出现以下问题：

1. JSON 无法解析。
2. 字段缺失。
3. 布尔值被写成中文。
4. 文件名丢失。
5. “不要导出”被误判为导出。

## 第七阶段：综合运行脚本

创建 `main.py`：

```python
import json

from samples import SAMPLES
from feature_extractor import extract_features
from intent_router import route_intent
from task_builder import build_task
from validator import validate_task


def parse_requirement(text: str) -> dict:
    features = extract_features(text)
    intent = route_intent(features)
    task = build_task(text, features, intent)
    ok, errors = validate_task(task)
    task["valid"] = ok
    task["errors"] = errors
    return task


if __name__ == "__main__":
    for sample in SAMPLES:
        result = parse_requirement(sample["text"])
        print("=" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))
```

运行：

```bash
python main.py
```

## 故障排除 FAQ

### Q1: 为什么不用大模型直接解析？

**A:** 可以使用大模型，但工程系统不能完全依赖模型“刚好输出正确”。规则特征词、字段校验和失败解释能显著提升系统稳定性。

### Q2: 特征词表是不是越大越好？

**A:** 不是。特征词表应优先覆盖高频业务场景。过大的词表会带来误匹配，建议每次新增词都配一个测试样本。

### Q3: 为什么“不要导出”容易被误判？

**A:** 因为文本里同时出现了“导出”这个关键词。工程上需要处理否定词，例如“不用”“不要”“暂时不”等。

### Q4: JSON 输出字段应该由谁决定？

**A:** 由业务系统决定，而不是由模型自由发挥。模型可以帮助填充字段，但字段结构应由工程侧定义。

### Q5: 规则方法是否太初级？

**A:** 本实验使用规则方法是为了让同学们看清意图解析的底层逻辑。真实系统通常会混合规则、模型和校验器。

## 参考资源

- Prompt Engineering Guide: https://www.promptingguide.ai/
- JSON Schema: https://json-schema.org/
- Python `re` 文档: https://docs.python.org/3/library/re.html
- OpenAI Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
