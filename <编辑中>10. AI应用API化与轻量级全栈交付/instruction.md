# 《现代软件开发技术》上机实验手册：AI 应用 API 化与轻量级全栈交付

## 实验主题

本实验把前面实现的 Agent、RAG 或工具链封装成可被外部调用的软件服务。课程重点不是做复杂页面，而是理解一个 AI 能力如何从本地脚本变成 API，再被前端页面或其他系统调用，形成最小可交付应用。

## 实验目标

完成本实验后，同学们应能够：

1. 使用 FastAPI 将 Python AI 工作流封装为 REST API。
2. 设计请求体、响应体和错误返回格式。
3. 实现简单 Token 鉴权，避免接口裸奔。
4. 编写最小前端页面调用后端 API。
5. 理解跨域、端口、环境变量和本地部署的基本问题。
6. 使用 Dockerfile 描述服务运行环境。
7. 将 API 能力整理为 Skill 契约，理解“能力包 -> 服务接口 -> 应用交付”的链路。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：从脚本到服务** | 理解 API 化交付的价值 | REST, HTTP |
| **25-60'** | **模块二：FastAPI 基础服务** | 创建健康检查与问答接口 | FastAPI, Uvicorn |
| **60-100'** | **模块三：封装 AI 工作流** | 将本地函数包装成 API | Pydantic |
| **100-140'** | **模块四：接口鉴权与错误处理** | 添加 Token 校验和标准错误响应 | Header Auth |
| **140-180'** | **模块五：最小前端页面** | 用 HTML/JS 调用后端接口 | fetch API |
| **180-205'** | **模块六：Skill/API 交付契约** | 将 API 能力描述为可复用 Skill | SKILL.md, API Contract |
| **205-230'** | **模块七：Docker 本地交付** | 编写 Dockerfile 并理解镜像化 | Docker |
| **230-240'** | **模块八：总结与扩展** | 梳理交付链路和后续云部署方向 | 工程复盘 |

## 实验安全注意事项

1. 本实验使用本地服务，不要绑定公网地址。
2. 接口 Token 使用模拟值即可，不要使用真实生产密钥。
3. 不要把 `.env` 文件提交到公开仓库。
4. 如果使用 Docker，注意不要挂载包含隐私数据的目录。
5. 前端页面仅用于教学演示，不要收集真实用户信息。

## 环境准备与验证

### 1. 创建实验目录

```bash
mkdir ai_api_delivery_lab
cd ai_api_delivery_lab
python -m venv .venv
```

激活环境后安装：

```bash
pip install fastapi uvicorn pydantic
```

### 2. 建议文件结构

```text
ai_api_delivery_lab/
├── app.py
├── workflow.py
├── auth.py
├── index.html
├── Dockerfile
├── requirements.txt
└── README_LOCAL.md
```

## 第一阶段：本地工作流函数

创建 `workflow.py`：

```python
def run_ai_workflow(question: str) -> dict:
    question = question.strip()
    if not question:
        return {
            "answer": "问题不能为空。",
            "sources": [],
            "ok": False,
        }

    if "RAG" in question or "检索" in question:
        answer = "RAG 通过检索外部资料增强回答，可以降低幻觉风险。"
        sources = ["course_notes:rag"]
    elif "Harness" in question:
        answer = "Harness 工程通过代码级护栏限制 Agent 的工具调用范围。"
        sources = ["course_notes:harness"]
    else:
        answer = "当前示例工作流没有找到足够资料，可在后续接入真实 RAG。"
        sources = []

    return {
        "answer": answer,
        "sources": sources,
        "ok": bool(sources),
    }
```

## 第二阶段：FastAPI 服务

创建 `app.py`：

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from workflow import run_ai_workflow

API_TOKEN = "dev-token"

app = FastAPI(title="Modern Software AI API", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    ok: bool


def check_token(authorization: str | None) -> None:
    expected = f"Bearer {API_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="invalid token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest, authorization: str | None = Header(default=None)):
    check_token(authorization)
    return run_ai_workflow(payload.question)
```

运行：

```bash
uvicorn app:app --reload --port 8000
```

打开：

```text
http://127.0.0.1:8000/docs
```

## 第三阶段：命令行验证 API

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

无 Token 请求：

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"RAG 是什么？"}'
```

应返回 `401`。

