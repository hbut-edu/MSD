# 《现代软件开发技术》上机实验手册：传统 SaaS 到 AI Agent (MCP) 全景实战

## 实验主题

传统 SaaS 到 AI Agent (MCP) 全景实战

## 实验目标

1. 理解传统 SaaS 架构与 AI Agent 架构的核心差异
2. 掌握 Dense 与 MoE 模型架构的特点和适用场景
3. 学会构建原子化业务工具库（Atomic Tools）
4. 掌握 MCP (Model Context Protocol) 工具定义规范，理解它与普通函数调用的区别
5. 理解 Agent 核心调度器的工作原理
6. 学会实现多工具链式调用（Chain of Actions）
7. 掌握自然语言界面（LUI）的构建方法
8. 建立 AI 时代软件工程的新思维

## 📅 课程概览 (Total: 240 Mins)

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :--- | :--- | :--- | :--- |
| **0-30'** | **模块一：理论导入** | 理解 SaaS 与 Agent 架构差异，掌握 Dense vs MoE 架构特点。 | 理论讲授、架构图解 |
| **30-70'** | **模块二：环境准备与工具构建** | 完成 Ollama 本地部署，下载模型，构建原子化业务工具库。 | Ollama, Python, pip, 函数式编程 |
| **70-110'** | **模块三：SaaS 对照组实现** | 实现传统 SaaS 巨石架构控制器，理解硬编码局限性。 | 面向对象编程, 耦合设计 |
| **110-150'** | **模块四：MCP 工具定义与 Agent 调度器** | 掌握 MCP 工具 Schema，实现 Agent 核心调度器。 | JSON Schema, OpenAI API, 链式调用 |
| **150-190'** | **模块五：双轨对比 UI 与实验观察** | 构建对比实验 UI，观测 Dense 与 MoE 模型的表现差异。 | Gradio, 实验设计, 性能观测 |
| **190-240'** | **模块六：综合实战与结课** | 完成综合实验，建立 AI 时代软件工程新思维。 | 项目实战, 工程化思维 |

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
* **内存**：代码与 UI 部分建议 16GB 以上；本地运行 Qwen3.6 默认对照模型建议 32GB 以上
* **磁盘空间**：默认量化模型建议至少 60GB 可用空间；若下载 BF16 或多个量化版本，需要按下表额外预留
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
ollama version x.y.z
```
版本号以本机安装结果为准，能正常执行 `ollama ps` 即可继续后续步骤。

### 4. 下载模型
```bash
# 下载 qwen3.6:27b (Dense 模型，默认量化版本约 17GB)
ollama pull qwen3.6:27b

# 下载 qwen3.6:35b-a3b (MoE 模型，默认量化版本约 24GB，以 Ollama 页面实际显示为准)
ollama pull qwen3.6:35b-a3b

# 查看已下载的模型
ollama list
```

**预期输出：**
```
NAME              ID              SIZE      MODIFIED
qwen3.6:27b       ...             17 GB     2 minutes ago
qwen3.6:35b-a3b   ...             24 GB     1 minute ago
```

如果课堂机器无法同时下载两个模型，可以先下载 `qwen3.6:35b-a3b` 完成 Agent 编排主实验；Dense 与 MoE 的完整对照可由实验室演示机或教师提前准备的远程环境完成。

### 5. 模型量化与硬件选择

量化（Quantization）是把模型权重从 BF16/FP16 等高精度格式压缩到 8 bit、4 bit 或其他低位格式的技术。它能显著降低磁盘、内存和显存占用，但也可能带来轻微的准确率、格式稳定性或工具调用稳定性损失。本实验的目标不是追求最高跑分，而是让同学们在普通实验环境中稳定观察 SaaS 与 Agent 的架构差异，因此默认选择 Ollama 的 `q4_K_M` 量化版本。

下面的容量来自 Ollama Qwen3.6 模型标签页；内存/显存建议是课堂短上下文、单模型加载场景下的保守经验值。实际占用会随上下文长度、并发请求数、KV Cache 精度、GPU/CPU 混合加载策略变化而上升。

| 模型标签 | 架构 | 量化类型 | 模型文件大小 | 可尝试内存/统一内存 | 全 GPU 加载显存建议 | 选择建议 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `qwen3.6:27b` / `qwen3.6:27b-q4_K_M` | Dense | Q4_K_M | 约 17GB | 24GB 起，32GB 更稳 | 24GB 起 | Dense 对照组默认选择，质量与资源占用较均衡 |
| `qwen3.6:27b-nvfp4` | Dense | NVFP4 | 约 20GB | 32GB 起 | 24GB 起 | 有较新 NVIDIA/支持 FP4 路径时可尝试；课堂不强制 |
| `qwen3.6:27b-q8_0` | Dense | Q8_0 | 约 30GB | 48GB 起 | 40GB 到 48GB | 更高精度，适合教师演示机或高配工作站 |
| `qwen3.6:27b-mxfp8` | Dense | MXFP8 | 约 31GB | 48GB 起 | 40GB 到 48GB | 适合对 FP8 路径感兴趣的硬件实验，不作为默认要求 |
| `qwen3.6:27b-bf16` | Dense | BF16 | 约 56GB | 64GB 起，96GB 更稳 | 80GB 或多卡 | 质量损失最小，但资源成本高，不建议普通课堂机器下载 |
| `qwen3.6:35b-a3b` / `qwen3.6:35b-a3b-q4_K_M` | MoE | Q4_K_M | 约 24GB | 32GB 起，48GB 更稳 | 32GB 起 | 本实验 Agent 编排默认推荐；多步工具调用观察更明显 |
| `qwen3.6:35b-a3b-nvfp4` | MoE | NVFP4 | 约 22GB | 32GB 起，48GB 更稳 | 32GB 起 | 文件略小，但硬件与运行栈适配性需现场验证 |
| `qwen3.6:35b-a3b-q8_0` | MoE | Q8_0 | 约 39GB | 64GB 起 | 48GB 起 | 更高精度的 MoE 对照，适合高配机器 |
| `qwen3.6:35b-a3b-mxfp8` | MoE | MXFP8 | 约 38GB | 64GB 起 | 48GB 起 | 可用于观察 FP8 与 Q4 的质量/速度差异 |
| `qwen3.6:35b-a3b-bf16` | MoE | BF16 | 约 71GB | 96GB 起，128GB 更稳 | 80GB 或多卡 | 只建议教师演示或专门硬件实验使用 |

同学们选择模型时可以按以下原则判断：

1. **普通笔记本或 32GB 统一内存机器**：优先使用 `qwen3.6:35b-a3b`，只下载一个模型完成主实验；如需 Dense 对照，再由实验室机器统一演示。
2. **24GB 显存 GPU 或 48GB 统一内存机器**：可同时准备 `qwen3.6:27b` 与 `qwen3.6:35b-a3b`，完成 Dense/MoE 全量对比。
3. **64GB 以上内存或高配工作站**：可尝试 `q8_0` 或 `mxfp8`，观察更高精度量化是否减少工具参数错误。
4. **BF16 版本**：只有在磁盘、内存、显存都充足时再下载；它更适合做模型质量上限参考，不适合作为课堂统一要求。
5. **长上下文实验**：不要因为 Ollama 页面标注 256K context window 就直接拉满上下文。上下文越长，KV Cache 占用越高。课堂建议保持默认上下文或在 Modelfile 中设置 `PARAMETER num_ctx 4096` 到 `8192`。

运行后可以用下面的命令观察模型实际加载到了哪里：

```bash
ollama ps
```

`PROCESSOR` 一列显示 `100% GPU` 说明模型完全加载到显存；显示 `100% CPU` 说明完全使用系统内存；显示类似 `48%/52% CPU/GPU` 说明 Ollama 正在进行 CPU/GPU 混合加载。

### 6. 使用 U 盘共享模型并让 Ollama 识别

如果同学们通过 U 盘或移动硬盘共享模型，推荐优先共享 Ollama 的完整模型库目录，而不是只复制某一个大文件。Ollama 的模型库由 `blobs` 和 `manifests` 两部分组成：`blobs` 存放实际权重层，`manifests` 记录模型名、标签和层引用。只复制 `blobs` 时，`ollama list` 通常看不到模型。

#### 方式 A：共享完整 Ollama 模型库（推荐）

源机器先确认模型已经存在：

```bash
ollama list
```

默认模型库位置如下：

| 系统 | 默认模型库目录 |
| :--- | :--- |
| macOS | `~/.ollama/models` |
| Linux | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

将该目录下的 `blobs` 和 `manifests` 一起复制到 U 盘，例如复制成：

```text
QWEN_MODELS/
└── models/
    ├── blobs/
    └── manifests/
