# 《现代软件开发技术》上机实验手册：本地 RAG 与知识增强问答：从资料检索到资料外拒答

## 实验主题

本实验围绕“让 AI 只根据给定资料回答”展开。同学们将在本地构建一个轻量级 RAG（Retrieval-Augmented Generation，检索增强生成）系统，把原神主题资料切分、向量化、检索并拼接成上下文，最终让模型基于资料回答问题，同时拒绝回答资料外问题。基础部分会先跑通最小闭环，进阶部分会继续加入向量数据库、真实工业向量库实践、真实大模型接入、引用来源、权限控制、多文档综合、过期文档识别和冲突内容提示。

本实验承接前序“传统 SaaS 到 AI Agent (MCP)”实验：前序实验解决“模型如何理解意图并调用工具”，本章进一步解决“模型回答时如何获得可靠资料依据”。本章不只关注“能检索到文本”，还要让同学们理解：一个可交付的 RAG 系统必须能说明答案从哪里来、谁有权看哪些资料、多个文档如何合并、旧资料如何降权或排除，以及资料互相矛盾时如何提醒用户。

## 为什么需要 RAG

RAG 是 Retrieval-Augmented Generation 的缩写，中文通常译为“检索增强生成”。它的基本思想是：**先从外部资料库中检索与问题相关的片段，再把这些片段作为上下文交给大模型生成回答**。也就是说，RAG 不直接改变模型参数，而是在模型回答前，为它补上一层可更新、可检查的资料依据。

通用大模型具有较强的语言理解和生成能力，但它并不天然掌握某个班级、课程、企业或项目中的最新资料。即使模型能流畅回答，也可能出现“说得像真的，但资料中没有依据”的情况。在软件工程场景中，这会带来几个具体问题：

| 通用模型的具体问题 | 可能造成的后果 | RAG 的解决思路 |
| :-- | :-- | :-- |
| 不知道本地课程资料、企业制度、项目文档等私有知识 | 回答泛泛而谈，无法结合真实资料 | 先检索本地资料，再把相关片段提供给模型 |
| 训练数据可能过时 | 对新版本接口、新规章、新项目说明回答错误 | 更新资料库即可让检索结果变新 |
| 容易补全不存在的细节 | 编造引用、流程、参数或结论，形成幻觉 | 要求回答只能基于检索到的上下文 |
| 难以说明答案依据 | 教师、同学或用户无法复核回答是否可靠 | 返回 `chunk_id`、来源文件和引用片段 |
| 一次性把所有资料塞进提示词不可行 | 上下文过长、成本高、噪声多 | 只召回 Top-K 相关片段进入上下文 |
| 资料外问题也可能被强行回答 | 系统越界回答，降低可信度 | 检索不到依据时明确拒答 |

因此，RAG 的核心作用不是让模型“变聪明一点”，而是给模型建立一个可更新、可检索、可追溯的外部知识层。模型负责理解问题和组织语言，检索系统负责找到依据，工程代码负责控制上下文和拒答边界。本实验要训练的正是这条工程链路：**问题 -> 检索资料 -> 拼接上下文 -> 基于资料回答 -> 没有依据就拒答**。

## RAG 与垂直领域模型训练的取舍

当大模型需要回答某个专业领域的问题时，常见思路有两类：一类是 **RAG**，即不改模型参数，而是在回答前先检索外部资料，把相关片段放进上下文；另一类是 **直接训练或微调垂直领域模型**，即用领域数据继续训练模型，让知识和表达习惯进入模型参数。

两种方案并不是互斥关系。真实项目中，常见做法是先用 RAG 快速建立可追溯的知识问答能力，再根据数据规模、稳定性要求和成本预算，判断是否需要训练垂直领域模型。

| 维度 | RAG | 直接训练或微调垂直领域模型 |
| :-- | :-- | :-- |
| 知识更新 | 更新资料库即可生效，适合课程资料、制度文档、产品手册等频繁变化内容 | 需要重新训练、微调或发布模型，更新周期更长 |
| 可追溯性 | 可以返回 `chunk_id`、来源文件和引用片段，便于检查依据 | 模型直接生成答案，知识来源不容易追溯 |
| 成本与门槛 | 小规模场景可用普通电脑和 Python 文件实现，适合作为课堂实验 | 需要准备高质量训练数据、训练算力、评估集和发布流程 |
| 回答稳定性 | 检索质量会影响回答质量，召回错误会导致答非所问 | 对高频领域表达可能更稳定，但仍可能幻觉 |
| 隐私与治理 | 资料库、索引和访问权限需要单独管理 | 训练数据进入模型参数后，删除和溯源更困难 |
| 适用场景 | 文档问答、知识库助手、政策查询、课程资料问答 | 领域语言风格适配、固定任务格式、专业术语理解增强 |

本实验选择 RAG 作为主线，是因为它更适合本科课堂快速验证：同学们可以直接看到“资料如何被切分、如何被检索、如何进入上下文、答案依据来自哪里”。这也能帮助大家建立一个重要判断：降低幻觉不只是写更强的提示词，还需要让模型回答时拿到可靠、可检查的资料依据。

## 本章知识结构与递进路线

本章不是一上来就使用完整框架，而是从最小闭环逐步推进到工程化 RAG。这样安排的原因是：如果同学们没有先看清楚“片段、向量、召回、上下文、拒答”这些基本对象，直接使用向量数据库和大模型接口时，很容易只是在调用库函数，却不知道系统为什么会答错、为什么会泄露、为什么会引用不完整。

本章的完整链路如下：

```text
原神资料
  -> 文档切分
  -> 简化向量表示
  -> Top-K 检索
  -> 上下文拼接
  -> 规则化回答与资料外拒答
  -> 检索评估
  -> 带元数据的轻量向量库
  -> 引用来源 / 权限过滤 / 多文档综合
  -> ChromaDB 真实向量数据库
  -> 本地 Qwen 真实模型生成
  -> 过期识别 / 冲突提示 / 工程复盘
```

从教学角度看，各阶段承担不同层次的任务：

| 层次 | 阶段 | 解决的问题 | 形成的关键产物 |
| :-- | :-- | :-- | :-- |
| 最小闭环 | 第一至第四阶段 | 资料如何被切分、检索并进入回答 | `chunks.json`、`retriever.py`、`rag_answer.py` |
| 可靠性边界 | 第五至第七阶段 | 如何约束模型回答、如何评估召回、如何拒答资料外问题 | 提示词模板、评估样例、拒答测试 |
| 工程化知识库 | 第八至第九阶段 | 如何保存来源、权限、版本和冲突信息 | `genshin_corpus.json`、`vector_store.json`、`governed_rag.py` |
| 工业工具迁移 | 第十阶段 | 如何把手写向量库迁移到真实向量数据库 | `chroma_vector_db.py`、`index/chroma_db/` |
| 真实生成演练 | 第十一阶段 | 如何把治理后的上下文交给真实 Qwen 模型 | `llm_rag_answer.py`、`run_real_llm_rag.py` |
| 治理复盘 | 第十二阶段 | 如何处理过期资料和冲突结论 | 告警信息、冲突来源、人工确认提示 |

本章中“简化词袋向量”和“ChromaDB 向量数据库”不是互相替代的重复内容。前者用于解释向量检索原理，后者用于展示真实工程接口。课堂版本的 ChromaDB 仍然使用简化向量，目的是让同学们把注意力放在向量库写入、持久化、元数据过滤和检索治理上；真实项目中应把 `embed()` 替换为稳定的 Embedding 模型，并记录模型版本。

