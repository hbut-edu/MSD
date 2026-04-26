# 《现代软件开发技术》上机实验手册：多模型智能体网关部署实战，以 OpenClaw 为例

---

## 实验主题

OpenClaw 与多模型智能体网关部署——理解基础设施即代码 (IaC)

## 实验目标

1. 理解"基础设施即代码 (IaC)"现代工程范式
2. 掌握如何利用 OpenClaw 搭建本地网关
3. 学会通过 WebSocket 实现与云端服务的实时双向通信
4. 实现企业级 IM（飞书）与云端/本地大模型的端到端智能路由
5. 掌握 Provider、Agent、Channel、Router 的声明式配置方法
6. 建立本地网关与云端服务的安全连接思维
7. 理解 Skill、MCP、Agent、Router 在 AgentOps 框架中的分工关系

## 📅 课程概览 (Total: 240 Mins)

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :--- | :--- | :--- | :--- |
| **0-30'** | **阶段一：OpenClaw 安装方式补充** | 建立实验目录，完成 Python 虚拟环境与 OpenClaw 安装验证。 | Python, venv, pip |
| **30-60'** | **阶段二：网关启动与架构体验** | 启动 OpenClaw 网关，理解默认配置与本地服务边界。 | OpenClaw Gateway, Debug 日志 |
| **60-90'** | **阶段三：接入云端智能体** | 配置火山引擎豆包模型，完成云端模型链路验证。 | Volcengine Ark, Provider, Agent |
| **90-120'** | **阶段四：飞书 WebSocket 通道** | 配置飞书 Channel，建立本地网关与飞书云端的双向连接。 | Feishu, WebSocket, OAuth |
| **120-150'** | **阶段五：机器人最小特权配置** | 配置机器人权限，验证消息从飞书抵达本地网关。 | 飞书开放平台, 权限控制 |
| **150-180'** | **阶段六：接入本地离线智能体** | 接入 Ollama 本地模型，理解本地模型与云端模型的资源差异。 | Ollama, Qwen3.5, Local Agent |
| **180-210'** | **阶段七：路由与端到端验收** | 配置 Router 规则，完成云端/本地 Agent 的端到端消息分发。 | Router, E2E Test |
| **210-240'** | **阶段八：Skill / MCP / IaC 落盘验证与总结** | 查看配置文件，理解 Skill、MCP、Agent、Router 与声明式配置的关系。 | Skill, MCP, YAML, Config as Code |

---

## 🤖 背景导入：什么是 OpenClaw？

**OpenClaw（原 Clawdbot）** 是一款**开源、自托管的个人 AI 助手框架**。它可以在本地计算机上运行，兼容 Windows 及 Linux 等多种系统，支持与火山引擎等主流模型服务集成。

### 核心能力
- **多模型接入**：支持火山引擎、OpenAI、Anthropic 等多种模型提供商
- **多渠道集成**：可接入飞书、钉钉、微信等常用聊天工具
- **插件扩展**：除内置多种 Agent 常用工具外，还可通过插件和 Skill 扩展更多能力
- **自托管**：完全本地部署，数据隐私可控

### Skill、MCP、Agent、Router 的关系

在 AgentOps 系统中，几个概念容易混在一起。本实验采用如下理解方式：

| 概念 | 主要职责 | 本实验中的观察位置 |
| :-- | :-- | :-- |
| **Skill** | 把一组知识、流程或工具封装为可复用能力包 | 插件扩展、后续安全文件助手 Skill |
| **MCP** | 用标准协议描述工具能力、参数和调用方式 | 工具说明、外部系统接口 |
| **Agent** | 持有模型、系统提示词和可调用能力，负责推理与行动 | `agent-doubao`、`agent-qwen` |
| **Router** | 根据消息前缀或上下文把请求分发给不同 Agent | `/code`、`/chat` 路由 |
| **Provider** | 管理模型服务来源，如火山引擎或 Ollama | 云端 Provider、本地 Provider |

可以把 Skill 理解为“能力包”，MCP 理解为“能力接口”，Agent 理解为“执行者”，Router 理解为“分发器”。同学们在查看配置文件时，应尝试把这些对象逐一对应到 YAML 或命令行参数中。

---

## 💡 为什么要学习 OpenClaw？