```

目标机器有两种配置方式：

**macOS：指定一个新的模型库目录**

```bash
mkdir -p "$HOME/ollama-models"
cp -R "/Volumes/QWEN_MODELS/models/." "$HOME/ollama-models/"
launchctl setenv OLLAMA_MODELS "$HOME/ollama-models"
```

然后退出并重新打开 Ollama，再运行：

```bash
ollama list
ollama run qwen3.6:35b-a3b "请用一句话说明你已成功加载。"
```

**Linux：给 Ollama 服务指定模型库目录**

```bash
sudo mkdir -p /data/ollama-models
sudo cp -R /media/$USER/QWEN_MODELS/models/. /data/ollama-models/
sudo chown -R ollama:ollama /data/ollama-models
sudo systemctl edit ollama.service
```

在打开的编辑器中添加：

```ini
[Service]
Environment="OLLAMA_MODELS=/data/ollama-models"
```

保存后重启服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
ollama list
```

**Windows：设置用户环境变量**

1. 将 U 盘中的 `models` 目录复制到本机，例如 `D:\ollama-models`，确保该目录下直接包含 `blobs` 和 `manifests`。
2. 退出任务栏中的 Ollama。
3. 打开“环境变量”，为当前用户新增或修改 `OLLAMA_MODELS`，值设为 `D:\ollama-models`。
4. 重新启动 Ollama，再运行 `ollama list` 验证。

如果只是临时实验，也可以把 U 盘路径直接设为 `OLLAMA_MODELS`，但不建议课堂长期这样做。U 盘读写速度慢，推理启动会明显变慢，拔出 U 盘后模型也会立即不可用。

#### 方式 B：只有 GGUF 文件时，用 Modelfile 导入

如果同学拿到的是单个 `.gguf` 文件，而不是 Ollama 的 `models/blobs + models/manifests` 目录，Ollama 不会自动把它识别成 `qwen3.6:35b-a3b` 这类模型名。此时需要创建一个 `Modelfile`：

```text
FROM /Volumes/QWEN_MODELS/Qwen3.6-35B-A3B-Q4_K_M.gguf
PARAMETER num_ctx 4096
```

然后执行：

```bash
ollama create qwen3.6-local:35b-a3b-q4 -f Modelfile
ollama run qwen3.6-local:35b-a3b-q4 "你好，请确认模型已导入。"
```

Windows 路径示例：

```text
FROM D:\QWEN_MODELS\Qwen3.6-35B-A3B-Q4_K_M.gguf
PARAMETER num_ctx 4096
```

导入完成后，`ollama list` 中会出现新名字 `qwen3.6-local:35b-a3b-q4`。注意这类自定义名称与本手册代码里的下拉选项不同；如果使用自定义模型名，需要同步修改 `model_selector` 的 `choices`。

#### 常见识别失败原因

1. `OLLAMA_MODELS` 指到了错误层级：它应该指向直接包含 `blobs` 和 `manifests` 的目录。
2. 只复制了 `blobs`，没有复制 `manifests`，导致 `ollama list` 看不到模型。
3. Linux 服务用户没有权限读取模型目录，需要执行 `sudo chown -R ollama:ollama <目录>`。
4. 设置环境变量后没有重启 Ollama。
5. GGUF 文件不是 Ollama 官方模型库格式，需要用 `ollama create` 导入。
6. 共享模型前应确认模型许可证允许课堂内分发；不确定时，请让任课教师或助教统一提供模型。

### 7. 测试本地模型
```bash
# 测试 qwen3.6:27b
ollama run qwen3.6:27b "你好，请用一句话介绍自己。"

# 测试 qwen3.6:35b-a3b
ollama run qwen3.6:35b-a3b "你好，请用一句话介绍自己。"
```

### 8. 创建并验证 Conda Python 环境

本实验所有 Python 代码和依赖安装都必须在独立 Conda 环境中完成，避免污染系统 Python 或其他课程环境。

```bash
# 创建课程专用环境
conda create -y -n msd-agent-mcp python=3.10

# 激活环境
conda activate msd-agent-mcp

# 检查 Python 版本
python --version

# 检查 pip 版本
python -m pip --version
```

**预期输出：**
```
Python 3.10.x
pip x.x.x from .../envs/msd-agent-mcp/... (python 3.10)
```

### 9. 安装依赖
```bash
# 确认当前处于 Conda 环境
conda activate msd-agent-mcp

# 安装项目依赖
python -m pip install gradio openai requests

# 验证安装
python -c "import gradio, openai, requests; print('gradio', gradio.__version__); print('openai', openai.__version__); print('requests', requests.__version__)"
```

**预期输出：**
```
gradio 6.x.x
openai 2.x.x
requests 2.x.x
```

### 10. 验证 Ollama API 连接
```python
from openai import OpenAI

# 初始化 Ollama 客户端。
# Ollama 本地服务默认监听 11434 端口，并在 /v1 路径上兼容 OpenAI Chat Completions API。
# api_key 对本地 Ollama 不做真实鉴权，但 OpenAI SDK 要求必须提供一个字符串。
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='local',
    timeout=120
)

# 测试连接。
# 这里选择 qwen3.6:35b-a3b，是因为本实验主线以 MoE 模型完成 Agent 编排。
# max_tokens 设置较小，避免环境验证阶段生成太久。
try:
    response = client.chat.completions.create(
        model="qwen3.6:35b-a3b",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ Ollama API 连接成功")
    print(f"模型回复: {response.choices[0].message.content}")
except Exception as e:
    # 连接失败时通常是 Ollama 服务未启动、模型未下载、端口被占用或内存不足。
    print(f"❌ Ollama API 连接失败: {e}")
```