## 实验目标

完成本实验后，同学们应能够：

1. 理解 RAG 与普通大模型问答的区别。
2. 掌握文档切分、Embedding、向量检索、上下文拼接的基本流程。
3. 使用轻量级本地向量库保存原神主题资料片段。
4. 使用 ChromaDB 这类真实向量数据库构建可持久化的 RAG 检索层。
5. 将 RAG 检索结果挂载到本地 Qwen 模型上，完成真实生成演练。
6. 编写一个“问题 -> 检索 -> 拼接上下文 -> 生成回答”的最小 RAG 管道。
7. 设计资料外拒答机制，降低幻觉风险。
8. 为回答生成引用来源，能追溯到 `chunk_id`、文档标题和版本信息。
9. 在检索阶段实现基于角色的资料权限过滤。
10. 支持从多个文档召回资料并进行综合回答。
11. 识别过期文档和冲突内容，并在回答中给出提示。
12. 评估检索命中率、回答相关性、拒答准确性、引用完整性、权限过滤效果和真实模型生成效果。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：RAG 理论导入** | 理解长期记忆与上下文增强 | RAG, Embedding |
| **25-55'** | **模块二：资料准备与切分** | 将原神主题文本切成可检索片段 | Python |
| **55-95'** | **模块三：向量化与本地索引** | 构建轻量级向量检索结构 | sentence-transformers 或简化词袋 |
| **95-130'** | **模块四：Top-K 检索** | 根据问题召回相关资料片段 | Cosine Similarity |
| **130-160'** | **模块五：RAG 回答生成** | 拼接上下文并约束模型回答 | Ollama 或规则模拟 |
| **160-185'** | **模块六：拒答与基础评估** | 识别资料外问题并评估命中率 | Hit Rate, Refusal |
| **185-215'** | **模块七：轻量向量数据库与元数据** | 持久化向量、来源、权限和版本信息 | Vector Store, Metadata |
| **215-245'** | **模块八：工程化检索治理** | 引用来源、权限过滤、多文档综合 | Citation, ACL, Synthesis |
| **245-275'** | **模块九：真实向量数据库实践** | 使用 ChromaDB 构建工业方案 RAG 检索层 | ChromaDB, Persistent Collection |
| **275-305'** | **模块十：真实大模型接入演练** | 同一套 RAG 上下文接入本地 Qwen 模型 | Ollama, Qwen, 原生 chat API |
| **305-315'** | **模块十一：过期与冲突识别** | 识别过期资料和互相矛盾的内容 | Freshness, Conflict Detection |
| **315-320'** | **模块十二：总结与扩展** | 思考 RAG 在软件工程中的应用 | 实验复盘 |

## 实验安全注意事项

1. 本实验只使用原神相关公开常识或自造文本，不使用真实企业文档；文中的原神资料为教学用简化样例，不代表游戏实时版本公告。
2. 如果使用个人笔记，应确认其中不含账号、手机号、Token、成绩表等敏感信息。
3. 本地向量库文件不要上传到公开仓库，除非确认内容可公开。
4. 模型回答必须基于检索资料，不允许编造资料中不存在的内容。
5. 带权限标记的资料必须在检索阶段过滤，不要只依赖提示词提醒模型“不要泄露”。
6. 本地 Qwen 模型运行时应注意内存占用，必要时减少 Top-K、缩短上下文或切换更小的量化模型。
7. 如安装依赖失败，可使用本实验提供的简化词袋检索方案完成核心流程。

### RAG 失效模式与防护点

RAG 系统的风险不只来自模型，也来自资料、检索和上下文组织。本实验后半部分加入引用、权限、过期和冲突处理，就是为了让同学们看到这些风险在工程上应该如何落地处理。

| 失效模式 | 具体表现 | 本实验中的防护点 |
| :-- | :-- | :-- |
| 召回错误 | 问题相关资料没有进入 Top-K，或召回了无关片段 | 检索评估、命中率统计、误检漏检分析 |
| 资料外幻觉 | 检索不到依据时模型仍然编造答案 | `grounded=False` 与明确拒答 |
| 来源不可追溯 | 回答正确但无法说明依据 | `chunk_id`、标题、来源文件、更新时间和相似度 |
| 权限泄露 | 未授权资料进入模型上下文 | 检索阶段按 `role` 过滤，未授权片段不进入上下文 |
| 旧资料误用 | 已过期资料被当作当前依据 | `expires_at`、`expired` 标记和默认过滤 |
| 内容冲突 | 同一主题出现不同结论 | `claim_key` / `claim_value` 冲突检测和人工确认提示 |
| 资料注入 | 文档片段中包含诱导模型忽略规则的内容 | 系统提示限定只依据上下文，工程代码控制上下文边界 |

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
pip install sentence-transformers numpy chromadb
```

如果网络或算力受限，先使用标准库版本完成前半部分；工业向量数据库实践建议安装 `chromadb`。

### 3. 准备资料

创建 `docs/genshin_notes.txt`：

```text
原神是一款开放世界冒险游戏，玩家以旅行者身份在提瓦特大陆探索不同地区。
祈愿系统可以消耗相应道具抽取角色或武器，是游戏中获取新角色和装备的重要方式之一。
原石是一种重要资源，可以用于兑换纠缠之缘或相遇之缘，也常用于参与祈愿。
角色养成包括等级提升、武器强化、天赋升级和命之座解锁等内容。
圣遗物可以提供主属性和副属性，用于提升角色的攻击、防御、生命或元素相关能力。
元素反应由不同元素相互作用触发，例如蒸发、融化、超载、感电和扩散等。
原粹树脂是一种体力资源，常用于领取地脉、秘境和首领挑战奖励。
```

### 4. 文件流转总览

开始编码前，先建立一个文件流转印象。后续每个阶段都在这条链路上增加一个能力，而不是另起一套系统。

| 阶段 | 输入 | 输出 | 验证方式 |
| :-- | :-- | :-- | :-- |
| 资料切分 | `docs/genshin_notes.txt` | `index/chunks.json` | 运行后看到 `chunks=7` 左右的输出 |
| 词袋向量 | 问题文本、片段文本 | `Counter` 向量 | 相同关键词越多，相似度越高 |
| Top-K 检索 | 问题、`chunks.json` | 带 `score` 的片段列表 | 原石、圣遗物等问题能命中对应片段 |
| 规则化回答 | 检索片段 | `answer/sources/grounded` | 资料外问题返回 `grounded=False` |
| 轻量向量库 | `genshin_corpus.json` | `index/vector_store.json` | 记录中同时有文本、向量和元数据 |
| ChromaDB | 多文档语料 | `index/chroma_db/` | `chroma_records` 等于写入片段数 |
| 本地 Qwen | 治理后的上下文 | 自然语言回答和引用 | 回答包含引用编号，不越过资料范围 |

## 第一阶段：资料切分

### 目标

把长文档拆成多个短片段。片段太长会浪费上下文，片段太短会丢失语义。

本阶段先只按行切分资料。创建 `chunker.py`，它负责读取原始文本并生成最基础的 `chunk` 结构：

```python
from pathlib import Path


def load_text(path: str) -> str:
    """读取原始资料文本，作为后续切分的输入。"""
    return Path(path).read_text(encoding="utf-8")