### 1. 理解现代 AI 网关架构
OpenClaw 是一个典型的**多模型智能体网关**，通过学习它，同学们可以理解：
- 如何将不同来源的模型（云端/本地）统一管理
- 如何通过声明式配置（Declarative Configuration）管理复杂系统
- 如何实现企业级 IM 与大模型的端到端智能路由

### 2. 体验声明式配置的便捷性
OpenClaw 采用了合理的默认配置（约定优于配置原则）：
- 开箱即用的默认设置，减少重复配置
- 只需显式声明需要覆盖的配置项
- 大幅降低入门和使用门槛

### 3. 实践"基础设施即代码"
通过 OpenClaw，同学们可以体验 **Infrastructure as Code (IaC)** 的威力：
- 所有配置都存储在 YAML/JSON 文件中
- 配置可版本控制、可复制、可迁移
- 一键部署成百上千个网关实例

---

## 🏆 OpenClaw 的重要性

### 1. 企业级落地的现实选择
在企业环境中，OpenClaw 提供了：
- **WebSocket 长连接**：通过 WebSocket 实现与云端服务的实时双向通信
- **权限隔离**：支持最小特权原则，保障数据安全
- **可观测性**：完整的日志系统，便于调试和审计

### 2. 开源社区生态
- 活跃的开源社区，持续迭代更新
- 丰富的插件生态，可扩展性强

### 3. 教育价值
对于学习现代软件工程的学生来说，OpenClaw 是一个**绝佳的教学案例**：
- 代码结构清晰，易于理解
- 涵盖了软件工程多个核心概念
- 可以亲手搭建从 0 到 1 的完整系统

---

## 🔍 其他类似方案对比

除了 OpenClaw，还有一些类似的 AI Agent 框架：

### 1. OpenAI Swarm
- **特点**：OpenAI 官方推出的轻量级多 Agent 协调框架
- **优势**：
  - 与 GPT 模型深度集成
  - 简单易用的 API 设计
  - 专注于 Agent 之间的协调
- **局限**：
  - 主要支持 OpenAI 模型
  - 缺少企业级功能（如渠道集成、权限管理）
  - 相对较新，生态尚在建设中

### 2. LangChain
- **特点**：最流行的 LLM 应用开发框架
- **优势**：
  - 生态最丰富，插件最多
  - 支持几乎所有主流模型
  - 社区活跃，文档完善
- **局限**：
  - 学习曲线较陡
  - 对于简单场景可能过于复杂
  - 更多是开发库而非完整产品

### 3. Dify
- **特点**：可视化的 LLMOps 平台
- **优势**：
  - 图形化界面，上手快
  - 内置工作流编排
  - 提供 SaaS 和自托管两种版本
- **局限**：
  - 自定义灵活性相对较低
  - 主要面向无代码/低代码场景

### 4. Coze
- **特点**：字节跳动推出的 AI Bot 开发平台
- **优势**：
  - 与豆包模型深度集成
  - 丰富的插件市场
  - 支持多渠道发布
- **局限**：
  - 主要是云端 SaaS
  - 自托管选项有限

### 为什么选择 OpenClaw？
在教学场景中，OpenClaw 的优势特别明显：
✅ **完整但不过度复杂**——可以学到完整架构，又不会被细节淹没  
✅ **自托管优先**——可以在本地完整运行，理解每个环节  
✅ **声明式配置**——直观展示 IaC 理念  
✅ **多模型支持**——可以同时体验云端和本地模型  
✅ **企业级功能**——权限、安全、可观测性一应俱全

---

## ⚠️ 实验安全注意事项

在开始实验之前，请仔细阅读并遵守以下安全规定：

### 1. 凭证安全
* **API Key 保护**：火山引擎 API Key、飞书 App Secret 等敏感信息请妥善保管，切勿提交到公开仓库
* **临时使用**：实验完成后，建议在火山引擎控制台删除临时创建的 API Key
* **飞书应用**：实验使用的飞书应用建议在课程结束后删除或重置 App Secret

### 2. 资源使用
* **模型资源**：合理控制模型调用频率，避免造成不必要的费用
* **本地资源**：Ollama 运行时注意监控内存和显存使用情况
* **网络资源**：WebSocket 连接保持稳定即可，无需频繁重连

