# 《现代软件开发技术》上机实验手册：轻量级异步并发与 Token 成本控制

## 实验主题

本实验面向 AI 软件系统的性能与成本问题。前序课程已经完成意图解析和安全护栏，本实验进一步解决“多个请求同时到来时如何不卡死”“API 调用失败如何重试”“Token 成本如何统计和限流”等工程问题。

## 实验目标

完成本实验后，同学们应能够：

1. 理解同步调用、异步调用和并发调度的区别。
2. 使用 `asyncio` 编写非阻塞任务流程。
3. 实现超时控制、失败重试和指数退避。
4. 编写轻量 Token 估算器，统计输入输出成本。
5. 实现单分钟 Token 限流器，防止成本失控。
6. 对比同步与异步执行的耗时差异。

## 课程概览

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :-- | :-- | :-- | :-- |
| **0-25'** | **模块一：性能与成本问题导入** | 理解 AI Agent 为什么容易慢和贵 | Latency, Token Cost |
| **25-55'** | **模块二：同步基线实现** | 建立串行调用基准 | Python time |
| **55-95'** | **模块三：asyncio 异步改造** | 将串行任务改成并发任务 | asyncio |
| **95-135'** | **模块四：超时与重试** | 处理慢请求和临时失败 | Timeout, Retry |
| **135-175'** | **模块五：Token 估算与成本统计** | 估算每次调用成本并汇总 | Token Accounting |
| **175-220'** | **模块六：限流器与压测** | 防止单分钟调用量超限 | Rate Limiter |
| **220-240'** | **模块七：总结与扩展** | 思考真实 API 接入方式 | 工程复盘 |

## 实验安全注意事项

1. 本实验默认使用模拟模型调用，不消耗真实 API 额度。
2. 如果扩展到真实 API，请设置较小并发数和明确预算上限。
3. 不要把 API Key 写入代码，应通过环境变量读取。
4. 压测时不要攻击公共服务或学校网络服务。
5. 如果电脑明显卡顿，应立即降低并发数。

## 环境准备与验证

### 1. 创建实验目录

```bash
mkdir async_token_lab
cd async_token_lab
python -m venv .venv
```

激活环境后验证：

```bash
python --version
```

本实验核心只依赖 Python 标准库。

### 2. 建议文件结构

```text
async_token_lab/
├── sync_baseline.py
├── async_runner.py
├── retry_timeout.py
├── token_meter.py
├── limiter.py
├── benchmark.py
└── main.py
```

## 第一阶段：同步基线

### 目标

先模拟一个“模型调用”函数，观察串行执行的耗时。

创建 `sync_baseline.py`：

```python
import time


PROMPTS = [
    "总结一下什么是 Git 分支。",
    "解释 TDD 的 Red-Green-Refactor。",
    "说明 Agent 工具调用的基本流程。",
    "解释什么是 Harness 工程。",
    "生成一个 JSON 格式的任务单。",
]


def fake_model_call(prompt: str) -> str:
    time.sleep(1)
    return f"模拟回答：{prompt[:20]}"


def run_sync() -> list[str]:
    results = []
    start = time.perf_counter()
    for prompt in PROMPTS:
        results.append(fake_model_call(prompt))
    elapsed = time.perf_counter() - start
    print(f"sync elapsed={elapsed:.2f}s")
    return results


if __name__ == "__main__":
    run_sync()
```

运行：

```bash
python sync_baseline.py
```

预期耗时约 5 秒。

## 第二阶段：asyncio 异步改造

### 目标

将多个 I/O 等待任务并发执行。

创建 `async_runner.py`：

```python
import asyncio
import time

from sync_baseline import PROMPTS


async def fake_model_call_async(prompt: str) -> str:
    await asyncio.sleep(1)
    return f"模拟回答：{prompt[:20]}"


async def run_async() -> list[str]:
    start = time.perf_counter()
    tasks = [fake_model_call_async(prompt) for prompt in PROMPTS]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start
    print(f"async elapsed={elapsed:.2f}s")
    return results


if __name__ == "__main__":
    asyncio.run(run_async())
```

运行：

```bash
python async_runner.py
```

预期耗时约 1 秒。这里的加速来自并发等待，而不是 CPU 计算变快。

## 第三阶段：超时控制

### 目标

真实模型调用可能长时间无响应，因此需要设置超时。

创建 `retry_timeout.py`：

```python
import asyncio
import random


class ModelCallError(Exception):
    pass


async def unstable_model_call(prompt: str) -> str:
    delay = random.choice([0.2, 0.5, 1.5])
    await asyncio.sleep(delay)
    if random.random() < 0.25:
        raise ModelCallError("模拟临时失败")
    return f"OK:{prompt[:16]}"


async def call_with_timeout(prompt: str, timeout: float = 1.0) -> str:
    return await asyncio.wait_for(unstable_model_call(prompt), timeout=timeout)
```

### 验证

创建临时测试：

```python
import asyncio
from retry_timeout import call_with_timeout

async def main():
    try:
        print(await call_with_timeout("测试超时"))
    except Exception as e:
        print("failed:", e)

asyncio.run(main())
```

## 第四阶段：失败重试与指数退避

继续编辑 `retry_timeout.py`：

```python
async def call_with_retry(prompt: str, retries: int = 3) -> dict:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            result = await call_with_timeout(prompt)
            return {
                "ok": True,
                "result": result,
                "attempts": attempt,
                "error": None,
            }
        except Exception as e:
            last_error = str(e)
            await asyncio.sleep(0.2 * attempt)

    return {
        "ok": False,
        "result": None,
        "attempts": retries,
        "error": last_error,
    }
```

