#!/usr/bin/env python3
"""框架知识库检索：FTS5 关键词 + 向量余弦 + RRF 融合，返回带出处的框架规则片段。

用法:
    .venv\\Scripts\\python.exe search_kb.py "查询内容" [--top 8] [--lexical-only]
输出: JSON 数组，每项 {source, tag, section, text, score, keyword_hit, vector_hit}
"""
from __future__ import annotations
import argparse
import collections
import json
import re
import sqlite3
import sys
from pathlib import Path

import numpy as np

DB = Path(__file__).resolve().parent / "framework_kb.sqlite3"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def terms(text: str):
    result = re.findall(r"[a-z0-9_]+", text.lower())
    for word in re.findall(r"[\u3400-\u9fff]+", text):
        result.extend(word[i:i + 2] for i in range(max(1, len(word) - 1)))
    return result


def search(query: str, top: int = 8, lexical_only: bool = False):
    if not DB.is_file():
        return {"error": "知识库未构建，先跑 build_kb.py"}
    q_terms = list(dict.fromkeys(terms(query)))
    db = sqlite3.connect(DB)

    rankings = []
    if q_terms:
        match = " OR ".join('"' + t + '"' for t in q_terms[:80])
        rows = db.execute("SELECT id FROM search WHERE search MATCH ? ORDER BY bm25(search) LIMIT 30", (match,))
        rankings.append([r[0] for r in rows])

    vector_sims = {}
    if not lexical_only:
        from fastembed import TextEmbedding
        encoder = TextEmbedding(EMBED_MODEL, cache_dir=str(Path(__file__).resolve().parent / "models"),
                                threads=4)
        qv = np.asarray(next(iter(encoder.query_embed(query))), dtype=np.float32)
        qv /= max(float(np.linalg.norm(qv)), 1e-12)
        rows = db.execute("SELECT chunk_id, vector FROM vectors").fetchall()
        sims = []
        for cid, raw in rows:
            v = np.frombuffer(raw, dtype=np.float32)
            if len(v) == len(qv):
                sims.append((float(v @ qv), cid))
        sims.sort(reverse=True)
        rankings.append([cid for _, cid in sims[:30]])
        vector_sims = dict((cid, s) for s, cid in sims)

    scores = collections.defaultdict(float)
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            scores[cid] += 1 / (60 + rank + 1)

    shortlist = sorted(scores, key=scores.get, reverse=True)[:top]
    results = []
    for cid in shortlist:
        row = db.execute("SELECT source, tag, section, text FROM chunks WHERE id=?", (cid,)).fetchone()
        if not row:
            continue
        source, tag, section, text = row
        results.append({
            "source": source, "tag": tag, "section": section, "text": text[:600],
            "score": round(scores[cid], 4),
            "keyword_hit": cid in (rankings[0] if rankings else []),
            "vector_hit": cid in (rankings[1] if len(rankings) > 1 and not lexical_only else []),
        })
    db.close()
    return {"query": query, "results": results}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--lexical-only", action="store_true")
    args = ap.parse_args()
    print(json.dumps(search(args.query, args.top, args.lexical_only), ensure_ascii=False, indent=2))