def split_by_lines(text: str) -> list[dict]:
    """按行切分教学资料，并为每个片段生成可追溯的 id。"""
    chunks = []
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        chunks.append({
            "id": f"chunk_{i:03d}",
            "text": line,
            "source": "genshin_notes.txt",
        })
    return chunks
```

再创建 `build_chunks.py`。这个脚本把 `chunker.py` 的切分结果写入 `index/chunks.json`，供后续检索器读取：

```python
import json
from pathlib import Path

from chunker import load_text, split_by_lines

text = load_text("docs/genshin_notes.txt")
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

预期可以看到类似 `chunks=7` 的输出。此时系统还没有“智能”，但已经形成了 RAG 的第一个关键产物：可检索的资料片段。

## 第二阶段：简化词袋向量

### 目标

为了让所有同学都能完成实验，本阶段先用词袋方式实现检索，不依赖大型 Embedding 模型。词袋向量不能真正理解中文语义，但它足够展示一个核心事实：RAG 检索需要把“问题”和“资料片段”变成可比较的表示。

创建 `simple_vector.py`。这个文件提供分词、向量化和相似度计算三个最小能力：

```python
import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """把问题或资料片段转换为简化 token，便于课堂观察检索原理。"""
    english = re.findall(r"[A-Za-z][A-Za-z0-9_/-]*", text.lower())
    chinese_terms = []
    for term in [
        "原神", "玩家", "旅行者", "提瓦特", "祈愿", "原石", "纠缠之缘", "相遇之缘",
        "角色", "武器", "养成", "等级", "天赋", "命之座", "圣遗物",
        "主属性", "副属性", "攻击", "防御", "生命", "元素", "反应",
        "蒸发", "融化", "超载", "感电", "扩散", "原粹树脂", "体力",
        "地脉", "秘境", "首领", "奖励", "活动", "建议", "优先",
    ]:
        if term.lower() in text.lower():
            chinese_terms.append(term.lower())
    return english + chinese_terms


def vectorize(text: str) -> Counter:
    """用词频 Counter 表示文本向量。"""
    return Counter(tokenize(text))


def cosine(a: Counter, b: Counter) -> float:
    """计算两个词袋向量的余弦相似度。"""
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
```

## 第三阶段：Top-K 检索

### 目标

本阶段把“资料片段”和“问题向量”连接起来，返回最相关的 Top-K 片段。Top-K 的意义是控制进入上下文的资料数量：太少会漏掉依据，太多会引入噪声。

创建 `retriever.py`。这个文件读取第一阶段生成的 `chunks.json`，并使用第二阶段的余弦相似度排序：

```python
import json
from pathlib import Path

from simple_vector import cosine, vectorize


def load_chunks(path: str = "index/chunks.json") -> list[dict]:
    """读取切分后的资料片段。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def retrieve(question: str, top_k: int = 3) -> list[dict]:
    """根据问题召回最相关的 Top-K 资料片段。"""
    query_vec = vectorize(question)
    scored = []
    for chunk in load_chunks():
        score = cosine(query_vec, vectorize(chunk["text"]))
        scored.append({**chunk, "score": round(score, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [item for item in scored[:top_k] if item["score"] > 0]
```

创建 `run_retrieve.py`。这个脚本用于观察检索器对资料内问题和资料外问题的不同表现：

```python
from retriever import retrieve

for question in ["原石有什么用途？", "圣遗物有什么作用？", "今天现实天气怎么样？"]:
    print("=" * 80)
    print("Q:", question)
    for item in retrieve(question):
        print(item)
```

运行：

```bash
python run_retrieve.py
```

预期现象：原石、圣遗物相关问题能召回对应片段；现实天气问题没有足够关键词，应返回空结果或极低相关结果。此时还没有调用模型，系统只是在回答“哪些资料可能有用”。

## 第四阶段：上下文拼接与回答生成

### 目标

先实现一个不依赖模型的回答器，确保流程清楚。

创建 `rag_answer.py`。这个文件把检索结果拼成上下文，并在没有检索结果时返回拒答：

```python
from retriever import retrieve


def build_context(chunks: list[dict]) -> str:
    """把召回片段整理成带来源标识的上下文。"""
    lines = []
    for chunk in chunks:
        lines.append(f"[{chunk['id']}|{chunk['source']}] {chunk['text']}")
    return "\n".join(lines)


def answer_with_context(question: str) -> dict:
    """基于检索上下文生成规则化回答，并在无依据时拒答。"""
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

创建 `main.py`。这个脚本把资料内问题和资料外问题放在一起运行，便于观察 `grounded` 状态：

```python
from rag_answer import answer_with_context

