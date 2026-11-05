# agent-deployed — 经 HASHRAP 转化好的 DSH 框架知识库

这里是经 [HASHRAP](https://github.com/hpsks416/HASHRAP) 管线**转化好的框架知识库**：把 DSH 框架内容（`AGENTS.md` 铁律、`persona.md` 画像、全部 `SKILL.md`、`meta-drift-log.md`）建成可检索索引，供 agent 调用框架 / SKILL 前先查原文（铁律三）。

转化方法（`build_kb.py` / `search_kb.py` / `eval` / `mcp`）在 HASHRAP 仓库；本仓库只放转化产物与使用层。

## 结构

- `SKILL.md` — `framework-kb` 检索 skill（接地回答契约 + 核验闭环 + 已知坑）
- `skill-rag/SKILL.md` — 通用 RAG skill
- `grounded-rag-template.md` — 通用「有据可依」回答模板
- `llms.txt` — agent 发现入口
- `mcp_server.py` — MCP server
- `评估-直接使用框架vs知识库.md` — 直接读框架 vs 查知识库的评估

## 用法

知识库 `framework_kb.sqlite3` 是构建产物（gitignored），由 HASHRAP 的 `build_kb.py` 在本机生成；检索由 HASHRAP 的 `search_kb.py` 执行：

```powershell
python search_kb.py "先申请后执行" --lexical-only --no-rerank
```

## 相关仓库

- [HASHRAP](https://github.com/hpsks416/HASHRAP) — 转化方法（RAG 管线：build / search / eval / mcp）

## License

MIT