**预期输出：**
```
✅ Ollama API 连接成功
模型回复: Hello! How can I help you today?
```

### 11. 本地代码验证要求

任课教师或助教发布本实验材料前，应在 Conda 环境中运行附件中的验证脚本，确认本文档里的 Python 代码块可以被抽取、拼装并执行：

```bash
conda activate msd-agent-mcp
python "附件/verify_instruction_code.py"
```

如果本机已经下载 `qwen3.6:35b-a3b`，还需要额外运行真实 Ollama API 验证：

```bash
conda activate msd-agent-mcp
python "附件/verify_instruction_code.py" --live-ollama
```

第一条命令会验证工具函数、SaaS 控制器、Gradio 应用构建、文档中的单元测试、集成测试和性能测试示例；第二条命令会实际调用本地 Ollama 的 OpenAI 兼容接口。若任一命令失败，应先修正文档代码，再发布给同学们。

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

### 3. MCP 入门：从“函数能调用”到“模型能理解”

普通 Python 函数只对程序员可见，例如 `calculate_salary(data)`。模型并不知道这个函数存在，也不知道参数应如何填写。MCP 风格的工具定义要解决的是“让模型看到能力边界”的问题。

一个合格的 MCP 工具说明通常包含四类信息：

| 组成部分 | 作用 | 示例 |
| :-- | :-- | :-- |
| `name` | 告诉模型工具叫什么 | `calculate_salary` |
| `description` | 告诉模型什么时候应该调用 | `根据员工职级计算应发工资、扣税和实发工资` |
| `parameters` | 告诉模型参数结构和类型 | `employees: array` |
| `required` | 告诉模型哪些字段不能缺失 | `["employees"]` |

同学们在本实验中需要特别观察：**MCP 不是让模型直接执行代码，而是让模型先提出结构化工具调用请求，再由工程系统负责校验、路由和执行。**

可以把 MCP 工具调用理解为三步：

1. **能力声明**：开发者用 Schema 描述工具。
2. **调用规划**：模型根据用户意图选择工具并填参数。
3. **工程执行**：程序解析工具名和参数，调用真实函数，并把 Observation 回注给模型。

这个过程也是后续 Skill、Harness 和 AgentOps 的基础：Skill 封装可复用能力，MCP 描述能力接口，Harness 负责限制能力边界，AgentOps 负责部署、路由和观测。

---

## 第二部分：Dense 模型与 MoE 模型的对比实验设计

在多工具编排（如：查数据 -> 算工资 -> 导出文件）这种长上下文、高逻辑依赖的场景中，基座模型的能力决定了 Agent 的上限。本实验特别设计了针对两种不同架构大模型的对比观察：

### 1. 稠密模型 (Dense Model)：以 `qwen3.6:27b` 为代表
*   **架构特点**：每次推理时，模型的全部参数（约 278 亿）都会被激活并参与计算，部署路径相对直接，不需要 MoE 专家路由。
*   **实验观察预期**：Qwen3.6 的 Dense 模型相比上一代小参数模型在代码理解、工具调用和上下文保持上更强，适合观察“参数全部参与推理”的稳定性与资源开销。但在连续多步工具调用（Chain of Actions）中，同学们仍需关注它是否会出现参数提取遗漏、格式幻觉，或者在执行到第三步时弱化第一步获取的数据。

### 2. 混合专家模型 (MoE Model)：以 `qwen3.6:35b-a3b` 为代表
*   **架构特点**：总参数量约 360 亿，但在每次推理时只动态激活约 30 亿参数的专家网络（Sparse Activation），因此能在较大总容量和较低单次激活成本之间取得平衡。
*   **实验观察预期**：MoE 架构更适合观察复杂任务路由和逻辑分发。在多步链式推理中，同学们重点记录它是否能稳定维持“思考 -> 行动 -> 观察”的循环，并将上一个工具的输出 JSON 转换为下一个工具的输入参数，从而降低逻辑断链的概率。

---

## 第三部分：实战演练 —— 循序渐进的代码实现

本环节将实现一个真实的财务业务流：**查询员工名单 -> 计算工资与五险一金 -> 导出 CSV 文件**。
本实验将代码拆分为 6 个阶段，同学们可按顺序将其拼接为一个完整的 `app.py` 并运行。

### 阶段 1：环境初始化与底层数据构建
无论是传统软件还是 AI 智能体，底层的数据资产是永恒不变的。

```python
# ==================== 依赖导入 ====================
# gradio 负责构建本地 Web UI；json/csv/tempfile 负责工具之间的数据交换和文件导出；
# logging 用于记录 Agent 每一轮决策，OpenAI SDK 用于调用 Ollama 的兼容接口。
import gradio as gr
import json
import os
import time
import csv
import tempfile
import logging
from datetime import datetime
from openai import OpenAI

# ==================== 日志配置 ====================
# 日志同时写入文件和终端：
# - 文件日志便于课后复盘 Agent 的工具调用链；
# - 终端日志便于课堂实时观察模型是否按预期规划。
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 初始化 Ollama 客户端 ====================
# Ollama 暴露 OpenAI 兼容接口，因此可以复用 OpenAI SDK。
# timeout=120 用于给本地大模型留出加载和首轮推理时间。
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

# ==================== 模拟底层数据 ====================
# 为了让实验可离线、可复现，这里不用真实数据库，而是用内存列表模拟员工花名册。
# 每条员工记录只保留 Agent 工具链所需的最小字段：id、name、level。
mock_employees = [
    {"id": "E01", "name": "张三", "level": "L1"},
    {"id": "E02", "name": "李四", "level": "L2"},
    {"id": "E03", "name": "王五", "level": "L3"}
]

# 职级到基础工资的映射表，后续工资计算工具会根据 level 查表。
mock_salary_levels = {"L1": 10000, "L2": 20000, "L3": 35000}
```

### 阶段 2：构建原子化业务工具库 (Atomic Tools)
将庞大的业务逻辑解构为纯粹的、无 UI 耦合的 Python 函数。这些就是未来挂载到 MCP 上的核心资产。

