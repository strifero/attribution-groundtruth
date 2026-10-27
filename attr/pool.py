"""Candidate pool and queries for one run.

  python attr/pool.py A   -> runs/attr/A/pool.npz (window indices, kind, fact, doc row), pool_text.jsonl (decoded),
                             queries.jsonl (fact id, form, prompt, answer, relevant pool positions)

Pool = every planted and distractor window of the run + 100,000 random base windows (the same base windows for
both runs, since base windows are identical). Queries = each of the run's facts in two forms; the relevant set
is the pool positions of that fact's planted windows. Distractor windows (same entity, other detail) are hard
negatives.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, "/home/sean/elroy")
from elroy.tokenizer import Tokenizer  # noqa: E402

RUN = sys.argv[1]
D = "/home/sean/tda/data"
OUT = f"/home/sean/tda/runs/attr/{RUN}"
os.makedirs(OUT, exist_ok=True)
tok = Tokenizer.load(f"{D}/tokenizer.json")
S = np.load(f"{D}/stream_{RUN}.npy", mmap_mode="r")
ix = np.load(f"{D}/index_{RUN}.npz")
docs = [json.loads(l) for l in open(f"{D}/plant_docs.jsonl")]
spec = json.load(open("/home/sean/tda/plants/spec.json"))
prow = ix["plant_row"]
plant_w = np.where(prow >= 0)[0]
base_w = np.where(prow < 0)[0]
rng = np.random.default_rng(99)
base_pick = np.sort(rng.choice(base_w, 100_000, replace=False))
pool = np.concatenate([plant_w, base_pick])
kind = np.array([docs[prow[w]]["kind"] if prow[w] >= 0 else "base" for w in pool])
fact = np.array([docs[prow[w]]["fact"] if prow[w] >= 0 else "" for w in pool])
np.savez(f"{OUT}/pool.npz", window=pool, kind=kind, fact=fact, plant_row=prow[pool])
with open(f"{OUT}/pool_text.jsonl", "w") as f:
    for w in pool:
        f.write(json.dumps(tok.decode([int(t) for t in S[w][:1024]])) + "\n")
pos_of = {}
for p, (k, fid) in enumerate(zip(kind, fact)):
    if k == "planted":
        pos_of.setdefault(fid, []).append(p)
with open(f"{OUT}/queries.jsonl", "w") as f:
    for fa in spec["facts"]:
        if fa["run"] != RUN:
            continue
        for form, prompt in (("cloze", fa["cloze"]), ("qa", f"Question: What is {fa['fact']}?\nAnswer:")):
            f.write(json.dumps({"fact": fa["id"], "form": form, "prompt": prompt, "answer": " " + fa["object"],
                                "freq": fa["freq"], "pos": fa["pos"], "domain": fa["domain"],
                                "relevant": pos_of.get(fa["id"], [])}) + "\n")
print(RUN, "pool", len(pool), "planted", int((kind == "planted").sum()), "distractor", int((kind == "distractor").sum()),
      "queries", sum(1 for _ in open(f"{OUT}/queries.jsonl")))