### 3. 数据安全
* **测试数据**：实验过程中使用测试数据，不要发送真实敏感信息
* **日志清理**：实验完成后，可以清理 OpenClaw 生成的日志文件
* **配置文件**：config.yaml 中包含敏感信息，注意保密

---

## 🔧 环境准备与验证

### 1. 系统要求
* **操作系统**：Windows 10/11 或 Linux
* **Python 版本**：Python 3.8+
* **内存**：建议 16GB 以上（运行本地模型建议 32GB）
* **磁盘空间**：至少 10GB 可用空间
* **网络**：稳定的互联网连接

### 2. 基础环境安装与确认

#### Windows 用户：使用 winget 安装（推荐）
如果同学使用 Windows 10/11，可以使用系统自带的包管理器 `winget` 快速安装：

```powershell
# 安装 Python 3.11
winget install Python.Python.3.11

# 安装 Git
winget install Git.Git
```

安装完成后，**重启终端**，然后验证：
```bash
python --version  # 要求 >= 3.8
git --version     # 确认 Git 客户端可用
```

#### 手动安装（通用方式）
如果 winget 不可用，请手动安装：
- **Python**: 访问 https://www.python.org/downloads/ 下载安装
- **Git**: 访问 https://git-scm.com/downloads/ 下载安装

**防坑提示**：如果提示 `python 不是内部或外部命令`，请立刻检查系统环境变量 (Path) 中是否已添加 Python 的安装路径。

### 3. 本地底座唤醒 (Ollama)

#### 检查 Ollama 运行状态
1. 检查 Windows 右下角系统托盘，确认有一只"小羊驼"图标（代表 Ollama 守护进程正在后台运行，否则本地 `11434` 端口是关闭的）。
2. 在终端运行：
```bash
ollama run qwen3.5:9b
```
3. 看到 `>>>` 提示符后，随便输入一句问候语。模型回复后，输入 `/bye` 退出。

**目的**：将几 GB 的模型权重预热加载到内存/显存中，避免后续实验时因冷启动导致网关请求超时。

### 4. OpenClaw 官方安装与火山引擎配置（推荐方式）

OpenClaw 提供了官方一键安装脚本，这是最简单、最标准的安装方式。

#### 方式一：使用官方安装脚本（推荐）

**Windows (PowerShell)**：
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

**Linux**：
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装完成后，根据提示信息完成配置：

| 提示信息 | 配置选项 |
| :--- | :--- |
| I understand this is personal-by-default and shared/multi-user use requires lock-down. Continue? | 选择 **"Yes"** |
| Setup mode | 选择 **"QuickStart"** |
| Model/auth provider | 选择 **"Volcano Engine"** |
| Enter Volcano Engine API key | 填入同学自己的火山引擎 API Key |
| Default model | 选择 **"volcengine-plan/ark-code-latest"** |
| Select channel (QuickStart) | 选择 **"Skip for now"**（后续配置） |
| Configure skills now? (recommended) | 选择 **"No"** |
| Enable hooks? | 按空格键选中，按回车下一步 |
| How do you want to hatch your bot? | 选择 **"Hatch in TUI"** |

#### 方式二：使用 Ark Helper 自动化配置（仅 Linux）

Ark Helper 是火山引擎官方提供的配置助手，可自动完成 OpenClaw 配置：

```bash
# 安装 Ark Helper
curl -fsSL https://lf3-static.bytednsdoc.com/obj/eden-cn/ylwslo-yrh/ljhwZthlaukjlkulzlp/install.sh | sh

# 验证安装
ark-helper --version

# 启动配置助手
ark-helper
```

根据界面提示：
1. 选择套餐：`[Volcano] Volcano Engine（国内）`
2. 配置 API Key
3. 选择默认模型
4. 选择工具：`OpenClaw`
5. 选择 `设置 Volcano 配置到 OpenClaw`

#### 火山引擎 API Key 获取

1. 登录**火山引擎控制台**，进入"火山方舟" (Volcengine Ark)
2. 在左侧导航栏找到 **"API Key 管理"**
3. 点击 **"创建 API Key"**，创建后复制保存

#### 支持的模型列表