QUESTIONS = [
    "原神玩家扮演谁？",
    "祈愿系统可以抽取什么角色或武器？",
    "元素反应有哪些例子？",
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

到这里，最小 RAG 闭环已经完成：资料被切分，问题可以检索片段，片段可以拼接成上下文，没有依据时可以拒答。后续阶段只是在这个闭环上逐步增加评估、元数据、向量数据库和真实模型。

## 第五阶段：模型提示词模板

本阶段先不强制调用真实模型，只设计模型提示词模板。这样做是为了让同学们先理解：RAG 不是把问题直接扔给模型，而是把“检索到的资料上下文”和“回答边界”一起交给模型。真正的本地 Qwen API 接入会在第十一阶段完成。

提示词模板：

```text
你是原神主题资料问答助手。请只根据【资料】回答【问题】。
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

### 目标

能检索并不等于检索正确。本阶段用一组小型评估样例检查 Top-K 结果中是否包含预期片段，帮助同学们理解“召回质量”是 RAG 系统的基础质量指标。

创建 `eval_cases.py`。每个样例包含一个问题和一个预期命中的片段编号：

```python
EVAL_CASES = [
    {"question": "原神玩家扮演谁？", "expected": "chunk_001"},
    {"question": "祈愿系统可以抽取什么角色或武器？", "expected": "chunk_002"},
    {"question": "原石有什么用途？", "expected": "chunk_003"},
    {"question": "圣遗物有什么作用？", "expected": "chunk_005"},
    {"question": "元素反应有哪些例子？", "expected": "chunk_006"},
    {"question": "原粹树脂用于什么？", "expected": "chunk_007"},
]
```

创建 `eval_retrieval.py`。这个脚本统计预期片段是否出现在 Top-K 结果中：

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

运行：

```bash
python eval_retrieval.py
```

如果命中率较低，优先检查关键词表是否覆盖了问题中的关键表达，再检查切分粒度是否过粗或过细。

## 第七阶段：资料外拒答测试

### 目标

RAG 系统可靠性的另一半是“知道自己不知道”。本阶段集中测试资料外问题，确认没有相关资料时系统不会强行回答。

创建 `eval_refusal.py`。这些问题不属于原神资料库，应触发拒答：

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

## 第八阶段：构建带元数据的轻量向量数据库

### 目标

前面的 `index/chunks.json` 只保存了文本片段和简单来源。真实 RAG 系统还需要保存更多治理信息，例如文档标题、版本、更新时间、过期时间、可见角色、冲突标识等。向量数据库的作用不是只“存向量”，而是把 **向量 + 文本 + 元数据** 放在一起，并支持按相似度和过滤条件检索。

为了保证所有同学都能运行，本实验先用 JSON 文件实现一个轻量向量数据库。它不是正式数据库产品，但保留了向量数据库最核心的工程结构。后续如果接入 ChromaDB、FAISS、Milvus 或云端向量库，数据结构和检索思想是一致的。

### 与真实向量数据库的对应关系

真实向量数据库通常至少保存四类信息：片段编号、原文、Embedding 向量和元数据过滤字段。本实验使用 JSON 保存这些字段，是为了让同学们看清楚它们在 RAG 系统中的作用。迁移到正式向量数据库时，可以按下面方式对应：

| 本实验字段 | 正式向量数据库中的常见字段 | 作用 |
| :-- | :-- | :-- |
| `chunk_id` | `id` | 唯一定位一个资料片段，用于引用来源和问题排查 |
| `text` | `document` 或 `payload.text` | 进入上下文的原始资料 |
| `vector` | `embedding` | 用于相似度检索 |
| `title`、`source`、`updated_at` | `metadata` | 显示引用来源，支持版本追溯 |
| `roles` | `metadata` 或独立 ACL 表 | 在检索前过滤未授权资料 |
| `expires_at` | `metadata` | 判断资料是否过期 |
| `claim_key`、`claim_value` | `metadata` | 检测同一主题下的冲突结论 |

例如使用 ChromaDB、Milvus 或云端向量库时，核心流程通常是：写入资料时把 `chunk_id` 作为主键，把片段文本作为 `document`，把 Embedding 写入 `embedding`，把权限、来源、更新时间和冲突标识写入 `metadata`；检索时先带上权限和有效期过滤条件，再按向量相似度召回 Top-K。也就是说，权限控制、过期过滤和引用来源不是提示词技巧，而是向量库查询条件和元数据设计的一部分。

### 创建多文档资料库

为了让后续引用来源能够落到真实文件，先创建几份补充资料。`genshin_corpus.json` 会把这些文件路径写入 `source` 元数据中。

创建 `docs/genshin_build.md`：

```text
角色养成包括等级提升、武器强化、天赋升级和命之座解锁等内容。
圣遗物可以提供主属性和副属性，用于提升角色的攻击、防御、生命或元素相关能力。
元素反应由不同元素相互作用触发，例如蒸发、融化、超载、感电和扩散等。
```

创建 `docs/resin_advice_2026.md`：

```text
当前教学模拟资料建议：原粹树脂优先用于秘境奖励，以便稳定获取角色养成材料和圣遗物。
```

创建 `docs/resin_advice_2024.md`：

```text
旧版教学模拟资料建议：原粹树脂优先用于地脉奖励，以便快速积累角色经验书和摩拉。
```

创建 `docs/teacher_private_strategy.md`：

```text
教师提示：讲解角色养成时，可提醒同学先围绕一个主要输出角色配置武器、天赋和圣遗物。
```

再创建 `docs/genshin_corpus.json`。这个 JSON 文件不是普通资料正文，而是“资料清单 + 元数据清单”：它把正文片段、来源文件、更新时间、过期时间、角色权限和冲突标识组织到一起。

创建 `docs/genshin_corpus.json`：

```json
{
  "documents": [
    {
      "doc_id": "genshin_basics_v1",
      "title": "原神基础说明",
      "source": "docs/genshin_notes.txt",
      "updated_at": "2026-05-01",
      "expires_at": "2099-12-31",
      "roles": ["student", "teacher"],
      "claim_key": null,
      "claim_value": null,
      "content": [
        "原神是一款开放世界冒险游戏，玩家以旅行者身份在提瓦特大陆探索不同地区。",
        "祈愿系统可以消耗相应道具抽取角色或武器，是游戏中获取新角色和装备的重要方式之一。",
        "原石是一种重要资源，可以用于兑换纠缠之缘或相遇之缘，也常用于参与祈愿。"
      ]
    },
    {
      "doc_id": "genshin_build_v1",
      "title": "角色养成与战斗资料",
      "source": "docs/genshin_build.md",
      "updated_at": "2026-05-02",
      "expires_at": "2099-12-31",
      "roles": ["student", "teacher"],
      "claim_key": null,
      "claim_value": null,
      "content": [
        "角色养成包括等级提升、武器强化、天赋升级和命之座解锁等内容。",
        "圣遗物可以提供主属性和副属性，用于提升角色的攻击、防御、生命或元素相关能力。",
        "元素反应由不同元素相互作用触发，例如蒸发、融化、超载、感电和扩散等。"
      ]
    },
    {
      "doc_id": "resin_advice_2026",
      "title": "原粹树脂使用建议（当前教学模拟版）",
      "source": "docs/resin_advice_2026.md",
      "updated_at": "2026-05-03",
      "expires_at": "2099-12-31",
      "roles": ["student", "teacher"],
      "claim_key": "resin_priority",
      "claim_value": "秘境优先",
      "content": [
        "当前教学模拟资料建议：原粹树脂优先用于秘境奖励，以便稳定获取角色养成材料和圣遗物。"
      ]
    },
    {
      "doc_id": "resin_advice_2024_old",
      "title": "原粹树脂使用建议（旧版教学模拟资料）",
      "source": "docs/resin_advice_2024.md",
      "updated_at": "2024-05-01",
      "expires_at": "2024-12-31",
      "roles": ["student", "teacher"],
      "claim_key": "resin_priority",
      "claim_value": "地脉优先",
      "content": [
        "旧版教学模拟资料建议：原粹树脂优先用于地脉奖励，以便快速积累角色经验书和摩拉。"
      ]
    },
    {
      "doc_id": "teacher_private_strategy_v1",
      "title": "教师用课堂提示",
      "source": "docs/teacher_private_strategy.md",
      "updated_at": "2026-05-04",
      "expires_at": "2099-12-31",
      "roles": ["teacher"],
      "claim_key": null,
      "claim_value": null,
      "content": [
        "教师提示：讲解角色养成时，可提醒同学先围绕一个主要输出角色配置武器、天赋和圣遗物。"
      ]
    }
  ]
}
```

这里的资料是教学模拟数据，不要求完全对应游戏实时版本。它故意包含一份旧版树脂建议和一份教师可见资料，用来观察过期识别、冲突提示和权限过滤。

### 构建轻量向量数据库

创建 `vector_db.py`：

```python
import json
from datetime import date
from pathlib import Path

from simple_vector import cosine, vectorize


def parse_date(value: str | None):
    """把元数据中的日期字符串转换成 date，便于判断资料时效。"""
    if not value:
        return None
    return date.fromisoformat(value)


def is_expired(metadata: dict, today: date | None = None) -> bool:
    """根据 expires_at 判断资料是否已经过期。"""
    today = today or date.today()
    expires_at = parse_date(metadata.get("expires_at"))
    return bool(expires_at and expires_at < today)


def can_access(metadata: dict, role: str) -> bool:
    """检查当前角色是否有权访问该资料片段。"""
    roles = metadata.get("roles", [])
    return role in roles


def build_vector_store(
    corpus_path: str = "docs/genshin_corpus.json",
    output_path: str = "index/vector_store.json",
) -> None:
    """把多文档语料写入轻量向量库，保留文本、向量和治理元数据。"""
    corpus = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
    records = []

    for doc in corpus["documents"]:
        for index, text in enumerate(doc["content"], start=1):
            chunk_id = f"{doc['doc_id']}#c{index:03d}"
            metadata = {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "source": doc["source"],
                "updated_at": doc["updated_at"],
                "expires_at": doc["expires_at"],
                "roles": doc["roles"],
                "claim_key": doc.get("claim_key"),
                "claim_value": doc.get("claim_value"),
            }
            records.append({
                "chunk_id": chunk_id,
                "text": text,
                "vector": dict(vectorize(text)),
                "metadata": metadata,
            })

    Path(output_path).parent.mkdir(exist_ok=True)
    Path(output_path).write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"vector_records={len(records)}")


