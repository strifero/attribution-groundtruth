"""Collect every number the report uses into report/data.json."""
import json
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

R = "/home/sean/tda"
spec = json.load(open(f"{R}/plants/spec.json"))["facts"]
out = {}

# learned rate: own model ranks the answer first in both prompt forms averaged; by freq x pos, averaged over runs
acc = defaultdict(list)
unseen = []
for run in "AB":
    fe = json.load(open(f"{R}/runs/fact_{run}_final.json"))
    for f in spec:
        a = float(np.mean([fe[f["id"]][k]["rank"] == 0 for k in ("cloze", "qa")]))
        if f["run"] == run:
            acc[(f["freq"], f["pos"])].append(a)
            acc[(f["freq"], "all")].append(a)
            acc[("all", f["pos"])].append(a)
            acc[("all", "all")].append(a)
        else:
            unseen.append(a)
out["learned"] = {f"{k[0]}|{k[1]}": float(np.mean(v)) for k, v in acc.items()}
out["unseen_acc"] = float(np.mean(unseen))
out["causal"] = json.load(open(f"{R}/runs/causal_final.json"))
out["causal2"] = json.load(open(f"{R}/runs/causal2_final.json"))
out["causal3"] = json.load(open(f"{R}/runs/causal3_final.json"))

# retrieval summaries
ret = {}
for run in "AB":
    for name, fn in [("bm25", "res_bm25"), ("embed_bge", "res_embed_bge"), ("rep_cos_final", "res_rep_cos_final"),
                     ("grad_dot_final", "res_grad_dot_final"), ("grad_cos_final", "res_grad_cos_final"),
                     ("grad_if_final", "res_grad_if_final"), ("tracin_grad_dot", "res_tracin_grad_dot"),
                     ("tracin_grad_if", "res_tracin_grad_if")]:
        d = json.load(open(f"{R}/runs/attr/{run}/{fn}.json"))
        s = d["summary"]
        ret.setdefault(name, {})[run] = {"ap": s["all"]["ap"], "r10": s["all"]["r10"], "rprec": s["all"]["rprec"],
                                          "by_freq": {k: v["ap"] for k, v in s["freq"].items()},
                                          "by_pos": {k: v["ap"] for k, v in s["pos"].items()},
                                          "distr": s["all"]["distr_top10"]}
out["retrieval"] = ret

# per-fact effect and own loss, for "influence tracks current loss"
fe = {r: json.load(open(f"{R}/runs/fact_{r}_final.json")) for r in "AB"}
mass = {}
for run in "AB":
    mass.update(json.load(open(f"{R}/runs/attr/{run}/mass_grad_if_final.json")))
ids = [f["id"] for f in spec]
own_loss = [-np.mean([fe[f["run"]][f["id"]][k]["logp_true"] for k in ("cloze", "qa")]) for f in spec]
learned = []
for f in spec:
    o, x = f["run"], "B" if f["run"] == "A" else "A"
    e = np.mean([fe[o][f["id"]][k]["logp_true"] - fe[x][f["id"]][k]["logp_true"] for k in ("cloze", "qa")])
    learned.append(bool(e > 0 and min(fe[o][f["id"]][k]["rank"] for k in ("cloze", "qa")) == 0))
m = np.array([mass[i] for i in ids])
lr = np.array(learned)
out["if_vs_loss"] = round(float(spearmanr(m, own_loss).statistic), 3)
out["if_mass_learned"] = round(float(m[lr].mean()), 3)
out["if_mass_unlearned"] = round(float(m[~lr].mean()), 3)

# training
for run in "AB":
    L = [json.loads(l) for l in open(f"{R}/ckpt/{run}/tda-124m/log.jsonl")]
    last = [x for x in L if "val" in x][-1]
    out.setdefault("train", {})[run] = {"final_loss": L[-1]["loss"], "val": last["val"], "steps": L[-1]["step"],
                                        "tok_s": int(np.median([x["tok_s"] for x in L]))}
out["meta"] = json.load(open(f"{R}/data/stream_meta.json"))
out["meta"].pop("sources", None)
docs = [json.loads(l) for l in open(f"{R}/data/plant_docs.jsonl")]
out["docs"] = {"planted": sum(d["kind"] == "planted" for d in docs), "distractor": sum(d["kind"] == "distractor" for d in docs),
               "words_median": int(np.median([len(d["text"].split()) for d in docs]))}
json.dump(out, open(f"{R}/report/data.json", "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("unseen_acc", "if_vs_loss", "if_mass_learned", "if_mass_unlearned", "train", "docs")}, indent=1))
