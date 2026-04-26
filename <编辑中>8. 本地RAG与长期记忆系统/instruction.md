# 《现代软件开发技术》上机实验手册：本地 RAG 与长期记忆系统

## 实验主题

本实验围绕“让 AI 只根据给定资料回答”展开。同学们将在本地构建一个轻量级 RAG（Retrieval-Augmented Generation，检索增强生成）系统，把课程资料切分、向量化、检索并拼接成上下文，最终让模型基于资料回答问题，同时拒绝回答资料外问题。

## 实验目标

完成本实验后，同学们应能够：

1. 理解 RAG 与普通大模型问答的区别。
2. 掌握文档切分、Embedding、向量检索、上下文拼接的基本流程。
3. 使用轻量级本地向量库保存课程资料片段。
4. 编写一个“问题 -> 检索 -> 拼接上下文 -> 生成回答”的最小 RAG 管道。
5. 设计资料外拒答机制，降低幻觉风险。
6. 评估检索命中率、回答相关性和拒答准确性。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：RAG 理论导入** | 理解长期记忆与上下文增强 | RAG, Embedding |
| **25-55'** | **模块二：资料准备与切分** | 将课程文本切成可检索片段 | Python |
| **55-95'** | **模块三：向量化与本地索引** | 构建轻量级向量检索结构 | sentence-transformers 或简化词袋 |
| **95-135'** | **模块四：Top-K 检索** | 根据问题召回相关资料片段 | Cosine Similarity |
| **135-180'** | **模块五：RAG 回答生成** | 拼接上下文并约束模型回答 | Ollama 或规则模拟 |
| **180-220'** | **模块六：拒答与评估** | 识别资料外问题并拒答 | Hit Rate, Refusal |
| **220-240'** | **模块七：总结与扩展** | 思考 RAG 在软件工程中的应用 | 实验复盘 |

## 实验安全注意事项

1. 本实验只使用课程资料或自造文本，不使用真实企业文档。
2. 如果使用个人笔记，应确认其中不含账号、手机号、Token、成绩表等敏感信息。
3. 本地向量库文件不要上传到公开仓库，除非确认内容可公开。
4. 模型回答必须基于检索资料，不允许编造资料中不存在的内容。
5. 如安装依赖失败，可使用本实验提供的简化词袋检索方案完成核心流程。

## 环境准备与验证

### 1. 创建实验目录

```bash
mkdir local_rag_lab
cd local_rag_lab
python -m venv .venv
```

激活环境后创建文件夹：

```bash
mkdir docs index outputs
```

### 2. 依赖选择

基础版本只使用 Python 标准库。增强版本可安装：

```bash
pip install sentence-transformers numpy
```

如果网络或算力受限，先使用标准库版本。

### 3. 准备资料

创建 `docs/course_notes.txt`：

```text
Git 是一种分布式版本控制系统，常用于记录代码历史、管理分支和协作开发。
TDD 是测试驱动开发，典型流程是 Red、Green、Refactor。
CI/CD 用于自动化构建、测试和部署，可以拦截不符合质量要求的代码。
AI Agent 通过理解用户意图、规划步骤并调用工具完成任务。
Harness 工程通过代码级护栏限制 Agent 的工具调用范围。
RAG 通过检索外部资料增强大模型回答，降低幻觉风险。
```

## 第一阶段：资料切分

### 目标

把长文档拆成多个短片段。片段太长会浪费上下文，片段太短会丢失语义。

创建 `chunker.py`：

```python
from pathlib import Path


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def split_by_lines(text: str) -> list[dict]:
    chunks = []
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        chunks.append({
            "id": f"chunk_{i:03d}",
            "text": line,
            "source": "course_notes.txt",
        })
    return chunks
```

创建 `build_chunks.py`：

```python
import json
from pathlib import Path

from chunker import load_text, split_by_lines

text = load_text("docs/course_notes.txt")
chunks = split_by_lines(text)
Path("index").mkdir(exist_ok=True)
Path("index/chunks.json").write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"chunks={len(chunks)}")
```

运行：

```bash
python build_chunks.py
```

## 第二阶段：简化词袋向量

### 目标

为了让所有同学都能完成实验，本阶段先用词袋方式实现检索，不依赖大型 Embedding 模型。

创建 `simple_vector.py`：

```python
import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    english = re.findall(r"[A-Za-z][A-Za-z0-9_/-]*", text.lower())
    chinese_terms = []
    for term in ["Git", "TDD", "CI", "CD", "Agent", "Harness", "RAG", "版本", "测试", "部署", "检索", "幻觉", "工具"]:
        if term.lower() in text.lower():
            chinese_terms.append(term.lower())
    return english + chinese_terms


def vectorize(text: str) -> Counter:
    return Counter(tokenize(text))


def cosine(a: Counter, b: Counter) -> float:
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
```

## 第三阶段：Top-K 检索

创建 `retriever.py`：