def load_vector_store(path: str = "index/vector_store.json") -> list[dict]:
    """读取轻量向量库记录。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def search_vector_db(
    question: str,
    role: str = "student",
    top_k: int = 5,
    include_expired: bool = False,
) -> list[dict]:
    """执行带角色权限和过期过滤的向量检索。"""
    query_vec = vectorize(question)
    scored = []

    for record in load_vector_store():
        metadata = record["metadata"]
        if not can_access(metadata, role):
            continue
        if is_expired(metadata) and not include_expired:
            continue

        score = cosine(query_vec, record["vector"])
        if score <= 0:
            continue

        item = {**record, "score": round(score, 4), "expired": is_expired(metadata)}
        scored.append(item)

    # 有效资料优先；同一新鲜度下再按相似度排序。
    scored.sort(key=lambda x: (x["expired"], -x["score"]))
    return scored[:top_k]


if __name__ == "__main__":
    build_vector_store()
```

运行：

```bash
python vector_db.py
```

再创建 `run_vector_search.py`：

```python
from vector_db import search_vector_db


for role in ["student", "teacher"]:
    print("=" * 80)
    print("role:", role)
    for item in search_vector_db("课堂讲角色养成时有什么建议？", role=role):
        print(item["chunk_id"], item["metadata"]["title"], item["score"])
```

观察重点：

1. `student` 角色不应检索到 `teacher_private_strategy_v1`。
2. `teacher` 角色可以检索到教师用课堂提示。
3. 这说明权限控制必须发生在检索阶段，而不是把所有资料都塞给模型后再要求模型“不要泄露”。

## 第九阶段：引用来源、权限控制与多文档综合

### 目标

一个可交付的 RAG 回答不应只给出自然语言答案，还应返回证据来源。否则同学、教师或用户无法判断答案是否真的来自资料库。本阶段将把检索结果整理成带引用的回答结构，并支持从多个文档综合信息。

创建 `governed_rag.py`：

```python
from collections import defaultdict

from vector_db import is_expired, search_vector_db


def format_citation(chunk: dict) -> dict:
    """把检索片段转换为回答中可展示的引用来源。"""
    metadata = chunk["metadata"]
    return {
        "chunk_id": chunk["chunk_id"],
        "title": metadata["title"],
        "source": metadata["source"],
        "updated_at": metadata["updated_at"],
        "expires_at": metadata["expires_at"],
        "score": chunk["score"],
        "expired": chunk["expired"],
    }


def detect_conflicts(chunks: list[dict]) -> dict:
    """识别同一 claim_key 下是否存在多个不同 claim_value。"""
    grouped = defaultdict(lambda: defaultdict(list))
    for chunk in chunks:
        metadata = chunk["metadata"]
        key = metadata.get("claim_key")
        value = metadata.get("claim_value")
        if key and value:
            grouped[key][value].append(chunk["chunk_id"])

    conflicts = {}
    for key, values in grouped.items():
        if len(values) > 1:
            conflicts[key] = dict(values)
    return conflicts


def build_evidence_lines(chunks: list[dict]) -> list[str]:
    """把多个资料片段整理成可直接展示的证据行。"""
    lines = []
    for chunk in chunks:
        meta = chunk["metadata"]
        status = "已过期" if is_expired(meta) else "有效"
        lines.append(
            f"- {chunk['text']} "
            f"[{chunk['chunk_id']}；{meta['title']}；{status}；score={chunk['score']}]"
        )
    return lines


def synthesize_answer(question: str, chunks: list[dict], warnings: list[str]) -> str:
    """在不调用模型的情况下，生成带证据和告警的规则化回答。"""
    evidence = "\n".join(build_evidence_lines(chunks))
    warning_text = ""
    if warnings:
        warning_text = "注意：" + "；".join(warnings) + "\n"

    return (
        f"问题：{question}\n"
        f"{warning_text}"
        "根据当前可访问资料，可以综合如下：\n"
        f"{evidence}\n"
        "以上回答只基于列出的引用来源。"
    )


def answer_with_governance(
    question: str,
    role: str = "student",
    include_expired: bool = False,
) -> dict:
    """执行检索治理流程，返回回答、引用、告警和 grounded 状态。"""
    chunks = search_vector_db(
        question=question,
        role=role,
        top_k=5,
        include_expired=include_expired,
    )

    if not chunks:
        return {
            "answer": "资料中没有找到足够依据，无法回答该问题。",
            "citations": [],
            "warnings": [],
            "grounded": False,
        }

    warnings = []
    expired_chunks = [chunk for chunk in chunks if chunk["expired"]]
    if expired_chunks:
        warnings.append(
            "检索结果包含过期资料，请优先参考未过期来源，并在实验记录中说明处理方式。"
        )

    conflicts = detect_conflicts(chunks)
    if conflicts:
        warnings.append(
            f"检测到同一主题存在冲突内容：{conflicts}。回答时应提示用户需要人工确认。"
        )

    return {
        "answer": synthesize_answer(question, chunks, warnings),
        "citations": [format_citation(chunk) for chunk in chunks],
        "warnings": warnings,
        "grounded": True,
    }
```

创建 `run_governed_rag.py`：

```python
from governed_rag import answer_with_governance


CASES = [
    ("原石、祈愿和角色养成有什么关系？", "student", False),
    ("课堂讲角色养成时有什么建议？", "student", False),
    ("课堂讲角色养成时有什么建议？", "teacher", False),
]

for question, role, include_expired in CASES:
    print("=" * 80)
    print("question:", question)
    print("role:", role)
    result = answer_with_governance(question, role=role, include_expired=include_expired)
    print(result["answer"])
    print("citations:", result["citations"])
    print("warnings:", result["warnings"])
```

观察重点：

1. “原石、祈愿和角色养成有什么关系？”应从多个文档片段中综合资料，而不是只返回一个片段。
2. `student` 角色不应看到教师私有资料。
3. 教师角色可以看到教师提示，但回答仍应显示引用来源。

## 第十阶段：使用真实向量数据库构建工业方案 RAG

### 目标

前面的 JSON 向量库用于帮助同学们看清楚“向量、文本、元数据”之间的关系。真实项目不会依赖手写 JSON 文件逐条扫描，而会使用向量数据库管理写入、持久化、索引、相似度检索和元数据过滤。本阶段使用 ChromaDB 构建一个本地可运行的真实向量数据库版本，并保留前面已经实现的引用来源、权限控制、过期过滤和冲突提示。

常见工业方案可以按部署方式理解：

| 方案 | 适用场景 | 课堂中的理解重点 |
| :-- | :-- | :-- |
| ChromaDB | 本地开发、教学实验、小型知识库原型 | Python 接口简单，支持持久化集合和元数据过滤 |
| Milvus | 大规模向量检索、分布式部署 | 适合数据量较大、需要独立向量检索服务的场景 |
| Qdrant | 带 payload 过滤的向量检索服务 | 适合理解“向量相似度 + 结构化过滤”的工程形态 |
| pgvector | 已经使用 PostgreSQL 的业务系统 | 适合把向量检索和关系型数据、事务、权限表放在一起 |
| 云端向量库 | 企业生产环境、托管运维 | 关注鉴权、备份、监控、扩缩容和数据合规 |

本实验选择 ChromaDB，是因为它既是真实向量数据库，又可以在普通电脑上通过 Python 持久化运行。换成 Milvus、Qdrant 或 pgvector 时，工程结构仍然相同：写入阶段保存 `id/document/embedding/metadata`，查询阶段使用向量相似度召回，并在查询条件中加入角色权限、有效期和其他业务过滤。

### 使用 ChromaDB 写入原神知识库

本阶段使用 ChromaDB 的真实持久化集合接口，但仍沿用前面的简化向量。这样安排可以把变量控制住：同学们先观察“向量数据库如何保存和过滤资料”，再在有余力时把 `embed()` 替换为真实 Embedding 模型。

创建 `chroma_vector_db.py`。这个文件负责把 `docs/genshin_corpus.json` 写入 ChromaDB，并提供带权限和过期过滤的查询函数：

```python
import json
from datetime import date
from pathlib import Path

import chromadb

from simple_vector import tokenize


COLLECTION_NAME = "genshin_rag"
TERMS = [
    "原神", "玩家", "旅行者", "提瓦特", "祈愿", "原石", "纠缠之缘", "相遇之缘",
    "角色", "武器", "养成", "等级", "天赋", "命之座", "圣遗物",
    "主属性", "副属性", "攻击", "防御", "生命", "元素", "反应",
    "蒸发", "融化", "超载", "感电", "扩散", "原粹树脂", "体力",
    "地脉", "秘境", "首领", "奖励", "活动", "建议", "优先",
]


def embed(text: str) -> list[float]:
    """把文本转换为固定长度向量，模拟真实 Embedding 写入向量库。"""
    tokens = set(tokenize(text))
    return [1.0 if term.lower() in tokens else 0.0 for term in TERMS]


def parse_date(value: str | None):
    """解析日期字符串，用于向量库元数据的时效判断。"""
    if not value:
        return None
    return date.fromisoformat(value)


def is_expired(metadata: dict, today: date | None = None) -> bool:
    """根据 expires_at 给 ChromaDB 元数据写入 expired 标记。"""
    today = today or date.today()
    expires_at = parse_date(metadata.get("expires_at"))
    return bool(expires_at and expires_at < today)


def get_client(path: str = "index/chroma_db"):
    """创建 ChromaDB 持久化客户端，数据会保存在本地目录。"""
    return chromadb.PersistentClient(path=path)


def get_collection(client):
    """获取或创建原神 RAG 集合。"""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_chroma_store(corpus_path: str = "docs/genshin_corpus.json") -> None:
    """把语料批量写入 ChromaDB，形成真实可查询的向量集合。"""
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = get_collection(client)
    corpus = json.loads(Path(corpus_path).read_text(encoding="utf-8"))

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for doc in corpus["documents"]:
        for index, text in enumerate(doc["content"], start=1):
            chunk_id = f"{doc['doc_id']}#c{index:03d}"
            metadata = {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "source": doc["source"],
                "updated_at": doc["updated_at"],
                "expires_at": doc["expires_at"],
                "roles": ",".join(doc["roles"]),
                "role_student": "student" in doc["roles"],
                "role_teacher": "teacher" in doc["roles"],
                "claim_key": doc.get("claim_key") or "",
                "claim_value": doc.get("claim_value") or "",
            }
            metadata["expired"] = is_expired(metadata)

            ids.append(chunk_id)
            documents.append(text)
            embeddings.append(embed(text))
            metadatas.append(metadata)

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"chroma_records={collection.count()}")


def build_where(role: str, include_expired: bool) -> dict:
    """构造 ChromaDB 元数据过滤条件，先过滤权限和过期状态。"""
    conditions = [{f"role_{role}": True}]
    if not include_expired:
        conditions.append({"expired": False})
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search_chroma_db(
    question: str,
    role: str = "student",
    top_k: int = 5,
    include_expired: bool = False,
) -> list[dict]:
    """通过 ChromaDB 查询相似片段，并返回统一的 RAG chunk 结构。"""
    query_embedding = embed(question)
    if not any(query_embedding):
        return []

    collection = get_collection(get_client())
    count = collection.count()
    if count == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k * 3, count),
        where=build_where(role, include_expired),
        include=["documents", "metadatas", "distances"],
    )

    items = []
    for chunk_id, text, metadata, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        score = round(1.0 - distance, 4)
        if score <= 0:
            continue
        items.append({
            "chunk_id": chunk_id,
            "text": text,
            "metadata": metadata,
            "score": score,
            "expired": bool(metadata["expired"]),
        })

    items.sort(key=lambda x: (x["expired"], -x["score"]))
    return items[:top_k]


if __name__ == "__main__":
    build_chroma_store()
```

运行：

```bash
python chroma_vector_db.py
```

执行后，`index/chroma_db/` 中会出现 ChromaDB 的持久化数据。此时资料不再只是一个 JSON 列表，而是写入了真实向量数据库集合。

### 使用 ChromaDB 检索并生成带治理信息的回答

创建 `run_chroma_rag.py`。这个脚本复用前面 `governed_rag.py` 中的引用和冲突检测逻辑，只把检索后端从 JSON 向量库换成 ChromaDB：

```python
from chroma_vector_db import build_chroma_store, search_chroma_db
from governed_rag import detect_conflicts, format_citation, synthesize_answer


def answer_with_chroma(
    question: str,
    role: str = "student",
    include_expired: bool = False,
) -> dict:
    """使用 ChromaDB 检索结果生成带引用和告警的 RAG 回答。"""
    chunks = search_chroma_db(
        question=question,
        role=role,
        top_k=5,
        include_expired=include_expired,
    )

    if not chunks:
        return {
            "answer": "资料中没有找到足够依据，无法回答该问题。",
            "citations": [],
            "warnings": [],
            "grounded": False,
        }

    warnings = []
    if any(chunk["expired"] for chunk in chunks):
        warnings.append("检索结果包含过期资料，请优先参考未过期来源。")

    conflicts = detect_conflicts(chunks)
    if conflicts:
        warnings.append(f"检测到冲突内容：{conflicts}，需要人工确认。")

    return {
        "answer": synthesize_answer(question, chunks, warnings),
        "citations": [format_citation(chunk) for chunk in chunks],
        "warnings": warnings,
        "grounded": True,
    }


build_chroma_store()

CASES = [
    ("课堂讲角色养成时有什么建议？", "student", False),
    ("课堂讲角色养成时有什么建议？", "teacher", False),
    ("原粹树脂应该优先做什么？", "student", True),
]

for question, role, include_expired in CASES:
    print("=" * 80)
    print("question:", question)
    print("role:", role)
    result = answer_with_chroma(question, role=role, include_expired=include_expired)
    print(result["answer"])
    print("citations:", result["citations"])
    print("warnings:", result["warnings"])
```

运行：

```bash
python run_chroma_rag.py
```

观察重点：

1. ChromaDB 的 `collection.add()` 保存了 `ids`、`documents`、`embeddings` 和 `metadatas`。
2. ChromaDB 的 `collection.query()` 使用 `query_embeddings` 做向量检索，并通过 `where` 条件过滤角色权限和过期状态。
3. `student` 角色仍然不能检索教师私有资料，说明权限过滤已经进入真实向量数据库查询层。
4. 检索结果仍能进入 `governed_rag.py` 的引用、冲突和回答合成逻辑，说明上层 RAG 治理可以复用。

### 工业实现要补齐的能力

课堂中的 ChromaDB 版本已经具备真实向量数据库的基本形态，但生产系统还需要继续补齐：

| 能力 | 生产系统中的要求 |
| :-- | :-- |
| Embedding 模型 | 使用稳定的中文或多语种 Embedding 模型，并记录模型版本 |
| 批量写入 | 支持增量更新、重复写入去重和失败重试 |
| 权限控制 | 查询时结合用户身份、组织、角色和文档 ACL，不让未授权片段进入上下文 |
| 生命周期管理 | 过期资料下线、重新索引、索引版本回滚 |
| 可观测性 | 记录查询词、召回片段、相似度、过滤条件、回答引用和拒答原因 |
| 灾备与合规 | 备份、删除、审计、密钥管理和数据分级 |

这也是为什么真实 RAG 系统不能只写一个“把文档塞给模型”的提示词。向量数据库承担的是知识检索基础设施的角色，模型只是后续的语言组织组件。

## 第十一阶段：接入真实大模型进行 RAG 场景演练

### 目标

到目前为止，同学们已经完成了检索、引用、权限、过期和冲突提示。下一步要把 RAG 挂载到前序实验已经部署过的本地 Qwen 模型上：检索系统负责找到可信资料，大模型负责在这些资料范围内组织自然语言回答。

本阶段沿用前序实验中的 Ollama 本地 Qwen 模型，例如 `qwen3.6:35b-a3b` 或 `qwen3.6:27b`。这样同学们可以把“上一章的本地模型调用能力”和“本章的 RAG 检索治理能力”接在一起，形成一个可运行的真实本地知识问答系统。

需要特别注意：RAG 的权限过滤、资料外拒答和引用来源不应交给模型“自觉遵守”。模型只接收已经过滤后的上下文，代码仍然负责判断哪些资料可以进入上下文、哪些资料已经过期、哪些资料存在冲突。

### 模型接入配置

本实验用 Ollama 原生 `chat` 接口调用本地 Qwen。这个接口可以显式设置 `think: false`，避免模型把课堂时间大量消耗在隐藏推理上。

本地 Qwen 配置：

```bash
ollama ps
export OLLAMA_BASE_URL="http://localhost:11434"
export QWEN_MODEL="qwen3.6:35b-a3b"
```

如果本机只部署了 Dense 对照模型，也可以改为：

```bash
export QWEN_MODEL="qwen3.6:27b"
```

在接入 RAG 之前，先做一次最小模型连通性测试：

```bash
python - <<'PY'
import json
import os
import urllib.request

root = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
model = os.getenv("QWEN_MODEL", "qwen3.6:35b-a3b")
payload = {
    "model": model,
    "messages": [{"role": "user", "content": "请只回复：连接成功"}],
    "stream": False,
    "think": False,
    "options": {"temperature": 0, "num_predict": 64},
}
request = urllib.request.Request(
    f"{root}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(request, timeout=300) as response:
    data = json.loads(response.read().decode("utf-8"))
print((data.get("message", {}).get("content") or "").strip())
PY
```

如果这里失败，先回到前序实验检查 Ollama 服务、模型名称和内存占用，不要急着调试 RAG 代码。

### 编写统一的大模型适配器

创建 `llm_rag_answer.py`。这个文件把 ChromaDB 检索结果变成模型上下文，并通过 Ollama 原生接口调用本地 Qwen：

```python
import json
import os
import urllib.error
import urllib.request

from chroma_vector_db import search_chroma_db
from governed_rag import detect_conflicts, format_citation


SYSTEM_PROMPT = """你是一个严格基于资料回答的 RAG 助手。
你只能依据 <context> 中的资料回答。
如果资料不足，请明确说“资料中没有足够依据”。
回答必须保留方括号中的引用编号，例如 [genshin_basics_v1#c002]。
如果系统提示存在过期或冲突资料，不要给出唯一确定结论。
回答应简洁，最多 5 条要点，每条不要超过 60 字。"""


def build_context(chunks: list[dict]) -> str:
    """把已通过权限和时效过滤的检索片段整理成模型上下文。"""
    lines = []
    for chunk in chunks:
        meta = chunk["metadata"]
        status = "已过期" if chunk["expired"] else "有效"
        lines.append(
            f"[{chunk['chunk_id']}] "
            f"标题：{meta['title']}；来源：{meta['source']}；"
            f"更新时间：{meta['updated_at']}；状态：{status}；"
            f"内容：{chunk['text']}"
        )
    return "\n".join(lines)


def build_warnings(chunks: list[dict]) -> list[str]:
    """根据检索结果生成工程告警，提醒模型不要忽略过期或冲突资料。"""
    warnings = []
    if any(chunk["expired"] for chunk in chunks):
        warnings.append("检索结果包含过期资料，请优先参考未过期来源。")

    conflicts = detect_conflicts(chunks)
    if conflicts:
        warnings.append(f"检测到冲突内容：{conflicts}，需要人工确认。")

    return warnings


def qwen_config() -> dict:
    """读取本地 Qwen 的连接参数，模型名称可通过环境变量切换。"""
    return {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("QWEN_MODEL", "qwen3.6:35b-a3b"),
        "max_tokens": int(os.getenv("QWEN_MAX_TOKENS", "1024")),
    }


def ollama_chat_url(base_url: str) -> str:
    """把可能带 /v1 的地址统一转换成 Ollama 原生 chat 地址。"""
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]
    return f"{root}/api/chat"


def call_qwen(messages: list[dict]) -> str:
    """通过 Ollama 原生 chat 接口调用本地 Qwen，并关闭隐藏思考模式。"""
    config = qwen_config()
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": config["max_tokens"],
        },
    }
    request = urllib.request.Request(
        ollama_chat_url(config["base_url"]),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接 Ollama：{exc}") from exc

    if data.get("done_reason") == "length":
        raise RuntimeError(
            "Qwen 输出被 token 上限截断。"
            "请调大 QWEN_MAX_TOKENS，例如设置为 2048 或 4096。"
        )

    message = data.get("message", {})
    answer = (message.get("content") or "").strip()
    if answer:
        return answer

    raise RuntimeError("Qwen 返回了空答案，请检查模型状态和提示词。")


def answer_with_qwen(
    question: str,
    role: str = "student",
    include_expired: bool = False,
) -> dict:
    """先执行 RAG 检索治理，再把可访问上下文交给本地 Qwen 生成。"""
    # 检索层先完成权限、过期过滤和 Top-K 召回，模型不会看到未授权片段。
    chunks = search_chroma_db(
        question=question,
        role=role,
        top_k=5,
        include_expired=include_expired,
    )

    if not chunks:
        return {
            "answer": "资料中没有找到足够依据，无法回答该问题。",
            "citations": [],
            "warnings": [],
            "grounded": False,
        }

    warnings = build_warnings(chunks)
    context = build_context(chunks)
    # 模型输入只包含已经筛选过的上下文和告警，不把整个资料库塞给模型。
    user_prompt = (
        f"<context>\n{context}\n</context>\n\n"
        f"系统提示：{'；'.join(warnings) if warnings else '无'}\n"
        f"用户问题：{question}"
    )

    answer = call_qwen(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return {
        "answer": answer,
        "citations": [format_citation(chunk) for chunk in chunks],
        "warnings": warnings,
        "grounded": True,
    }
```

这段代码刻意把“检索治理”和“模型生成”拆开：`search_chroma_db()` 负责查询向量库并做权限、过期过滤；`answer_with_qwen()` 只把已经治理过的上下文交给本地 Qwen。这样同学们可以清楚看到 RAG 系统中“检索层”和“生成层”的边界。

### 运行真实模型对比演练

创建 `run_real_llm_rag.py`。这个脚本会先重建 ChromaDB 知识库，再把同一批问题交给本地 Qwen：

```python
from chroma_vector_db import build_chroma_store
from llm_rag_answer import answer_with_qwen


QUESTIONS = [
    "原石、祈愿和角色养成有什么关系？",
    "课堂讲角色养成时有什么建议？",
    "原粹树脂应该优先做什么？",
]


def run_case(question: str, include_expired: bool = False) -> None:
    """运行一次真实模型 RAG 问答，并打印回答、引用和告警。"""
    print("=" * 80)
    print("question:", question)
    try:
        result = answer_with_qwen(
            question=question,
            role="student",
            include_expired=include_expired,
        )
    except Exception as exc:
        print("qwen_skipped_or_failed:", exc)
        return

    print(result["answer"])
    print("citations:", result["citations"])
    print("warnings:", result["warnings"])


build_chroma_store()

run_case(QUESTIONS[0])
run_case(QUESTIONS[1])
run_case(QUESTIONS[2], include_expired=True)
```

运行本地 Qwen：

```bash
ollama ps
export QWEN_MODEL="qwen3.6:35b-a3b"
python run_real_llm_rag.py
```

如需使用 Dense 对照模型：

```bash
export QWEN_MODEL="qwen3.6:27b"
python run_real_llm_rag.py
```

如果本地模型运行失败，优先检查 `ollama ps`、`ollama list`、模型名称、内存占用和上下文长度。

### 真实场景观察任务

使用同一套原神 RAG 数据库，让本地 Qwen 回答前面的问题，观察以下现象：

| 观察项 | 记录方式 |
| :-- | :-- |
| 是否严格依据资料 | 回答中是否出现资料库没有的角色、版本、活动或玩法细节 |
| 是否保留引用 | 是否包含 `[chunk_id]`，引用是否能对应检索结果 |
| 权限是否生效 | `student` 角色回答中是否避开教师私有资料 |
| 冲突处理 | 包含旧资料时，是否提示不能直接给出唯一结论 |
| 回答质量 | 是否能把原石、祈愿、角色养成、树脂建议等资料综合成自然回答 |
| 成本与性能 | 记录本地模型响应速度、内存占用、失败原因和重试次数 |

真实 RAG 演练的重点不是让模型自由发挥，而是观察：当检索上下文、提示词和治理规则都由工程代码控制时，本地 Qwen 是否能够稳定地依据资料作答、保留引用，并在资料冲突时遵守告警。

## 第十二阶段：过期文档识别与冲突内容提示

### 目标

RAG 系统很容易把旧资料也检索出来。如果旧资料与新资料表达不同，系统不能假装没有冲突。工程系统至少应做到两件事：

1. 标记资料是否过期。
2. 检测同一主题下是否出现不同结论，并提示人工确认。

创建 `run_freshness_conflict.py`：

```python
from governed_rag import answer_with_governance


print("=" * 80)
print("只检索未过期资料")
fresh = answer_with_governance(
    "原粹树脂应该优先做什么？",
    role="student",
    include_expired=False,
)
print(fresh["answer"])
print("warnings:", fresh["warnings"])

print("=" * 80)
print("包含过期资料，用于观察冲突提示")
with_old = answer_with_governance(
    "原粹树脂应该优先做什么？",
    role="student",
    include_expired=True,
)
print(with_old["answer"])
print("warnings:", with_old["warnings"])
```

预期现象：

1. `include_expired=False` 时，只应使用当前教学模拟资料。
2. `include_expired=True` 时，系统可能同时检索到“秘境优先”和“地脉优先”两种建议。
3. 如果出现冲突，回答中应明确提示：资料存在版本差异，不能直接给出唯一结论，应优先参考未过期资料或交由人工确认。

### 工程检查清单

完成进阶部分后，同学们可以用下面的清单自查：

| 能力 | 检查问题 |
| :-- | :-- |
| 向量数据库 | `index/vector_store.json` 是否同时保存了文本、向量和元数据？ |
| 真实向量数据库 | `index/chroma_db/` 是否完成持久化写入，ChromaDB 查询是否返回了带元数据的结果？ |
| 真实大模型接入 | 同一套 RAG 上下文是否能交给本地 Qwen 生成回答？ |
| 引用来源 | 回答中是否返回了 `chunk_id`、标题、来源文件、更新时间和相似度？ |
| 权限控制 | `student` 是否无法检索教师私有资料？ |
| 多文档综合 | 一个问题是否能召回并综合多个文档片段？ |
| 过期识别 | 过期资料是否被默认过滤，或至少被明确标记？ |
| 冲突提示 | 同一 `claim_key` 出现不同 `claim_value` 时是否给出警告？ |
| 资料外拒答 | 无相关资料时是否返回 `grounded=False`？ |

## 故障排除 FAQ

### Q1: 为什么先用 JSON 实现向量数据库？

**A:** 本实验目标是理解向量数据库在 RAG 中保存“向量、文本和元数据”的作用。小规模原神主题资料使用 JSON 文件即可观察核心流程；真实项目可以替换为 ChromaDB、FAISS、Milvus 或云端向量库。

### Q2: 为什么还要使用 ChromaDB？

**A:** JSON 版本便于理解原理，但它不是工业基础设施。ChromaDB 提供真实的集合、持久化、向量写入、相似度查询和元数据过滤接口，能帮助同学们理解生产 RAG 系统中向量数据库的位置。

### Q3: 检索结果不准怎么办？

**A:** 优先检查切分粒度和关键词覆盖。简化词袋模型对中文语义理解有限，可以通过扩展关键词或接入 Embedding 模型改进。

### Q4: 为什么要拒答？

**A:** RAG 的可靠性不仅体现在答对资料内问题，也体现在不编造资料外答案。

### Q5: Top-K 应该设置多大？

**A:** 小资料集可设置 2-3。过小容易漏召回，过大容易引入噪声。

### Q6: 是否必须安装 `sentence-transformers`？

**A:** 不是。标准库版本即可完成核心实验。增强版本适合有余力的同学。

### Q7: 权限控制为什么不能只写进提示词？

**A:** 因为模型看到资料后就可能复述或泄露内容。权限控制必须在检索阶段完成，未授权资料不应进入上下文。

### Q8: 检测到冲突内容后应该怎么办？

**A:** 不要强行合并成一个确定结论。应提示资料存在版本差异，展示冲突来源，并优先参考未过期或权威来源。

### Q9: 本地 Qwen 跑不动怎么办？

**A:** 可以减少 `top_k`、缩短问题和上下文，或切换到更小的量化模型。如果仍然无法运行，应先保留 ChromaDB 检索、引用、权限、过期和冲突提示结果，确认 RAG 检索链路本身正确。

### Q10: 为什么不用模型自己去检索资料？

**A:** 本实验训练的是可控 RAG 工程链路。检索、权限、过期和冲突判断应由工程代码完成，模型只负责根据已经筛选好的上下文组织回答。这样系统更容易审计和排查问题。

## 参考资源

- RAG 概念介绍：https://www.promptingguide.ai/techniques/rag
- sentence-transformers：https://www.sbert.net/
- ChromaDB：https://docs.trychroma.com/
- FAISS：https://faiss.ai/