带 Token 请求：

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{"question":"RAG 是什么？"}'
```

应返回 JSON 回答。

## 第四阶段：最小前端页面

创建 `index.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>AI API Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; }
    textarea { width: 100%; min-height: 100px; }
    button { padding: 8px 16px; margin-top: 12px; }
    pre { background: #f5f5f5; padding: 16px; overflow: auto; }
  </style>
</head>
<body>
  <h1>AI API Demo</h1>
  <textarea id="question">RAG 是什么？</textarea>
  <br />
  <button onclick="ask()">发送</button>
  <pre id="result"></pre>

  <script>
    async function ask() {
      const question = document.getElementById("question").value;
      const result = document.getElementById("result");
      result.textContent = "请求中...";
      try {
        const res = await fetch("http://127.0.0.1:8000/api/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer dev-token"
          },
          body: JSON.stringify({ question })
        });
        const data = await res.json();
        result.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        result.textContent = String(err);
      }
    }
  </script>
</body>
</html>
```

如果浏览器跨域报错，可在 FastAPI 中加入 CORS 中间件。课堂中也可直接使用 `/docs` 验证接口。

## 第五阶段：CORS 处理

如需允许本地 HTML 页面访问 API，在 `app.py` 中加入：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

教学环境可以使用 `*`，真实系统应限制为明确域名。

## 第六阶段：Skill/API 交付契约

### 目标

API 解决“外部系统如何调用能力”，Skill 解决“Agent 或开发者如何理解和复用能力”。本阶段将 `/api/ask` 的能力整理成 Skill 契约，形成从能力说明到服务接口的交付文档。

创建目录：

```bash
mkdir -p skill
```

创建 `skill/SKILL.md`：

````markdown
---
name: course-qa-api
description: 通过本地 FastAPI 服务回答现代软件开发技术课程相关问题。适用于需要查询 RAG、Harness、Agent、TDD、CI/CD 等课程概念的场景；调用前必须确认本地 API 服务已启动，并携带授权 Token。
---

# Course QA API

## 能力范围

- 接收一个课程相关问题。
- 调用 `POST /api/ask`。
- 返回 `answer`、`sources`、`ok` 字段。

## 接口约定

- URL: `http://127.0.0.1:8000/api/ask`
- Method: `POST`
- Header: `Authorization: Bearer dev-token`
- Body:

```json
{
  "question": "RAG 是什么？"
}
```

## 失败处理

- `401`：检查 Token。
- `422`：检查请求体字段。
- `ok=false`：说明当前工作流没有足够资料回答。
````

### 观察要点

同学们需要区分：

1. **API 文档**：面向程序调用，强调 URL、方法、请求体、响应体。
2. **Skill 文档**：面向 Agent 或开发者复用，强调何时使用、能力边界、失败处理。
3. **Dockerfile**：面向部署，强调运行环境和启动命令。

这三者合在一起，才构成一个较完整的 AI 能力交付单元。

## 第七阶段：Dockerfile

创建 `requirements.txt`：

```text
fastapi
uvicorn
pydantic
```

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py workflow.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建镜像：

```bash
docker build -t ai-api-demo .
```

运行容器：

```bash
docker run --rm -p 8000:8000 ai-api-demo
```

如果电脑未安装 Docker，可只完成 FastAPI 本地服务部分。

## 第八阶段：交付检查清单

同学们应确认：

1. `/health` 返回正常。
2. `/api/ask` 无 Token 时被拒绝。
3. `/api/ask` 带 Token 时返回结构化 JSON。
4. 前端页面能显示 API 返回结果。
5. `skill/SKILL.md` 能说明 API 的能力范围、接口约定和失败处理。
6. Dockerfile 能说明服务运行环境。
7. 错误响应可被前端或调用方理解。

## 故障排除 FAQ

### Q1: `uvicorn` 命令找不到怎么办？

**A:** 检查虚拟环境是否激活，并确认已执行 `pip install fastapi uvicorn pydantic`。

### Q2: 访问 `/api/ask` 返回 401 是错误吗？

**A:** 如果没有带 Token，返回 401 是正确行为，说明接口鉴权生效。

### Q3: 前端页面跨域报错怎么办？

**A:** 加入 CORS 中间件，或使用 FastAPI 自带 `/docs` 先验证后端接口。

### Q4: Docker 构建很慢怎么办？

**A:** 可以先完成本地服务。Docker 是交付增强项，依赖镜像下载速度。

### Q5: 真实项目能使用固定 `dev-token` 吗？

**A:** 不能。真实项目应使用环境变量、密钥管理服务或 OAuth 等机制。

## 参考资源

- FastAPI: https://fastapi.tiangolo.com/
- Uvicorn: https://www.uvicorn.org/
- Docker: https://docs.docker.com/
- MDN Fetch API: https://developer.mozilla.org/docs/Web/API/Fetch_API