```python
# 工具 A：仅负责查询全量员工基础数据
def get_employee_directory():
    """返回全公司员工的花名册 JSON。

    该函数模拟企业 HR 系统中的“员工目录服务”。
    Agent 调用它不需要任何参数，因此它通常是工具链第一步。
    """
    try:
        # 即使模拟数据为空，也返回 JSON 错误对象，避免上层拿到 None。
        if not mock_employees:
            return json.dumps({"error": "员工数据为空"}, ensure_ascii=False)

        # ensure_ascii=False 可以保留中文姓名，方便前端和日志直接阅读。
        return json.dumps(mock_employees, ensure_ascii=False)
    except Exception as e:
        # 工具函数统一返回 JSON 字符串，让模型可以把错误当作上下文继续处理。
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

# 工具 B：仅负责算薪与扣税 (不关心数据从哪来，只负责处理传入的 JSON)
def calculate_payroll_and_tax(employees_json: str):
    """接收员工 JSON，计算五险一金、个税和实发工资。"""
    try:
        # 模型生成的参数不可信，先检查空值，避免 json.loads 抛出难懂错误。
        if not employees_json or not employees_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            # 将上一个工具返回的 JSON 字符串恢复为 Python 列表。
            employees = json.loads(employees_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        # 本工具只接受员工数组；如果模型传入对象或普通文本，应明确拒绝。
        if not isinstance(employees, list):
            return json.dumps({"error": "输入数据格式错误，应为数组"}, ensure_ascii=False)
        
        if len(employees) == 0:
            return json.dumps({"error": "员工列表为空"}, ensure_ascii=False)
        
        results = []
        for emp in employees:
            # 容错：列表中如果混入非字典数据，跳过该项，避免整批失败。
            if not isinstance(emp, dict):
                continue

            # level 是计算工资的关键字段，缺失时保留该员工记录并追加错误说明。
            if "level" not in emp:
                emp_result = emp.copy()
                emp_result["error"] = "缺少 level 字段"
                results.append(emp_result)
                continue
            
            # 根据职级查基础工资。未知职级返回 0，并被视为业务错误。
            base_salary = mock_salary_levels.get(emp["level"], 0)
            if base_salary <= 0:
                emp_result = emp.copy()
                emp_result["error"] = f"无效的职级: {emp.get('level')}"
                results.append(emp_result)
                continue
            
            # 简化版薪酬规则：
            # - 五险一金按基础工资 20% 计算；
            # - 个税按扣除五险一金后的 5% 计算；
            # - 实发工资 = 基础工资 - 五险一金 - 个税。
            social_security = base_salary * 0.20
            tax = max(0, (base_salary - social_security) * 0.05)
            net_salary = base_salary - social_security - tax
            
            # 在原始员工信息上追加工资字段，方便导出和前端展示。
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
        # 所有未预期异常也转为 JSON，保持工具协议稳定。
        return json.dumps({"error": f"计算失败: {str(e)}"}, ensure_ascii=False)

# 工具 C：仅负责将传入的 JSON 写成物理 CSV 文件
def export_payroll_csv(payroll_json: str):
    """接收算好工资的 JSON，生成 CSV 文件并返回系统路径。"""
    try:
        # CSV 导出工具同样要先检查模型传入的参数是否为空。
        if not payroll_json or not payroll_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        
        try:
            # 将工资 JSON 转成 Python 列表，供 csv.DictWriter 写入。
            payroll_data = json.loads(payroll_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        
        # 至少需要一条记录才能确定 CSV 表头。
        if not isinstance(payroll_data, list) or len(payroll_data) == 0:
            return json.dumps({"error": "工资数据为空或格式错误"}, ensure_ascii=False)
        
        # 使用系统临时目录，避免同学需要提前创建输出文件夹。
        filepath = os.path.join(tempfile.gettempdir(), "payroll_report.csv")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # 以第一条工资记录的字段作为表头，要求上游工具保持字段一致。
                writer = csv.DictWriter(f, fieldnames=payroll_data[0].keys())
                writer.writeheader()
                writer.writerows(payroll_data)
        except IOError as e:
            return json.dumps({"error": f"文件写入失败: {str(e)}"}, ensure_ascii=False)
            
        return json.dumps({"status": "success", "file_path": filepath, "record_count": len(payroll_data)}, ensure_ascii=False)
    except Exception as e:
        # 文件权限、磁盘空间等异常也以 JSON 形式返回给 Agent。
        return json.dumps({"error": f"导出失败: {str(e)}"}, ensure_ascii=False)
```

### 阶段 3：构建 SaaS 对照组 (巨石控制器)
展示传统开发的"硬编码"特性：开发者必须规定死输入输出格式，一旦需求变更（例如用户不想导出文件），这套流水线就失效了。

```python
def saas_generate_payroll_api():
    """传统 SaaS 后端接口：硬编码的流水线，高度耦合。

    传统 SaaS 的特点是“程序员先规定流程，用户只能按流程操作”。
    本函数把查询、计算、导出三个步骤固定串在一起，作为 Agent 方案的对照组。
    """
    try:
        # 模拟系统耗时，方便同学在前端观察按钮触发后的处理过程。
        time.sleep(1)
        
        # 步骤 1：查询员工目录。这里用 error 字段做简化错误判断。
        emp_str = get_employee_directory()
        if "error" in emp_str:
            raise Exception(emp_str)

        # 步骤 2：工资计算。控制器必须显式知道第二步调用哪个函数。
        payroll_str = calculate_payroll_and_tax(emp_str)
        if "error" in payroll_str:
            raise Exception(payroll_str)

        # 步骤 3：导出 CSV。即使用户只想看结果，传统流程也会按代码固定执行。
        export_result = json.loads(export_payroll_csv(payroll_str))
        if "error" in export_result:
            raise Exception(export_result["error"])
        
        # Gradio Dataframe 需要二维数组，因此要把 JSON 对象转成表格行。
        payroll_data = json.loads(payroll_str)
        table_data = [[d["name"], d["level"], d["应发工资"], d["五险一金扣除"], d["实发工资"]] for d in payroll_data]
        
        # 严格返回两个输出：第一个给表格，第二个给文件下载组件。
        return table_data, export_result.get("file_path")
    except Exception as e:
        # 失败时也返回 Dataframe 可显示的二维数组，避免前端组件类型不匹配。
        print(f"❌ SaaS 执行失败: {e}")
        return [[str(e), "", "", "", ""]], None
```

**📊 预期结果：**
执行成功后，将在表格中显示所有员工的工资信息，并生成 CSV 文件。

### 阶段 4：构建 Agent 的"神经接口" (MCP Schema)
这是大模型操控软件的唯一媒介。大模型依靠这段 JSON Schema 动态了解系统的能力边界。

```python
# MCP 风格的工具说明书：告诉大模型“有哪些工具、什么时候用、参数怎么填”。
# 需要注意：模型只看到 Schema，不会直接看到或执行 Python 函数体。
tools_schema = [
    {
        # 每个工具都以 function 形式暴露给模型。
        "type": "function",
        "function": {
            # name 必须和后续 Python 路由中的函数名完全一致。
            "name": "get_employee_directory",
            # description 会直接影响模型是否选择这个工具，应写清楚调用时机。
            "description": "第一步：获取全公司所有员工的基础数据（包含姓名和职级）。不需要参数。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_payroll_and_tax",
            "description": "第二步：接收员工基础数据 JSON，计算实发工资。必须在获取员工名单后调用。",
            "parameters": {
                # JSON Schema 的 object 表示该工具需要接收命名参数。
                "type": "object",
                "properties": {
                    # employees_json 的描述告诉模型：这个参数应来自上一个工具的输出。
                    "employees_json": {"type": "string", "description": "由 get_employee_directory 返回的 JSON 数据"}
                },
                # required 可以减少模型漏填关键参数的概率。
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
                    # payroll_json 必须接收已经计算后的工资明细，而不是原始员工目录。
                    "payroll_json": {"type": "string", "description": "由 calculate_payroll_and_tax 返回的工资 JSON"}
                },
                "required": ["payroll_json"]
            }
        }
    }
]
```