```python
import json
from pathlib import Path

from simple_vector import cosine, vectorize


def load_chunks(path: str = "index/chunks.json") -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def retrieve(question: str, top_k: int = 3) -> list[dict]:
    query_vec = vectorize(question)
    scored = []
    for chunk in load_chunks():
        score = cosine(query_vec, vectorize(chunk["text"]))
        scored.append({**chunk, "score": round(score, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [item for item in scored[:top_k] if item["score"] > 0]
```

创建 `run_retrieve.py`：

```python
from retriever import retrieve

for question in ["TDD 是什么？", "Harness 有什么作用？", "天气怎么样？"]:
    print("=" * 80)
    print("Q:", question)
    for item in retrieve(question):
        print(item)
```

运行：

```bash
python run_retrieve.py
```

## 第四阶段：上下文拼接与回答生成

### 目标

先实现一个不依赖模型的回答器，确保流程清楚。

创建 `rag_answer.py`：

```python
from retriever import retrieve


def build_context(chunks: list[dict]) -> str:
    lines = []
    for chunk in chunks:
        lines.append(f"[{chunk['id']}|{chunk['source']}] {chunk['text']}")
    return "\n".join(lines)


def answer_with_context(question: str) -> dict:
    chunks = retrieve(question, top_k=3)
    if not chunks:
        return {
            "answer": "资料中没有找到足够依据，无法回答该问题。",
            "sources": [],
            "grounded": False,
        }

    context = build_context(chunks)
    answer = f"根据资料：\n{context}\n\n针对问题“{question}”，可依据上述资料作答。"
    return {
        "answer": answer,
        "sources": [chunk["id"] for chunk in chunks],
        "grounded": True,
    }
```

创建 `main.py`：

```python
from rag_answer import answer_with_context

QUESTIONS = [
    "Git 是什么？",
    "TDD 的流程是什么？",
    "Harness 工程有什么作用？",
    "今天食堂有什么菜？",
]

for question in QUESTIONS:
    print("=" * 80)
    print("Q:", question)
    result = answer_with_context(question)
    print(result["answer"])
    print("sources:", result["sources"], "grounded:", result["grounded"])
```

运行：

```bash
python main.py
```

## 第五阶段：接入本地模型（可选增强）

如果本机已安装 Ollama，可将检索上下文交给模型生成自然语言回答。

提示词模板：

```text
你是课程助教。请只根据【资料】回答【问题】。
如果资料中没有依据，请回答“资料中没有找到足够依据，无法回答该问题。”

【资料】
{context}

【问题】
{question}
```

工程要求：

1. 不把原始问题直接交给模型裸答。
2. 不允许模型使用资料外知识补充。
3. 回答末尾列出使用的 `chunk_id`。

## 第六阶段：检索评估

创建 `eval_cases.py`：

```python
EVAL_CASES = [
    {"question": "Git 用来做什么？", "expected": "chunk_001"},
    {"question": "TDD 的三个阶段是什么？", "expected": "chunk_002"},
    {"question": "CI/CD 有什么作用？", "expected": "chunk_003"},
    {"question": "Agent 如何完成任务？", "expected": "chunk_004"},
    {"question": "RAG 为什么能降低幻觉？", "expected": "chunk_006"},
]
```

创建 `eval_retrieval.py`：

```python
from eval_cases import EVAL_CASES
from retriever import retrieve

hit = 0
for case in EVAL_CASES:
    results = retrieve(case["question"], top_k=3)
    ids = [item["id"] for item in results]
    ok = case["expected"] in ids
    hit += int(ok)
    print(case["question"], ids, "OK" if ok else "MISS")

print(f"hit_rate={hit}/{len(EVAL_CASES)}")
```

## 第七阶段：资料外拒答测试

创建 `eval_refusal.py`：

```python
from rag_answer import answer_with_context

OUT_OF_SCOPE = [
    "今天北京天气怎么样？",
    "请推荐一款手机。",
    "请解释量子力学的测不准原理。",
]

for question in OUT_OF_SCOPE:
    result = answer_with_context(question)
    print(question, result["grounded"], result["answer"])
```

资料外问题应返回 `grounded=False`。

## 故障排除 FAQ

### Q1: 为什么不用数据库？

**A:** 本实验目标是理解 RAG 核心流程。小规模课程资料使用 JSON 文件和简化向量即可完成教学目标。

### Q2: 检索结果不准怎么办？

**A:** 优先检查切分粒度和关键词覆盖。简化词袋模型对中文语义理解有限，可以通过扩展关键词或接入 Embedding 模型改进。

### Q3: 为什么要拒答？

**A:** RAG 的可靠性不仅体现在答对资料内问题，也体现在不编造资料外答案。

### Q4: Top-K 应该设置多大？

**A:** 小资料集可设置 2-3。过小容易漏召回，过大容易引入噪声。

### Q5: 是否必须安装 `sentence-transformers`？

**A:** 不是。标准库版本即可完成核心实验。增强版本适合有余力的同学。

## 参考资源

- RAG 概念介绍：https://www.promptingguide.ai/techniques/rag
- sentence-transformers：https://www.sbert.net/
- ChromaDB：https://docs.trychroma.com/
- FAISS：https://faiss.ai/