配置文件中支持以下模型（可配置 Model Name）：
- `doubao-seed-2.0-code`
- `doubao-seed-2.0-pro`
- `doubao-seed-2.0-lite`
- `doubao-seed-code`
- `minimax-m2.5`
- `glm-4.7`
- `deepseek-v3.2`
- `kimi-k2.5`

**重要提示**：
- Base URL 请使用：`https://ark.cn-beijing.volces.com/api/coding/v3`（兼容 OpenAI 协议）
- 不要使用 `https://ark.cn-beijing.volces.com/api/v3`（会产生额外费用）
- 支持 Auto 模式（通过控制台切换，配置文件中不支持）

---

## 第一阶段：OpenClaw 安装方式补充

**注意**：官方一键安装方式已在"环境准备与验证"部分提供。如果已经使用官方脚本安装，可以直接跳至“第二阶段”。

以下提供 pip 安装方式作为备选方案：

### 方式二：pip 安装方式（备选）

现代软件开发的第一条铁律：**永远不要把第三方包直接安装到系统全局环境中。**

#### 1. Python 虚拟环境创建与激活

**Windows 环境**：
在同学电脑的 D 盘或 E 盘创建一个全英文的实验目录（例如 `D:\AgentOps_Lab`）。在该目录下打开 PowerShell：
```powershell
python -m venv openclaw-env
.\openclaw-env\Scripts\activate
```

**🛑 致命易错点 (PowerShell 拦截)**：如果执行第二句时出现红字报错 `无法加载文件... 因为在此系统上禁止运行脚本`。
* **解决**：以**管理员身份**打开一个新的 PowerShell 窗口，执行 `Set-ExecutionPolicy RemoteSigned`，输入 `Y` 确认。然后回到刚才的窗口重新激活。

**成功标志**：命令行最前面出现 `(openclaw-env)` 的绿色前缀。

#### 2. 包管理安装
在激活的虚拟环境中拉取 OpenClaw 核心包：
```bash
pip install openclaw openclaw-cli
openclaw --version  # 验证安装是否成功
```

#### 3. Ollama 沙箱安装体验（可选）
如果暂不配置 Python 环境，其实还可以利用大模型引擎直接拉取工具包。可新开一个普通终端尝试：
```bash
ollama run openclaw
```

**👨‍🏫 核心思考**：`pip` 安装的包放置在 `.venv` 目录中，而 `ollama run` 下载的文件去哪了？它们在系统资源隔离级别上有什么本质不同？

---

## 第二阶段：网关 (Gateway) 启动与架构体验

网关是 Agent 系统的交通枢纽。本阶段将体验默认配置的便捷性。

### 1. 参数化配置与启动

无需配置 IP 和端口，框架已经约定好了默认值。这里只显式声明需要覆盖的配置（开启 Debug 方便查错）：
```bash
openclaw configure gateway --log-level debug
openclaw start
```

**🛑 致命易错点 (防火墙拦截)**：敲下 start 后，Windows 可能会弹出"Windows Defender 防火墙已阻止此应用的部分功能"。**务必勾选"专用网络"和"公用网络"并允许访问**，否则网关将被彻底封死。

**验证**：打开浏览器，访问 `http://127.0.0.1:18789/health`。看到 `{"status": "ok"}` 即代表网关核心运转正常。**保持这个终端不要关闭！**

### 2. Wizard 交互式探索

重新打开一个**新的终端窗口**（记得激活虚拟环境），直接输入：
```bash
openclaw configure
```

**目的**：利用方向键浏览，看看网关级别还隐藏了哪些诸如 SSL 证书、CORS 跨域等高级网络配置面板。看完后按 `Ctrl+C` 退出向导。

---

## 第三阶段：接入云端智能体 (火山引擎豆包)

### 1. Provider 与 Agent 声明式配置

在第二个终端中，使用完整的 CLI 命令进行配置注入：
```bash
# 1. 注册火山引擎作为供应商
openclaw configure provider add --name volcengine-provider --base-url "https://ark.volces.com/api/v3" --api-key "填入同学自己的火山 API_KEY"

# 2. 挂载 Agent 1，注意 --model 后面跟的是 Endpoint ID！
openclaw configure agent add --name agent-doubao \
  --provider volcengine-provider \
  --model "ep-2024xxxx-xxxx" \
  --temperature 0.1 \
  --system-prompt "你是一个资深的程序员助手，只输出可执行的精简代码。"
```

