"""Score a method's rankings against the answer key.

  scores: float array (n_queries, n_pool), higher = more responsible.
Per query: average precision over the fact's planted windows, recall@10, recall@k where k = number of relevant
windows (R-precision), and the rank of the first relevant window. Reported overall and by frequency, position,
domain and form; distractor confusion = share of the top-10 that are distractor windows of the same entity.
"""
import json
from collections import defaultdict
import numpy as np


def evaluate(scores, queries, pool_kind, pool_fact):
    rows = []
    for qi, q in enumerate(queries):
        rel = np.array(q["relevant"], dtype=np.int64)
        rel = rel[rel < scores.shape[1]]          # a truncated pool (tests) keeps only what it has
        if len(rel) == 0:
            continue
        s = scores[qi]
        order = np.argsort(-s, kind="stable")
        rank = np.empty(len(s), dtype=np.int64)
        rank[order] = np.arange(len(s))
        rr = np.sort(rank[rel])
        ap = float(np.mean((np.arange(len(rr)) + 1) / (rr + 1)))
        top10 = order[:10]
        same_ent_distr = float(np.mean((pool_kind[top10] == "distractor") & (pool_fact[top10] == q["fact"])))
        rows.append({"fact": q["fact"], "form": q["form"], "freq": q["freq"], "pos": q["pos"], "domain": q["domain"],
                     "ap": ap, "r10": float(np.mean(rr < 10)) if len(rr) >= 10 else float(np.sum(rr < 10) / len(rr)),
                     "rprec": float(np.mean(rr < len(rr))), "first": int(rr[0]), "distr_top10": same_ent_distr})
    return rows


def summarize(rows, keys=("freq", "pos", "domain", "form")):
    def agg(rs):
        return {m: round(float(np.mean([r[m] for r in rs])), 4) for m in ("ap", "r10", "rprec", "distr_top10")} | \
               {"median_first": int(np.median([r["first"] for r in rs])), "n": len(rs)}
    out = {"all": agg(rows)}
    for k in keys:
        g = defaultdict(list)
        for r in rows:
            g[r[k]].append(r)
        out[k] = {str(v): agg(rs) for v, rs in sorted(g.items(), key=lambda x: str(x[0]))}
    return out