创建 `main.py`：

```python
import asyncio

from retry_timeout import call_with_retry
from sync_baseline import PROMPTS


async def main():
    tasks = [call_with_retry(prompt) for prompt in PROMPTS]
    results = await asyncio.gather(*tasks)
    for item in results:
        print(item)


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python main.py
```

观察每个请求的 `attempts` 字段。

## 第五阶段：Token 估算与成本统计

### 目标

实际系统中，Token 是成本控制的基本单位。本实验用粗略估算代替真实 tokenizer。

创建 `token_meter.py`：

```python
from dataclasses import dataclass


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def estimate_tokens(text: str) -> int:
    chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other_chars = len(text) - chinese_chars
    return chinese_chars + max(1, other_chars // 4)


def estimate_usage(prompt: str, completion: str) -> TokenUsage:
    return TokenUsage(
        prompt_tokens=estimate_tokens(prompt),
        completion_tokens=estimate_tokens(completion),
    )


def estimate_cost(usage: TokenUsage, price_per_1k: float = 0.002) -> float:
    return usage.total_tokens / 1000 * price_per_1k
```

### 验证

```bash
python -c "from token_meter import estimate_usage, estimate_cost; u=estimate_usage('解释TDD','TDD是一种开发方法'); print(u, estimate_cost(u))"
```

## 第六阶段：Token 限流器

### 目标

当单分钟 Token 消耗超过阈值时，系统应等待或拒绝请求。

创建 `limiter.py`：

```python
import asyncio
import time
from collections import deque


class TokenRateLimiter:
    def __init__(self, max_tokens_per_minute: int):
        self.max_tokens = max_tokens_per_minute
        self.events = deque()

    def _cleanup(self) -> None:
        now = time.time()
        while self.events and now - self.events[0][0] > 60:
            self.events.popleft()

    def current_tokens(self) -> int:
        self._cleanup()
        return sum(tokens for _, tokens in self.events)

    async def acquire(self, tokens: int) -> None:
        while True:
            self._cleanup()
            if self.current_tokens() + tokens <= self.max_tokens:
                self.events.append((time.time(), tokens))
                return
            await asyncio.sleep(0.5)
```

## 第七阶段：综合压测

创建 `benchmark.py`：

```python
import asyncio
import time

from limiter import TokenRateLimiter
from retry_timeout import call_with_retry
from sync_baseline import PROMPTS
from token_meter import estimate_cost, estimate_tokens, estimate_usage


async def guarded_call(prompt: str, limiter: TokenRateLimiter) -> dict:
    estimated_prompt_tokens = estimate_tokens(prompt)
    await limiter.acquire(estimated_prompt_tokens)

    start = time.perf_counter()
    result = await call_with_retry(prompt)
    elapsed = time.perf_counter() - start

    completion = result["result"] or ""
    usage = estimate_usage(prompt, completion)

    return {
        **result,
        "prompt": prompt,
        "elapsed": round(elapsed, 3),
        "tokens": usage.total_tokens,
        "cost": round(estimate_cost(usage), 6),
    }


async def main():
    limiter = TokenRateLimiter(max_tokens_per_minute=120)
    prompts = PROMPTS * 3
    start = time.perf_counter()
    tasks = [guarded_call(prompt, limiter) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    total_elapsed = time.perf_counter() - start

    for item in results:
        print(item)

    print("=" * 80)
    print("total_elapsed", round(total_elapsed, 3))
    print("total_tokens", sum(item["tokens"] for item in results))
    print("total_cost", round(sum(item["cost"] for item in results), 6))


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python benchmark.py
```

### 观察要点

1. 异步并发总耗时是否明显小于同步执行。
2. 是否存在失败后重试。
3. Token 总量是否能统计。
4. 限流阈值调低后，程序是否会等待。

## 第八阶段：真实 API 接入思路

本实验默认使用模拟调用。如果接入真实 API，应额外加入：

1. 环境变量读取 API Key。
2. 请求超时。
3. 失败重试。
4. Token 返回值读取。
5. 预算上限。
6. 审计日志脱敏。

不要让真实 API 调用绕过限流器。

## 故障排除 FAQ

### Q1: 为什么异步代码没有变快？

**A:** 如果任务是 CPU 密集型，`asyncio` 不会明显加速。本实验模拟的是网络等待型任务，适合异步并发。

### Q2: `asyncio.run()` 报错怎么办？

**A:** 检查是否在已有事件循环中运行。普通命令行脚本中可以直接使用 `asyncio.run()`。

### Q3: 重试次数越多越好吗？

**A:** 不是。重试会增加延迟和成本。真实系统应设置最大重试次数和总超时时间。

### Q4: 估算 Token 和真实 Token 为什么不同？

**A:** 本实验使用粗略估算帮助理解成本控制。真实项目应使用模型对应 tokenizer 或 API 返回的 usage 字段。

### Q5: 限流器为什么要等待，而不是直接失败？

**A:** 两种策略都可以。等待适合后台任务；直接失败适合交互式产品，避免用户长时间无响应。

## 参考资源

- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- OpenAI Rate Limits: https://platform.openai.com/docs/guides/rate-limits
- Tenacity Retry Library: https://tenacity.readthedocs.io/