### 2. 架构思考与本地验证

**👨‍🏫 架构思考**：为什么这里配置模型时不写 `Doubao-Seed-2.0-Code`，而是必须填 `ep-xxxx` 这个乱码一样的端点 ID？

*解析*：因为在企业级云环境中，基础模型是被共享的。创建 Endpoint 相当于在云端划分专属的计算资源配额（TPS/RPM）。网关只认资源端点，不认模型名字。

**验证**：
```bash
openclaw cli chat --agent agent-doubao -m "写一段Python的冒泡排序"
```

如果能看到流式的代码输出，说明本地到云端的加密链路已打通。

---

## 第四阶段：配置飞书 WebSocket 通信通道

为了让不在同一局域网的设备也能与本地网关通信，本实验需要接入企业级 IM（飞书）。

### 1. 飞书后台基础配置

1. 登录**飞书开发者后台**，点击"创建企业自建应用"，随便起个名字（如"代码网关测试"）。
2. 在左侧"凭证与基础信息"中，找到 `App ID` 和 `App Secret`，不要泄露。
3. **关键步骤**：左侧找到"事件订阅"，在这个页面中，将接收方式明确切换为**"使用长连接接收事件 (WebSocket)"**。

### 2. 配置网关通道

回到第二个终端，执行通道打通命令：
```bash
openclaw configure channel add --name feishu-ws \
  --type feishu \
  --app-id "你的AppID" \
  --app-secret "你的AppSecret" \
  --mode websocket
```

**验证**：切回运行着 `openclaw start` 的第一个终端。观察 Debug 日志，只要刷出一行类似 `[Channel] Feishu WebSocket connected successfully` 的字样，说明同学电脑与飞书云端建立了双向隧道！

### 3. 现代开发者体验 (DX)（可选）

如果复制 App Secret 不便，可敲入无参数的 `openclaw configure channel`，选择 Feishu 后，终端往往会打印出一个二维码。用飞书手机端扫码，网关会自动完成 OAuth 鉴权。这在工业界被称为"现代 DX 体验提升"。

---

## 第五阶段：飞书端机器人"最小特权"配置

### 1. 权限最小化原则

1. 在飞书后台左侧点击"添加应用能力"，添加"机器人"。
2. 左侧点击"权限管理"，搜索并**仅勾选**以下两个权限：
   * `获取与发送单聊、群组消息 (im:message:send_as_bot)`
   * `获取单聊消息 (im:message.p2p_msg:readonly)`
3. 点击"创建版本" -> "发布"。

**验证**：打开飞书 PC 客户端，搜索已创建的机器人，发一句"你好"。此时观察本地的 `openclaw start` 终端，屏幕上一定会闪过一大段 JSON 代码（Message Payload）。这证明消息已经抵达同学电脑。

---

## 第六阶段：接入本地离线智能体 (Qwen3.5:9b)

### 1. 配置本地 Agent

在终端注入本地 Ollama 的配置：
```bash
openclaw configure provider add --name local-provider --base-url "http://127.0.0.1:11434/v1"

openclaw configure agent add --name agent-qwen \
  --provider local-provider \
  --model qwen3.5:9b \
  --temperature 0.6 \
  --system-prompt "你是一个热情、博学的全能AI助手。"
```

### 2. 离线验证测试

**操作**：**为了证明它真的是在本地跑的，请拔掉电脑网线（或关闭 Wi-Fi）。**

在终端执行：
```bash
openclaw cli chat --agent agent-qwen -m "用中文介绍一下你自己"
```

如果电脑风扇开始狂转并成功输出文字，说明本地私有化部署完美成功。**测试完记得把网络恢复。**

---

## 第七阶段：配置网关路由 (Router) 与端到端验收

这是最核心的一步：网关就像一个调度员，需要根据消息中的命令前缀，将飞书的消息分发给刚才建好的两个 Agent。

### 1. 路由分发配置

```bash
openclaw configure router add --prefix "/code" --target agent-doubao
openclaw configure router add --prefix "/chat" --target agent-qwen
```