### 阶段 5：Agent 核心调度器 (链式推理中枢)
本段代码是现代 AI 软件工程的灵魂所在。代码通过 `while True` 循环，赋予了大模型**"反思与继续执行"**的能力，让它能在 Dense 和 MoE 架构下展现真正的规划水平。

```python
def agent_orchestrator(user_message, history, messages_state, selected_model):
    """
    Agent 的大脑调度器。接收用户指令，并根据选择的模型（qwen3.6:27b 或 qwen3.6:35b-a3b）进行推理。

    history 是 Gradio Chatbot 可见历史；messages_state 是真正发给模型的上下文。
    二者分开保存，是为了让前端展示更友好，同时保留 tool 消息给模型继续推理。
    """
    # Gradio 首次调用时可能传入 None，这里统一转为空列表，避免后续 append 报错。
    history = history or []
    messages_state = messages_state or []

    try:
        logger.info(f"开始处理用户请求: {user_message}, 模型: {selected_model}")
        
        # 1. 严格的 System Prompt，框定 Agent 行为规范。
        # 只在新会话第一次初始化，避免每轮重复追加 system 消息。
        if not messages_state:
            messages_state = [{"role": "system", "content": "你是专业的 HR 助手。请自动规划工具调用链完成计算。输出最终结果时，请用 Markdown 表格展示，并附上文件下载路径。"}]
            logger.info("初始化系统提示词")
        
        # 将用户自然语言写入模型上下文；同时构造前端可见的“正在规划”提示。
        messages_state.append({"role": "user", "content": user_message})
        history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": f"🤖 [当前引擎: {selected_model}] 正在规划任务流..."}
        ]
        yield history, messages_state
        
        # 2. 开启多轮循环：这是实现多工具接力 (Chain of Actions) 的核心机制。
        # max_iterations 是安全阀，避免模型不断调用工具导致无限循环。
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始迭代 {iteration}/{max_iterations}")
            
            try:
                # 向所选模型发起请求，赋予其 tool_choice="auto" 的自主权。
                # 模型可以选择直接回答，也可以选择调用 tools_schema 中声明的工具。
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
                # 如果出现 tool_calls，说明模型还需要程序执行真实业务函数。
                if response_msg.tool_calls:
                    logger.info(f"模型请求调用 {len(response_msg.tool_calls)} 个工具")
                    
                    for tool_call in response_msg.tool_calls:
                        func_name = tool_call.function.name
                        logger.info(f"准备调用工具: {func_name}")
                        
                        # 解析模型推理出的参数。
                        # tool_call.function.arguments 是 JSON 字符串，不是 Python 字典。
                        try:
                            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            logger.info(f"工具参数: {func_args}")
                        except json.JSONDecodeError as e:
                            # 参数解析失败时使用空参数进入工具逻辑，让工具返回结构化错误。
                            logger.warning(f"工具参数解析失败: {e}")
                            func_args = {}
                        
                        # 在前端流式打印当前的执行进度
                        history[-1]["content"] += f"\n\n> 🛠️ **触发节点**: `{func_name}`"
                        yield history, messages_state
                        
                        # 4. 动态路由：实际执行本地 Python 业务代码。
                        # 模型只负责“选择工具和填写参数”，真正的权限边界仍由工程代码控制。
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
                        
                        # 5. 上下文回注：将物理世界的真实执行结果，作为 Context 塞回给大模型。
                        # role=tool 和 tool_call_id 必须保留，否则模型无法知道该结果对应哪个工具调用。
                        messages_state.append({
                            "role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": tool_result
                        })
                        logger.info(f"工具结果已回注到上下文")
                    
                    # 【重点】遇到 continue 意味着当前循环不退出。
                    # 模型会带着刚才的工具结果进入下一轮判断，决定是否继续调用下一个工具。
                    logger.info("继续下一轮迭代")
                    continue 

                else:
                    # 6. 出口条件：当大模型认为所有工具调用完毕，它会输出自然语言总结，此时退出循环。
                    final_text = response_msg.content or "任务已完成，但模型没有返回文本结果。"
                    logger.info(f"模型输出最终结果: {final_text[:100]}...")
                    
                    messages_state.append({"role": "assistant", "content": final_text})
                    history[-1] = {"role": "assistant", "content": final_text}
                    yield history, messages_state
                    break 
                    
            except Exception as e:
                # 单轮推理失败时不清空上下文，保留日志和前端状态用于课堂排错。
                logger.error(f"迭代 {iteration} 执行失败: {str(e)}", exc_info=True)
                error_msg = f"❌ 迭代 {iteration} 执行失败: {str(e)}"
                history[-1]["content"] += f"\n\n{error_msg}"
                yield history, messages_state
                break
                
        if iteration >= max_iterations:
            # 达到轮次上限通常意味着模型没有形成终止判断，是 Agent 系统常见风险。
            logger.warning(f"已达到最大迭代次数 {max_iterations}，任务可能未完成")
            history[-1]["content"] += "\n\n⚠️ 已达到最大迭代次数，任务可能未完成"
            yield history, messages_state
            
        logger.info(f"用户请求处理完成，总迭代次数: {iteration}")
            
    except Exception as e:
        # 外层兜底覆盖初始化、参数类型、前端状态等非单轮模型调用错误。
        logger.error(f"Agent 调度器执行失败: {str(e)}", exc_info=True)
        error_msg = f"❌ Agent 调度器执行失败: {str(e)}"
        history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": error_msg}
        ]
        yield history, messages_state
```

**📊 预期结果：**
- **qwen3.6:27b (Dense)**：在简单单步调用和代码理解任务中表现更强，但仍需要观察多步链式调用中的参数传递、上下文保持和格式稳定性
- **qwen3.6:35b-a3b (MoE)**：在多步链式调用中通常更稳定，适合观察专家路由对复杂任务分发和上下文维护的帮助

**💡 思考问题：**
* 为什么 MoE 模型在多步调用中表现更稳定？
* Dense 模型在什么情况下会出现逻辑断链？
* 如何提高 Agent 的执行稳定性？

### 阶段 6：双轨对比前端与实验 UI 组装
构建交互界面，将静态的 SaaS 流水线与动态的 Agent 编排并排展示，并提供模型架构的切换开关。

