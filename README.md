# agent-deployed — 经 HASHRAP 转化好的 DSH 框架知识库

这里是经 [HASHRAP](https://github.com/hpsks416/HASHRAP) 管线**转化好的框架知识库**：把 DSH 框架内容（`AGENTS.md` 铁律、`persona.md` 画像、全部 `SKILL.md` 及其 `references/*.md`、`meta-drift-log.md`、`HANDOFF.md`）建成可检索索引，供 agent 调用框架 / SKILL 前先查原文（铁律三）。

转化方法（`build_kb.py` / `search_kb.py` / `eval` / `mcp`）在 HASHRAP 仓库；本仓库放**转化产物与使用层**。

## 结构

- `framework_kb.sqlite3` — **知识库构建产物，已入库**（clone 即用，无需本机重建）
- `SKILL.md` — `framework-kb` 检索 skill（接地回答契约 + 核验闭环 + 已知坑）
- `skill-rag/SKILL.md` — 通用 RAG skill
- `grounded-rag-template.md` — 通用「有据可依」回答模板
- `llms.txt` — agent 发现入口
- `mcp_server.py` — MCP server
- `build_kb.py` — 构建脚本副本（权威版在 HASHRAP）
- `评估-直接使用框架vs知识库.md` — 直接读框架 vs 查知识库的评估

## 知识库现状

- 源文档 77 个、chunks 724 个（`chunks` 表），FTS5 关键词索引
- 索引范围：铁律 / 画像 / 偏离日志 / HANDOFF + 全部 `SKILL.md` + 各 skill 的 `references/**/*.md`（细节常驻 references，不进索引就会检索不到）
- journal 模式用 **DELETE**（非 WAL）——WAL 在受限沙箱下要求 `-wal/-shm` 写权限，会导致只读场景打不开库
- 源文件变化后由 HASHRAP 的 `build_kb.py` 重建，再复制回本仓 `framework_kb.sqlite3` 并提交

## 用法

可直接用本仓自带的库检索；`search_kb.py` 在 HASHRAP 仓库（本仓只放产物）：

```powershell
python search_kb.py "先申请后执行" --lexical-only --no-rerank
```

## 相关仓库

- [HASHRAP](https://github.com/hpsks416/HASHRAP) — 转化方法（RAG 管线：build / search / eval / mcp）
- [agent-deploy](https://github.com/hpsks416/agent-deploy) — 被转化的框架本体（skill + 铁律 + 部署脚本）

## License

MIT
