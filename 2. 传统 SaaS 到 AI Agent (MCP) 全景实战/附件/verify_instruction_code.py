"""验证实验手册中的 Python 代码块是否真的可以运行。

这个脚本面向教师或助教，用于发布材料前做自动化自检。它会从上一级
`instruction.md` 中抽取所有 Python 代码块，临时拼装成可执行的应用文件，
再运行编译检查、业务冒烟测试、文档内单元测试以及可选的 Ollama API 实测。

为什么要这样做：
- 教学文档里的代码最容易在复制、改模型名、改依赖版本时悄悄失效。
- 同学遇到的很多问题不是业务逻辑问题，而是文档代码和附件代码不一致。
- 该脚本把“文档代码是否可运行”变成一个可重复执行的检查项。

Run inside the course Conda environment:

    conda run -n msd-agent-mcp python verify_instruction_code.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import argparse
from pathlib import Path


# ROOT 指向实验主题目录，INSTRUCTION 指向需要被验证的教学手册。
# 使用相对层级定位，保证脚本在不同机器、不同仓库路径下都能运行。
ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION = ROOT / "instruction.md"


def extract_code_blocks() -> list[tuple[str, str]]:
    """从 Markdown 文档中抽取所有三反引号代码块。

    Returns:
        `(language, code)` 元组列表。language 是代码块声明的语言，例如 `python` 或 `bash`。

    注意：本实验手册中的 Python 代码块均使用标准三反引号，因此这里使用轻量正则足够稳定。
    """
    text = INSTRUCTION.read_text(encoding="utf-8")
    pattern = re.compile(r"```([^\n`]*)\n(.*?)```", re.S)
    return [(match.group(1).strip(), match.group(2)) for match in pattern.finditer(text)]


def pick_python_blocks(blocks: list[tuple[str, str]]) -> list[str]:
    """筛选出真正需要 Python 解释器验证的代码块。"""
    return [code for lang, code in blocks if lang == "python"]


def build_app_code(py_blocks: list[str]) -> str:
    """把分散在文档中的应用代码块拼成一个完整 Python 文件。

    文档为了教学节奏把代码拆成“导入依赖、工具函数、SaaS 控制器、
    Agent 调度器、Gradio UI”等多个阶段。验证时需要把这些阶段重新拼接，
    才能像同学最终完成的 `app.py` 一样运行。
    """
    # 每个 marker 对应一个教学阶段的关键片段；缺失任意阶段都说明文档不完整。
    markers = [
        "import gradio as gr",
        "def get_employee_directory",
        "def saas_generate_payroll_api",
        "tools_schema =",
        "def agent_orchestrator",
        "with gr.Blocks",
    ]
    selected: list[str] = []
    for marker in markers:
        # 按 marker 顺序寻找代码块，保持最终文件的依赖顺序正确。
        for block in py_blocks:
            if marker in block:
                selected.append(block)
                break
        else:
            raise AssertionError(f"Missing Python code block containing: {marker}")
    return "\n\n".join(selected) + "\n"


def pick_test_blocks(py_blocks: list[str]) -> list[str]:
    """找出文档中引用 `your_app_file` 的单元测试代码块。"""
    tests: list[str] = []
    for block in py_blocks:
        if "from your_app_file import" in block:
            tests.append(block)
    # 文档应至少包含工具测试、Agent 调度器测试和集成测试三个测试片段。
    if len(tests) < 3:
        raise AssertionError("Expected at least 3 unittest/performance snippets importing your_app_file")
    return tests


def pick_block(py_blocks: list[str], marker: str) -> str:
    """按关键文本找到某个独立代码块，例如清理脚本或 API 连接脚本。"""
    for block in py_blocks:
        if marker in block:
            return block
    raise AssertionError(f"Missing Python code block containing: {marker}")


def run(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """在临时目录中运行命令，并在失败时输出 stdout/stderr。

    Args:
        cmd: 要执行的命令列表，第一项通常是当前 conda 环境中的 Python 解释器。
        cwd: 命令执行目录。验证脚本会把临时应用文件写到这个目录。
        timeout: 单个命令的超时时间，避免测试卡死。

    Returns:
        subprocess.CompletedProcess，供调用方在需要时继续读取输出。
    """
    env = os.environ.copy()
    # 让临时测试文件可以直接 `import your_app_file` 或 `import app`。
    env["PYTHONPATH"] = str(cwd)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        # 失败时主动打印输出，便于助教定位是哪段文档代码不可运行。
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def ollama_has_model(model: str) -> bool:
    """检查本机 Ollama 是否已经下载指定模型。"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return model in result.stdout