```python
# 使用 Gradio 构建现代且极简的 Web UI
with gr.Blocks() as demo:
    # 页面标题说明本实验的双轨对比主题。
    gr.Markdown("## 💸 现代软件架构实验：SaaS 巨石架构 vs Agent 动态编排")
    
    with gr.Row():
        # ================= 控制组：传统 SaaS 面板 =================
        with gr.Column(scale=1):
            # 左侧展示传统“按钮触发固定后端流程”的产品形态。
            gr.Markdown("### 🏢 控制组：SaaS (硬编码)")
            gr.Markdown("> 极度高效，但极度死板。开发者提前锁死了业务流。")
            
            # 三个输出组件分别承接：触发按钮、工资表格、导出的 CSV 文件。
            saas_btn = gr.Button("🚀 一键执行：生成工资单并下载", variant="primary")
            saas_table = gr.Dataframe(headers=["姓名", "职级", "应发", "五险一金", "实发"])
            saas_file = gr.File(label="导出的物理文件")
            
            # 事件绑定：点击按钮即触发巨石函数
            saas_btn.click(fn=saas_generate_payroll_api, inputs=None, outputs=[saas_table, saas_file])
            
        # ================= 实验组：AI Agent 面板 =================
        with gr.Column(scale=1):
            # 右侧展示自然语言驱动的 Agent 编排过程。
            gr.Markdown("### 🤖 实验组：Agent (意图驱动)")
            
            # 【实验核心变量控制】允许动态切换 Dense 和 MoE 模型进行观察
            model_selector = gr.Dropdown(
                choices=["qwen3.6:27b", "qwen3.6:35b-a3b"],
                value="qwen3.6:35b-a3b",
                label="🧪 核心变量：选择底层大模型架构 (Dense vs MoE)"
            )
            
            # messages_state 保存发给模型的完整上下文；chatbot 只负责前端可见展示。
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
    # Gradio 6 将 theme 参数放在 launch 阶段设置，这样运行时不会出现迁移警告。
    demo.launch(theme=gr.themes.Soft())
```

---

## 实验总结与教学启发

通过这份完整的代码实现，可以从工程视角得出以下结论：

1.  **架构维度的降维打击**：SaaS 时代的开发者在编写"功能"；而 Agent 时代的开发者在编写"能力边界"。当同学们在实验中输入"我不想导出文件，只看李四的工资"时，SaaS 只能全量跑完并报错，而 Agent 会自主阻断工具 C 的调用，展现出极高的**系统柔韧度**。
2.  **模型维度的深刻对比**：在切换 `qwen3.6:27b` (Dense) 和 `qwen3.6:35b-a3b` (MoE) 运行上述多步骤指令时，同学们可以直观观察到 Dense 与 MoE 在资源占用、上下文保持、工具参数传递和逻辑断链概率上的差异。Qwen3.6 的 Dense 模型已经具备较强的 Agentic Coding 能力，而 MoE 模型则更适合观察动态专家路由在复杂任务分发中的价值。

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
2. 下载模型：`ollama pull qwen3.6:27b` 或 `ollama pull qwen3.6:35b-a3b`
3. 确认模型名称拼写正确（使用冒号 `qwen3.6:27b`）
4. 如果模型来自 U 盘，确认 `OLLAMA_MODELS` 指向直接包含 `blobs` 和 `manifests` 的目录，并重启 Ollama

### 问题 3：复制模型后 `ollama list` 看不到
**症状**：U 盘已经复制了模型文件，但本机 Ollama 不显示模型
**解决方案**：
1. 确认复制的是完整 Ollama 模型库目录，而不是单独的 `sha256-*` 文件
2. 检查目录结构是否为 `<模型库>/blobs` 和 `<模型库>/manifests`
3. 设置或修正 `OLLAMA_MODELS` 后必须重启 Ollama
4. Linux 下检查目录权限：`sudo chown -R ollama:ollama <模型库目录>`
5. 如果手中只有 `.gguf` 文件，请使用 `ollama create <模型名> -f Modelfile` 导入

### 问题 4：内存不足
**症状**：模型加载失败或系统卡死
**解决方案**：
1. 关闭其他应用程序释放内存
2. 只加载一个模型，优先保证 `qwen3.6:35b-a3b` 或 `qwen3.6:27b` 中的一个能够稳定运行
3. 增加系统虚拟内存
4. 优先选择 `q4_K_M` 量化版本，避免在普通课堂机器上下载 BF16 版本

### 问题 5：Agent 执行中断
**症状**：Agent 在多步调用中出现逻辑断链
**解决方案**：
1. 切换到 MoE 模型（qwen3.6:35b-a3b）
2. 检查 System Prompt 是否清晰明确
3. 增加最大迭代次数限制
4. 优化工具描述，使其更清晰

### 问题 6：CSV 文件导出失败
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
ollama rm qwen3.6:27b
ollama rm qwen3.6:35b-a3b
```

### 5. 删除 Conda 实验环境（可选）
```bash
# 退出当前环境后删除课程专用环境
conda deactivate
conda env remove -n msd-agent-mcp
```

### 6. 卸载 Ollama（可选）
```bash
# Windows：通过控制面板卸载
# macOS：brew uninstall ollama
# Linux：根据安装方式选择相应的卸载方法
```

---

## 📝 课后延伸与测试建议

### 1. 核心收获

完成本次实验后，同学们应掌握以下关键知识：

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

在实验过程中，同学们可能观察到以下现象：

**SaaS 架构：**
- ✅ 执行效率高，响应速度快
- ❌ 灵活性差，难以应对变更需求
- ❌ 扩展性受限，新增功能需要全链路修改

**AI Agent 架构：**
- ✅ 灵活性强，能够理解自然语言意图
- ✅ 扩展性好，新增工具只需添加 Schema
- ❌ 执行效率相对较低，存在推理开销
- ❌ 对模型能力依赖较高

**Dense 模型（qwen3.6:27b）：**
- ✅ 单次调用表现良好
- ✅ 相比 MoE 对照模型部署路径更直接
- ❌ 本地运行仍有较高内存和磁盘要求
- ❌ 在长链式工具调用中仍需观察参数传递和上下文稳定性

**MoE 模型（qwen3.6:35b-a3b）：**
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
    """验证三个原子工具函数的输入输出协议是否稳定。"""

    def test_get_employee_directory(self):
        """员工目录工具应返回非空 JSON 数组，并包含后续计算所需字段。"""
        # 工具函数返回 JSON 字符串，因此测试先反序列化，再检查结构。
        result = get_employee_directory()
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
    
    def test_calculate_payroll_and_tax_with_valid_data(self):
        """有效员工数据应能计算出工资字段。"""
        # L1 是已知职级，测试可稳定验证成功路径。
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L1"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("应发工资", data[0])
        self.assertIn("实发工资", data[0])
    
    def test_calculate_payroll_and_tax_with_empty_data(self):
        """空输入应返回 error，而不是抛出未捕获异常。"""
        result = calculate_payroll_and_tax("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_invalid_json(self):
        """非法 JSON 应被工具捕获，避免 Agent 工具链中断。"""
        result = calculate_payroll_and_tax("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_export_payroll_csv_with_valid_data(self):
        """工资明细应能导出 CSV，并返回可供前端下载的文件路径。"""
        payroll_data = json.dumps([
            {"id": "E01", "name": "张三", "level": "L1", "应发工资": 10000, "实发工资": 8000}
        ])
        result = export_payroll_csv(payroll_data)
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("file_path", data)

if __name__ == "__main__":
    # 允许同学直接运行该文件观察测试结果。
    unittest.main()
```

