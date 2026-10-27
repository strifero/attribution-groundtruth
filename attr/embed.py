"""Embedding retrieval baseline (no Elroy): bge-base-en-v1.5 on decoded windows (first 512 tokens) and on
query prompt + answer.  python attr/embed.py <run>"""
import json, sys
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
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
D = f"/home/sean/tda/runs/attr/{RUN}"
texts = [json.loads(l) for l in open(f"{D}/pool_text.jsonl")]
qs = [json.loads(l) for l in open(f"{D}/queries.jsonl")]
P = np.load(f"{D}/pool.npz")
m = SentenceTransformer("BAAI/bge-base-en-v1.5", device="cuda")
m.max_seq_length = 512
E = m.encode(texts, batch_size=128, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
Q = m.encode([q["prompt"] + q["answer"] for q in qs], normalize_embeddings=True, convert_to_numpy=True)
s = Q @ E.T
write_mass(s, qs, D, "embed_bge")
rows = evaluate(s, qs, P["kind"], P["fact"])
summ = summarize(rows)
json.dump({"method": "embed_bge", "summary": summ, "rows": rows}, open(f"{D}/res_embed_bge.json", "w"))
print(json.dumps(summ["all"]), json.dumps({k: v["ap"] for k, v in summ["freq"].items()}))