### 2. 端到端验收 (终测)

在飞书客户端，向已创建的机器人发送以下两条消息：
1. `@机器人 /code 帮我用Java写一个线程安全的单例模式`
2. `@机器人 /chat 请用30个字解释一下什么是现代软件开发`

**验收标准**：
* 指令 1 应该迅速返回，且代码在飞书中呈现漂亮的**黑底 Markdown 代码块**排版。
* 指令 2 应该会稍微慢一点（取决于机房电脑的显卡算力），并在本地终端引发一波日志刷屏，最终将结果返回飞书。

---

## 第八阶段：Skill / MCP / 基础设施即代码 (IaC) 的落盘验证与总结

### 1. 揭开魔法的面纱

在同学的实验文件夹中，找到自动生成的 `config.yaml`（或 `.openclaw/config.yaml`）。用 VS Code 或记事本打开它。

**观察**：同学们会发现，刚才敲下的所有 `--name`、`--temperature`、`--prefix`，全部严丝合缝地转化为了这个 YAML 文件中的树状结构。

### 2. Skill 与 MCP 的配置观察

如果配置文件或插件目录中出现 Skill、Tool、MCP Server 等字段，同学们重点观察三件事：

1. Skill 是否声明了自身名称、描述和触发方式。
2. 工具能力是否通过类似 Schema 的方式描述输入参数。
3. Agent 是否能够在配置中关联到这些能力。

即使本次只完成 Provider、Agent、Channel、Router 主链路，也应理解后续扩展 Skill 时不会改变网关的基本思想：**声明能力 -> 挂载能力 -> 路由请求 -> 观测执行结果**。

### 3. 课后总结

在企业里进行 CI/CD（持续集成与交付）时，没有任何界面用于点击“下一步”，也不依赖手机扫码。只需把这个写满命令的脚本跑一遍，或者直接把这个 `config.yaml` 推送到服务器，成百上千台网关就能在 1 秒内配置完毕。这就是**基础设施即代码**的暴力美学，也是本实验希望同学们形成的最重要的工程思维。

---

## ❓ 常见问题 FAQ

### 环境配置相关

#### Q1: Python 虚拟环境激活失败？
**A:** 
- Windows: 检查 PowerShell 执行策略，使用管理员权限运行 `Set-ExecutionPolicy RemoteSigned`
- Linux: 确认使用 `source` 命令激活，而不是直接执行脚本
- 确认虚拟环境目录路径正确

#### Q2: OpenClaw 安装失败？
**A:**
- 确认虚拟环境已激活（命令行前有 `(openclaw-env)` 前缀）
- 检查网络连接，尝试使用清华源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple openclaw openclaw-cli`
- 确认 Python 版本 >= 3.8

#### Q3: Ollama 无法启动？
**A:**
- Windows: 检查系统托盘中是否有 Ollama 图标
- Linux: 运行 `ollama serve` 手动启动服务
- 检查端口 11434 是否被占用：`netstat -ano | findstr 11434` (Windows) 或 `lsof -i :11434` (Linux)

---

### 网关配置相关

#### Q4: 网关启动后无法访问 health 接口？
**A:**
- 确认 `openclaw start` 终端没有报错
- 检查防火墙设置，确保允许 OpenClaw 访问网络
- 尝试访问 `http://localhost:18789/health` 或 `http://127.0.0.1:18789/health`
- 查看 Debug 日志，确认网关监听的端口

#### Q5: Provider 配置后验证失败？
**A:**
- 确认 API Key 正确无误，没有多余空格
- 检查火山引擎 Endpoint 状态是否为"健康"
- 确认 base-url 格式正确：`https://ark.volces.com/api/v3`
- 查看网关 Debug 日志，定位具体错误

#### Q6: Agent 聊天测试失败？
**A:**
- 确认 Provider 配置正确
- 检查模型名称/Endpoint ID 是否正确
- 确认温度参数在合理范围 (0.0-2.0)
- 查看网关日志，了解详细错误信息

---

### 飞书配置相关

#### Q7: WebSocket 连接失败？
**A:**
- 确认飞书后台已切换到"使用长连接接收事件"模式
- 检查 App ID 和 App Secret 是否正确
- 确认网络连接正常，能够访问飞书服务器
- 查看网关 Debug 日志中的 WebSocket 连接信息