### 2. Agent 调度器测试

```python
import unittest
from unittest.mock import Mock, patch
from your_app_file import agent_orchestrator

class TestAgentOrchestrator(unittest.TestCase):
    """验证 Agent 调度器在不真实调用 Ollama 的情况下仍可被单元测试覆盖。"""

    @patch("your_app_file.client")
    def test_agent_orchestrator_with_simple_query(self, mock_client):
        """当模型不请求工具时，调度器应直接把最终回答写入前端历史。"""
        # 构造一个假的模型响应，避免单元测试依赖本地模型和显存。
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "这是测试回复"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        
        history = []
        messages_state = []
        
        # agent_orchestrator 是生成器，必须迭代到最后一次 yield 才能拿到最终状态。
        for result in agent_orchestrator("测试问题", history, messages_state, "qwen3.6:27b"):
            updated_history, updated_messages = result
        
        self.assertEqual(len(updated_history), 2)
        self.assertEqual(updated_history[-1]["role"], "assistant")
        self.assertIn("测试回复", updated_history[-1]["content"])
    
    @patch("your_app_file.client")
    def test_agent_orchestrator_with_tool_call(self, mock_client):
        """当模型请求工具时，调度器应解析 tool_call 并把工具结果写回上下文。"""
        # 构造一个假的工具调用：模型选择 get_employee_directory，且不需要参数。
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
        
        # 这里不要求最终回答，只验证上下文已记录 system/user/tool 等消息。
        for result in agent_orchestrator("查询员工", history, messages_state, "qwen3.6:27b"):
            updated_history, updated_messages = result
        
        self.assertGreater(len(updated_messages), 0)

if __name__ == "__main__":
    # 允许独立运行该测试文件。
    unittest.main()
```

### 3. 集成测试

```python
import unittest
import subprocess
import sys
import time
import requests

class TestIntegration(unittest.TestCase):
    def test_gradio_launch(self):
        """启动完整 Gradio 应用，并检查 7860 端口是否返回 HTTP 200。"""
        # 使用 sys.executable 可以确保子进程仍运行在当前 Conda 环境中。
        process = subprocess.Popen([sys.executable, "your_app_file.py"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        # 给 Gradio 留出启动时间；真实机器较慢时可以适当调大。
        time.sleep(5)
        
        try:
            response = requests.get("http://localhost:7860")
            self.assertEqual(response.status_code, 200)
        finally:
            # 无论测试成功还是失败，都关闭子进程，避免端口被占用。
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
    """轻量性能测试，用于观察纯 Python 工具函数的本地执行开销。"""
    print("开始性能测试...")
    
    # 测试 get_employee_directory：该函数只读取内存模拟数据，理论上应非常快。
    start_time = time.time()
    for i in range(100):
        get_employee_directory()
    avg_time = (time.time() - start_time) / 100
    print(f"get_employee_directory 平均耗时: {avg_time:.4f} 秒")
    
    # 测试 calculate_payroll_and_tax：包含 JSON 解析和简单工资计算。
    employees = get_employee_directory()
    start_time = time.time()
    for i in range(100):
        calculate_payroll_and_tax(employees)
    avg_time = (time.time() - start_time) / 100
    print(f"calculate_payroll_and_tax 平均耗时: {avg_time:.4f} 秒")
    
    print("性能测试完成")

if __name__ == "__main__":
    # 直接运行时执行性能测试；它不是 unittest，而是课堂观察用脚本。
    test_performance()
```

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

## 📚 参考资源

### 官方文档
* **Ollama 官方文档**：https://github.com/ollama/ollama
* **Ollama FAQ（模型目录、环境变量、GPU 加载观察）**：https://docs.ollama.com/faq
* **Ollama 导入 GGUF 模型**：https://docs.ollama.com/import
* **Ollama Modelfile 参考**：https://docs.ollama.com/modelfile
* **Ollama Qwen3.6 标签列表**：https://ollama.com/library/qwen3.6/tags
* **Ollama Qwen3.6:27b**：https://ollama.com/library/qwen3.6:27b
* **Ollama Qwen3.6:35b-a3b**：https://ollama.com/library/qwen3.6:35b-a3b
* **OpenAI API 文档**：https://platform.openai.com/docs/
* **Gradio 文档**：https://www.gradio.app/docs
* **Qwen 模型**：https://github.com/QwenLM/Qwen
* **Qwen3.6-27B 发布说明**：https://qwen.ai/blog?id=qwen3.6-27b
* **Qwen3.6-35B-A3B 发布说明**：https://qwen.ai/blog?id=qwen3.6-35b-a3b

### 技术文章
* **AI Agent 架构设计**：https://lilianweng.github.io/posts/2023-06-23-agent/
* **MoE 模型详解**：https://arxiv.org/abs/2211.15841
* **MCP 协议规范**：https://modelcontextprotocol.io/

### 学习资源
* **AI Agent 实战课程**：https://www.deeplearning.ai/short-courses/multi-ai-agent-systems/
* **大模型应用开发**：https://www.coursera.org/learn/llm-application-development

---

## ❓ 常见问题 FAQ

### 环境配置相关

#### Q1: Ollama安装失败怎么办？
**A:** 
- 检查系统要求：Windows 10/11
- Windows用户：确认下载的是Windows版本安装包
- 查看Ollama官方文档：https://github.com/ollama/ollama
- 检查是否有杀毒软件阻止安装

#### Q2: Ollama服务启动失败？
**A:**
- Windows：检查任务管理器中是否有ollama.exe进程
- 检查端口11434是否被占用：`netstat -ano | findstr "11434"`
- 重启Ollama服务或重启电脑

#### Q3: 模型下载太慢或失败？
**A:**
- 检查网络连接稳定性
- 可以尝试使用代理或镜像源
- 先只下载一个模型测试，例如：`ollama pull qwen3.6:35b-a3b`
- 查看已下载的模型：`ollama list`
- 删除失败的下载重新开始：`ollama rm qwen3.6:35b-a3b`

#### Q4: 模型文件太大，磁盘空间不足？
**A:**
- 只下载需要的模型，不要下载所有模型
- 删除不需要的模型：`ollama rm <模型名>`
- `qwen3.6:27b` 默认量化版本约 17GB，`qwen3.6:35b-a3b` 默认量化版本约 24GB（以 Ollama 页面实际显示为准）
- 如果磁盘或内存不足，可以先只用 `qwen3.6:35b-a3b` 完成 Agent 编排主实验，并在报告中说明未完成 Dense/MoE 对照的原因
- 如果使用 U 盘共享模型，不要把 `OLLAMA_MODELS` 长期指向慢速 U 盘；建议复制到本机 SSD 后再运行

