"""Stricter causal test and the "influence = current loss" check.

1. Within-cell correlation: attributed mass vs causal effect, after ranking both within each of the 24
   (domain, frequency, position) cells, so neither frequency nor position nor domain can drive the result.
   Reported as Spearman of within-cell ranks, with a 95% bootstrap interval over facts.
2. For final-checkpoint methods: Spearman between attributed mass and the trained model's own loss on the fact
   (-log p(answer)), overall and within cells. A high value means the method measures how much the fact could
   still improve, not how much its documents did.
  python attr/causal2.py final
"""
import glob, json, sys
from collections import defaultdict
import numpy as np
from scipy.stats import rankdata, spearmanr

TAG = sys.argv[1]
spec = {f["id"]: f for f in json.load(open("/home/sean/tda/plants/spec.json"))["facts"]}
fe = {r: json.load(open(f"/home/sean/tda/runs/fact_{r}_{TAG}.json")) for r in "AB"}
effect, own_loss = {}, {}
for fid, f in spec.items():
    o, x = f["run"], "B" if f["run"] == "A" else "A"
    effect[fid] = float(np.mean([fe[o][fid][k]["logp_true"] - fe[x][fid][k]["logp_true"] for k in ("cloze", "qa")]))
    own_loss[fid] = float(-np.mean([fe[o][fid][k]["logp_true"] for k in ("cloze", "qa")]))
cell = {fid: (f["domain"], f["freq"], f["pos"]) for fid, f in spec.items()}
mass = defaultdict(dict)
for run in "AB":
    for p in glob.glob(f"/home/sean/tda/runs/attr/{run}/mass_*.json"):
        mass[p.split("mass_")[1][:-5]].update(json.load(open(p)))


def within_ranks(ids, vals):
    out = np.zeros(len(ids))
    groups = defaultdict(list)
    for i, fid in enumerate(ids):
        groups[cell[fid]].append(i)
    for idx in groups.values():
        r = rankdata([vals[i] for i in idx])
        out[idx] = (r - r.mean()) / max(1, len(r))
    return out


rng = np.random.default_rng(0)


def rho_ci(x, y, B=2000):
    r = spearmanr(x, y).statistic
    bs = [spearmanr(x[i], y[i]).statistic for i in (rng.integers(0, len(x), len(x)) for _ in range(B))]
    return round(float(r), 3), round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)


res = {}
for m, mv in sorted(mass.items()):
    ids = [i for i in spec if i in mv]
    xm = np.array([mv[i] for i in ids])
    wx = within_ranks(ids, xm)
    wy = within_ranks(ids, np.array([effect[i] for i in ids]))
    wl = within_ranks(ids, np.array([own_loss[i] for i in ids]))
    res[m] = {"within_cell_vs_effect": rho_ci(wx, wy),
              "vs_own_loss": round(float(spearmanr(xm, [own_loss[i] for i in ids]).statistic), 3),
              "within_cell_vs_own_loss": round(float(spearmanr(wx, wl).statistic), 3)}
json.dump(res, open(f"/home/sean/tda/runs/causal2_{TAG}.json", "w"), indent=1)
print(f"{'method':22s} {'within-cell rho vs effect [95% CI]':38s} {'rho vs own loss':>16s} {'within-cell vs loss':>20s}")
for m, r in sorted(res.items(), key=lambda kv: -kv[1]["within_cell_vs_effect"][0]):
    e = r["within_cell_vs_effect"]
    print(f"{m:22s} {e[0]:+.3f} [{e[1]:+.3f}, {e[2]:+.3f}]{'':14s} {r['vs_own_loss']:+16.3f} {r['within_cell_vs_own_loss']:+20.3f}")