#### Q8: 机器人收不到消息？
**A:**
- 确认机器人已发布到企业
- 检查机器人权限是否正确配置
- 确认是单聊还是群聊，群聊需要 @机器人
- 查看网关日志，确认是否有消息 payload 到达

#### Q9: 机器人回复失败？
**A:**
- 确认路由配置正确：`/code` 和 `/chat` 前缀
- 检查对应 Agent 是否正常工作
- 确认飞书机器人有发送消息的权限
- 查看网关日志，定位回复失败原因

---

### 本地模型相关

#### Q10: Ollama 本地模型连接失败？
**A:**
- 确认 Ollama 服务正在运行
- 检查 `http://127.0.0.1:11434` 是否可访问
- 确认模型已正确下载：`ollama list`
- 检查 base-url 配置：`http://127.0.0.1:11434/v1`

#### Q11: 本地模型响应很慢？
**A:**
- 这是正常现象，本地模型推理需要消耗大量计算资源
- 检查电脑内存和显存使用情况
- 考虑使用更小的模型（如 qwen3.5:4b）
- 关闭其他占用资源的应用程序

#### Q12: 离线测试失败？
**A:**
- 确认网络已完全断开（拔掉网线或关闭 Wi-Fi）
- 确认使用的是 `agent-qwen`（本地模型）而不是 `agent-doubao`（云端模型）
- 确认 Ollama 服务仍在运行（Ollama 不需要网络）
- 检查本地模型是否已正确下载到本地

---

### 路由与验收相关

#### Q13: 路由配置不生效？
**A:**
- 确认前缀格式正确（如 `/code`，前面有斜杠）
- 确认目标 Agent 名称正确
- 查看 config.yaml 文件，确认路由配置已保存
- 重启网关使配置生效

#### Q14: 飞书中代码块显示不正常？
**A:**
- 这通常是飞书客户端的渲染问题
- 确认 Agent 的 system prompt 要求输出 Markdown 格式
- 可以尝试在飞书中复制消息内容，在其他 Markdown 编辑器中查看
- 检查网关日志，确认返回内容格式正确

#### Q15: 如何查看生成的 config.yaml？
**A:**
- Windows: 通常在用户目录下的 `.openclaw` 文件夹中
- Linux: `~/.openclaw/config.yaml`
- 也可以在实验目录中查找
- 注意：该文件包含敏感信息，不要分享给他人

---

### 扩展学习相关

#### Q16: 可以参考哪些额外资源？
**A:**
- OpenClaw 官方文档（如有）
- 火山引擎方舟文档
- 飞书开放平台文档
- Ollama 官方文档
- 现代软件工程相关书籍和文章

---

## 附录：OpenClaw 常用命令参考

```bash
# 网关相关
openclaw configure gateway --log-level debug  # 配置网关日志级别
openclaw start                                  # 启动网关
openclaw stop                                   # 停止网关

# Provider 相关
openclaw configure provider add --name <name> --base-url <url> --api-key <key>  # 添加 Provider
openclaw configure provider list                                                 # 列出所有 Provider
openclaw configure provider remove <name>                                        # 删除 Provider

# Agent 相关
openclaw configure agent add --name <name> --provider <provider> --model <model>  # 添加 Agent
openclaw configure agent list                                                       # 列出所有 Agent
openclaw configure agent remove <name>                                              # 删除 Agent
openclaw cli chat --agent <agent> -m <message>                                     # 测试 Agent

# Channel 相关
openclaw configure channel add --name <name> --type <type> --app-id <id> --app-secret <secret>  # 添加 Channel
openclaw configure channel list                                                                      # 列出所有 Channel
openclaw configure channel remove <name>                                                             # 删除 Channel

# Router 相关
openclaw configure router add --prefix <prefix> --target <agent>  # 添加路由
openclaw configure router list                                       # 列出所有路由
openclaw configure router remove <prefix>                            # 删除路由

# 交互式配置
openclaw configure          # 进入 Wizard 交互式配置
openclaw configure provider # Provider 配置向导
openclaw configure agent    # Agent 配置向导
openclaw configure channel  # Channel 配置向导
openclaw configure router   # Router 配置向导
```