def main() -> None:
    """执行完整验证流程。"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live-ollama",
        action="store_true",
        help="also run the Ollama API connection code block against qwen3.6:35b-a3b",
    )
    args = parser.parse_args()

    # 先抽取并分类代码块，再准备拼装应用、测试片段和独立验证片段。
    blocks = extract_code_blocks()
    py_blocks = pick_python_blocks(blocks)
    app_code = build_app_code(py_blocks)
    test_blocks = pick_test_blocks(py_blocks)
    cleanup_block = pick_block(py_blocks, "csv_path = os.path.join")
    api_block = pick_block(py_blocks, "Ollama API 连接成功")

    # 使用临时目录运行文档代码，避免污染课程目录，也避免覆盖同学自己的 app.py。
    with tempfile.TemporaryDirectory(prefix="msd_instruction_verify_") as tmp:
        workdir = Path(tmp)
        for name in ("your_app_file.py", "app.py"):
            # 同时写两个文件名，是为了兼容文档中不同测试片段的导入方式。
            (workdir / name).write_text(app_code, encoding="utf-8")

        # 第一层检查：确保拼装后的应用语法正确。
        run([sys.executable, "-m", "py_compile", "your_app_file.py"], workdir)

        # 第二层检查：不依赖真实模型，直接调用业务函数和 Gradio 构建结果。
        smoke = """
import json
import os
import your_app_file as app

employees = app.get_employee_directory()
payroll = app.calculate_payroll_and_tax(employees)
exported = json.loads(app.export_payroll_csv(payroll))
table, path = app.saas_generate_payroll_api()

assert isinstance(json.loads(employees), list)
assert isinstance(json.loads(payroll), list)
assert exported["status"] == "success"
assert exported["record_count"] == 3
assert os.path.exists(exported["file_path"])
assert len(table) == 3
assert path and os.path.exists(path)
assert app.demo is not None
"""
        run([sys.executable, "-c", smoke], workdir)

        # 第三层检查：运行文档中的清理脚本，确认临时文件删除逻辑无语法和路径错误。
        (workdir / "cleanup_snippet.py").write_text(cleanup_block, encoding="utf-8")
        run([sys.executable, "cleanup_snippet.py"], workdir)

        # 第四层检查：逐个运行文档中的 unittest 片段。
        for index, block in enumerate(test_blocks, start=1):
            test_file = workdir / f"test_doc_snippet_{index}.py"
            test_file.write_text(block, encoding="utf-8")
            # Gradio 启动测试需要等待本地端口响应，因此给它略短但足够的超时。
            timeout = 45 if "test_gradio_launch" in block else 60
            run([sys.executable, str(test_file.name)], workdir, timeout=timeout)

        # 可选 live 检查：只有本机已有 qwen3.6:35b-a3b 时才真实调用 Ollama。
        if args.live_ollama:
            if not ollama_has_model("qwen3.6:35b-a3b"):
                raise AssertionError("qwen3.6:35b-a3b is not available in `ollama list`")
            (workdir / "api_connection_snippet.py").write_text(api_block, encoding="utf-8")
            run([sys.executable, "api_connection_snippet.py"], workdir, timeout=240)

    mode = "with live Ollama API" if args.live_ollama else "without live Ollama API"
    print(f"Verified {len(py_blocks)} Python code blocks from {INSTRUCTION} ({mode})")


if __name__ == "__main__":
    main()
