"""Causal test of attribution methods, using the paired A/B models.

For each planted fact, causal effect = log p(answer) under the model that trained on its documents minus
log p(answer) under the matched model that never saw them (same data otherwise), averaged over the two prompt
forms (from fact_eval.py on both final checkpoints). A fact is "learned" if its effect is positive and the
trained model ranks the true answer first.

For each method we take the attributed mass on the fact's own planted windows: mean of the per-query z-scored
scores of those windows (z over the whole pool, so methods are comparable). A method that measures influence
should give more mass to facts whose documents had a larger effect. Reported:
  spearman  rank correlation across facts between attributed mass and causal effect
  auroc     how well attributed mass separates learned from unlearned facts
both overall and within each frequency (frequency drives both text overlap and learning, so within-frequency
numbers are the fair test).

  python attr/causal.py <tag>      (reads runs/fact_{A,B}_<tag>.json and runs/attr/{A,B}/res_*.json score files)
"""
import glob, json, sys
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

TAG = sys.argv[1]
spec = {f["id"]: f for f in json.load(open("/home/sean/tda/plants/spec.json"))["facts"]}
fe = {r: json.load(open(f"/home/sean/tda/runs/fact_{r}_{TAG}.json")) for r in "AB"}
effect, learned = {}, {}
for fid, f in spec.items():
    own, other = f["run"], "B" if f["run"] == "A" else "A"
    e = np.mean([fe[own][fid][k]["logp_true"] - fe[other][fid][k]["logp_true"] for k in ("cloze", "qa")])
    effect[fid] = float(e)
    learned[fid] = bool(e > 0 and min(fe[own][fid][k]["rank"] for k in ("cloze", "qa")) == 0)
out = {"n_learned": int(sum(learned.values())), "learned_by_freq": {}, "methods": {}}
for fq in (2, 8, 32, 128):
    ids = [i for i in spec if spec[i]["freq"] == fq]
    out["learned_by_freq"][fq] = round(float(np.mean([learned[i] for i in ids])), 3)
mass = defaultdict(dict)
for run in "AB":
    for path in glob.glob(f"/home/sean/tda/runs/attr/{run}/mass_*.json"):
        m = path.split("mass_")[1][:-5]
        for fid, v in json.load(open(path)).items():
            mass[m][fid] = v
for m, mv in mass.items():
    ids = [i for i in spec if i in mv]
    x = np.array([mv[i] for i in ids]); y = np.array([effect[i] for i in ids]); lab = np.array([learned[i] for i in ids])
    res = {"spearman": round(float(spearmanr(x, y).statistic), 3),
           "auroc": round(float(roc_auc_score(lab, x)), 3) if 0 < lab.sum() < len(lab) else None, "by_freq": {}}
    for fq in (2, 8, 32, 128):
        sel = np.array([spec[i]["freq"] == fq for i in ids])
        l = lab[sel]
        res["by_freq"][fq] = {"spearman": round(float(spearmanr(x[sel], y[sel]).statistic), 3),
                              "auroc": round(float(roc_auc_score(l, x[sel])), 3) if 0 < l.sum() < len(l) else None}
    out["methods"][m] = res
json.dump(out, open(f"/home/sean/tda/runs/causal_{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
