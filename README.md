# Framework KB — DSH 框架知识库

把 DSH 框架内容（`AGENTS.md` 铁律、`persona.md` 画像、全部 `SKILL.md`、`meta-drift-log.md`、`HANDOFF.md`）建成本地可检索知识库，让 agent 用「关键词 + 向量 + RRF」找回规则原文，而非靠记忆。

## 结构

- `build_kb.py` — 收集框架文档 → 分块 → FTS5 关键词索引 + 向量化 → `framework_kb.sqlite3`
- `search_kb.py` — 检索（FTS5 BM25 + 向量余弦 + RRF 融合）
- `SKILL.md` — 检索 skill（接地回答契约 + 核验闭环 + 已知坑）
- `grounded-rag-template.md` — 通用「有据可依」回答模板
- `pylibs/` — fastembed 等依赖（`pip install --target`）
- `models/` — 嵌入模型缓存（首次运行自动下载）

## 用法

```powershell
# 1) 构建（首次；含向量化，需 pylibs + 模型下载）
$env:PYTHONPATH = "$PWD\pylibs"
python build_kb.py

# 2) 检索
python search_kb.py "判重读版本差异" --top 8
python search_kb.py "先申请后执行" --lexical-only   # 纯关键词，不加载模型
```

## 依赖

- 运行时：Python 3.11 + numpy + fastembed（已装入 `pylibs/`）
- 嵌入模型：`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`（多语言，缓存于 `models/`）

## 相关仓库

- [HASHRAP](https://github.com/hpsks416/HASHRAP) — RAG 基础设施（MinerU 混合检索 + eval + MCP + skill），本知识库的构建方法即复用它的管线
- 框架本体源码：`~/.dsh/AGENTS.md`（铁律）、`~/.dsh/persona.md`（画像）、`~/.dsh/skills/`（全部 skill）、`~/.dsh/meta-drift-log.md`