---

### Python环境相关

#### Q5: Python版本不兼容？
**A:**
- 确认已安装 Conda：`conda --version`
- 创建课程专用环境：`conda create -y -n msd-agent-mcp python=3.10`
- 激活环境后检查版本：`conda activate msd-agent-mcp`，再运行 `python --version`
- 确认 Python 路径位于 `envs/msd-agent-mcp` 目录中

#### Q6: Conda环境内依赖安装失败？
**A:**
- 先确认已经激活环境：`conda activate msd-agent-mcp`
- 使用清华源加速：`python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple gradio openai requests`
- 升级pip：`python -m pip install --upgrade pip`
- 检查网络连接
- 尝试逐个安装依赖包
- 查看错误信息，根据提示解决

#### Q7: 导入模块报错？
**A:**
- 确认当前处于 Conda 环境：`conda info --envs`
- 验证依赖：`python -c "import gradio, openai, requests; print('ok')"`
- 检查是否在正确的 Python 环境中：macOS/Linux 使用 `which python`，Windows 使用 `where python`
- 尝试重新安装：`python -m pip install --force-reinstall gradio openai requests`

---

### 代码运行相关

#### Q8: Ollama API连接失败？
**A:**
- 确认Ollama服务正在运行：`ollama ps`
- 检查API地址是否正确：`http://localhost:11434/v1`
- 确认api_key设置为'local'
- 尝试在浏览器访问：`http://localhost:11434`
- 检查防火墙设置

#### Q9: 模型调用超时？
**A:**
- 增加timeout参数：`timeout=120` 或更高
- 首次加载模型较慢，耐心等待
- 只加载一个模型，或改用任课教师指定的远程/实验室模型服务
- 关闭其他占用内存的程序
- 检查系统资源使用情况

#### Q10: Gradio应用无法启动？
**A:**
- 检查端口7860是否被占用
- 尝试更换端口：`demo.launch(server_port=7861)`
- 确认所有依赖都已安装
- 查看错误日志，根据提示修复
- 尝试在浏览器访问：`http://localhost:7860`

#### Q11: 代码运行报错？
**A:**
- 仔细阅读错误信息，定位问题
- 检查代码缩进是否正确（Python对缩进敏感）
- 确认所有函数都已正确定义
- 检查变量名拼写错误
- 逐步调试，先运行简单的测试

---

### Agent功能相关

#### Q12: 为什么我的 Agent 总是调用错误的工具？
**A:** 可能的原因和解决方案：
- 检查 System Prompt 是否清晰明确
- 优化工具描述（tools_schema），确保功能描述准确
- 检查参数定义是否完整和准确
- 尝试使用更适合多步工具调用的模型（如 `qwen3.6:35b-a3b`）

#### Q13: Agent不调用工具？
**A:**
- 检查tools_schema是否正确定义
- 确认tool_choice设置为"auto"
- 检查System Prompt是否正确
- 尝试使用更明确的用户指令
- 查看日志输出，了解Agent的思考过程

#### Q14: 工具调用参数错误？
**A:**
- 检查JSON Schema定义是否完整
- 确认required字段设置正确
- 查看Agent生成的参数内容
- 在代码中添加参数验证
- 添加异常处理和错误提示

#### Q15: 如何提高 Agent 的执行速度？
**A:** 可以尝试以下方法：
- 只加载一个模型，或使用任课教师提供的轻量/远程模型服务
- 优化 System Prompt，减少不必要的约束
- 实现工具调用缓存机制
- 增加并发处理能力
- 使用模型量化技术减少推理时间

#### Q16: 多步链式调用中断？
**A:**
- 检查Agent是否有足够的上下文记忆
- 增加max_iterations参数
- 检查工具返回结果格式是否正确
- 使用 MoE 模型（`qwen3.6:35b-a3b`）效果更好
- 查看日志，找出中断原因

#### Q17: Agent 出现幻觉怎么办？
**A:** 可以采取以下措施：
- 优化 System Prompt，增加约束条件
- 增加工具调用结果的验证机制
- 实现多轮确认机制
- 使用更强大的模型
- 增加示例（Few-shot learning）

#### Q18: 如何添加更多的业务工具？
**A:** 添加新工具的步骤：
1. 实现工具函数（遵循原子化原则）
2. 在 tools_schema 中添加工具描述
3. 在 agent_orchestrator 中添加工具调用路由
4. 更新 System Prompt（可选）

#### Q19: 如何实现多 Agent 协作？
**A:** 实现多 Agent 协作的方法：
1. 定义不同角色的 Agent（如：规划 Agent、执行 Agent、验证 Agent）
2. 实现 Agent 之间的通信机制
3. 设计任务分配和协调策略
4. 实现结果汇总和验证机制

---

### Git提交相关

#### Q20: Git提交信息怎么写？
**A:**
- 使用约定式提交规范：`<类型>: <描述>`
- 常用类型：feat(新功能)、fix(修复)、docs(文档)、style(格式)、refactor(重构)、test(测试)、chore(构建)
- 示例：`feat: 添加Agent调度器`、`fix: 修复工具调用参数错误`
- 用中文或英文都可以，保持一致即可
- 提交信息要简洁明了

### 性能优化相关

#### Q21: 如何提高模型推理速度？
**A:**
- 只加载一个模型，或使用任课教师提供的轻量/远程模型服务
- 关闭其他占用内存的程序
- 增加系统内存（本地运行 Qwen3.6 默认对照模型推荐 32GB 以上）
- 如果有GPU，使用GPU加速
- 减少max_tokens参数

#### Q22: 如何减少内存占用？
**A:**
- 只加载需要的模型，并优先选择 `q4_K_M` 量化版本
- 使用完后从内存中卸载模型：`ollama stop <模型名>`
- 确认不再需要后再删除磁盘模型：`ollama rm <模型名>`
- 避免同时打开多个大模型，必要时设置更小的 `num_ctx`
- 关闭不需要的程序和浏览器标签
- 使用轻量级的代码编辑器
- 定期重启Ollama服务

---

### 扩展学习相关

#### Q23: 想深入学习，有什么推荐资源？
**A:**
- Ollama官方文档：https://github.com/ollama/ollama
- Gradio官方文档：https://www.gradio.app/docs
- OpenAI API文档：https://platform.openai.com/docs
- Qwen模型：https://github.com/QwenLM/Qwen
- MCP协议：https://modelcontextprotocol.io/

#### Q24: 可以尝试其他模型吗？
**A:**
- 可以。Ollama支持很多模型
- 推荐尝试：llama3、mistral、gemma等
- 对比不同模型的表现
- 记录不同模型的表现差异
- 注意模型大小和系统资源限制

---
