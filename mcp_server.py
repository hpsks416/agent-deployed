"""framework-kb 检索 MCP server：把框架知识库检索暴露成 agent 可全权驱动的 MCP 工具。

依赖：pip install mcp（已随 pylibs 装入）
启动：python mcp_server.py        # MCP 在 http://127.0.0.1:8000/mcp
连接：claude mcp add --transport http framework-kb http://127.0.0.1:8000/mcp

本服务只读检索（search），不改框架文件；重建知识库走 build_kb.py。
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

# --target 安装的依赖：先补 sys.path 与 pywin32 DLL 搜索路径，再 import mcp
BASE = Path(__file__).resolve().parent
_PYLIBS = BASE / "pylibs"
if _PYLIBS.is_dir():
    sys.path.insert(0, str(_PYLIBS))
    sys.path.insert(0, str(_PYLIBS / "win32"))
    sys.path.insert(0, str(_PYLIBS / "win32" / "lib"))
    _dll = _PYLIBS / "pywin32_system32"
    if _dll.is_dir() and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(_dll))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("framework-kb")


def _python() -> str:
    """返回框架知识库的自包含 Python（.uv-python 优先），保证与 pylibs 的 numpy/fastembed ABI 一致；
    找不到才退回 sys.executable。避免依赖系统 python 或 DSH runtime 的 python 版本漂移。"""
    uv_dir = BASE / ".uv-python"
    if uv_dir.is_dir():
        for d in sorted(uv_dir.iterdir()):
            if d.is_dir() and d.name.startswith("cpython-") and (d / "python.exe").is_file():
                return str(d / "python.exe")
    return sys.executable


def _run(*args: str) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(BASE / "pylibs")
    env["PYTHONUTF8"] = "1"
    proc = subprocess.run(
        [_python(), str(BASE / "search_kb.py"), *args],
        cwd=str(BASE), env=env, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        return json.dumps({"error": (proc.stderr or "").strip()}, ensure_ascii=False)
    return proc.stdout


@mcp.tool()
def search(query: str, top: int = 8, lexical_only: bool = False) -> str:
    """检索 DSH 框架知识库（FTS5 关键词 + 向量余弦 + RRF 融合），返回带出处（source/section）的框架规则原文。"""
    args = [query, "--top", str(top)]
    if lexical_only:
        args.append("--lexical-only")
    return _run(*args)


def _load_skill() -> str:
    return (BASE / "SKILL.md").read_text(encoding="utf-8")


@mcp.resource("tool://skill")
def skill() -> str:
    """工具说明书（接地回答契约 + 核验闭环 + 已知坑）。"""
    return _load_skill()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
