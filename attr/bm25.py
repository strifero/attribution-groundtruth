"""BM25 baseline (no model). Query = prompt + answer text.  python attr/bm25.py A"""
import json, sys
import numpy as np
import bm25s
sys.path.insert(0, "/home/sean/tda/attr")
from metrics import evaluate, summarize  # noqa: E402


def write_mass(scores, queries, D, name):
    import json as _j
    import numpy as _np
    acc = {}
    for qi, q in enumerate(queries):
        rel = _np.array(q["relevant"], dtype=_np.int64)
        rel = rel[rel < scores.shape[1]]
        if len(rel) == 0:
            continue
        s = scores[qi]
        z = (s[rel] - s.mean()) / (s.std() + 1e-12)
        acc.setdefault(q["fact"], []).append(float(z.mean()))
    _j.dump({k: float(_np.mean(v)) for k, v in acc.items()}, open(f"{D}/mass_{name}.json", "w"))

RUN = sys.argv[1]
OUT = f"/home/sean/tda/runs/attr/{RUN}"
texts = [json.loads(l) for l in open(f"{OUT}/pool_text.jsonl")]
queries = [json.loads(l) for l in open(f"{OUT}/queries.jsonl")]
P = np.load(f"{OUT}/pool.npz")
ret = bm25s.BM25()
ret.index(bm25s.tokenize(texts, stopwords="en", show_progress=False), show_progress=False)
qt = bm25s.tokenize([q["prompt"] + q["answer"] for q in queries], stopwords="en", show_progress=False)
docs, sc = ret.retrieve(qt, k=1000, show_progress=False, n_threads=6)
scores = np.full((len(queries), len(texts)), -1e9, dtype=np.float32)
for i in range(len(queries)):
    scores[i, docs[i]] = sc[i]
scores[scores < -1e8] = scores[scores > -1e8].min()
write_mass(scores, queries, OUT, "bm25")
rows = evaluate(scores, queries, P["kind"], P["fact"])
s = summarize(rows)
json.dump({"method": "bm25", "summary": s, "rows": rows}, open(f"{OUT}/res_bm25.json", "w"))
print(json.dumps(s["all"]), json.dumps(s["freq"]))
