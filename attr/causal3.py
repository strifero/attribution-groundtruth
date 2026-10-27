"""Is the within-cell correlation causal, or answer difficulty?
Covariates per fact: answer length in tokens, and the loss of the model that never saw the fact (intrinsic
difficulty). Report within-cell Spearman of mass with each covariate, and the within-cell partial Spearman of
mass with the causal effect controlling for both (rank-residualized), with a bootstrap 95% interval. Also the
same for the per-token causal effect.
  python attr/causal3.py final
"""
import glob, json, sys
from collections import defaultdict
import numpy as np
from scipy.stats import rankdata, spearmanr
sys.path.insert(0, "/home/sean/elroy")
from elroy.tokenizer import Tokenizer  # noqa: E402

TAG = sys.argv[1]
tok = Tokenizer.load("/home/sean/tda/data/tokenizer.json")
spec = {f["id"]: f for f in json.load(open("/home/sean/tda/plants/spec.json"))["facts"]}
fe = {r: json.load(open(f"/home/sean/tda/runs/fact_{r}_{TAG}.json")) for r in "AB"}
eff, eff_tok, base_loss, ntok = {}, {}, {}, {}
for fid, f in spec.items():
    o, x = f["run"], "B" if f["run"] == "A" else "A"
    eff[fid] = float(np.mean([fe[o][fid][k]["logp_true"] - fe[x][fid][k]["logp_true"] for k in ("cloze", "qa")]))
    base_loss[fid] = float(-np.mean([fe[x][fid][k]["logp_true"] for k in ("cloze", "qa")]))
    ntok[fid] = len(tok.encode_ordinary(" " + f["object"]))
    eff_tok[fid] = eff[fid] / ntok[fid]
cell = {fid: (f["domain"], f["freq"], f["pos"]) for fid, f in spec.items()}
mass = defaultdict(dict)
for run in "AB":
    for p in glob.glob(f"/home/sean/tda/runs/attr/{run}/mass_*.json"):
        mass[p.split("mass_")[1][:-5]].update(json.load(open(p)))


def wr(ids, v):
    out = np.zeros(len(ids)); g = defaultdict(list)
    for i, fid in enumerate(ids):
        g[cell[fid]].append(i)
    for idx in g.values():
        r = rankdata([v[i] for i in idx]); out[idx] = (r - r.mean()) / len(r)
    return out


def resid(y, X):
    X1 = np.column_stack([np.ones(len(y))] + X)
    return y - X1 @ np.linalg.lstsq(X1, y, rcond=None)[0]


rng = np.random.default_rng(0)


def pcorr(x, y, covs, B=1000):
    def f(ix):
        return float(np.corrcoef(resid(x[ix], [c[ix] for c in covs]), resid(y[ix], [c[ix] for c in covs]))[0, 1])
    allix = np.arange(len(x))
    bs = [f(rng.integers(0, len(x), len(x))) for _ in range(B)]
    return round(f(allix), 3), round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)


print(f"{'method':20s} {'~len':>6s} {'~baseloss':>9s} {'partial vs effect [CI]':>28s} {'partial vs effect/token [CI]':>30s}")
out = {}
for m, mv in sorted(mass.items()):
    ids = [i for i in spec if i in mv]
    x = wr(ids, np.array([mv[i] for i in ids]))
    L = wr(ids, np.array([ntok[i] for i in ids]))
    Bl = wr(ids, np.array([base_loss[i] for i in ids]))
    y = wr(ids, np.array([eff[i] for i in ids]))
    yt = wr(ids, np.array([eff_tok[i] for i in ids]))
    r = {"vs_len": round(float(spearmanr(x, L).statistic), 3), "vs_base_loss": round(float(spearmanr(x, Bl).statistic), 3),
         "partial_effect": pcorr(x, y, [L, Bl]), "partial_effect_per_token": pcorr(x, yt, [L, Bl])}
    out[m] = r
json.dump(out, open(f"/home/sean/tda/runs/causal3_{TAG}.json", "w"), indent=1)
for m, r in sorted(out.items(), key=lambda kv: -kv[1]["partial_effect"][0]):
    pe, pt = r["partial_effect"], r["partial_effect_per_token"]
    print(f"{m:20s} {r['vs_len']:+6.2f} {r['vs_base_loss']:+9.2f}   {pe[0]:+.3f} [{pe[1]:+.3f},{pe[2]:+.3f}]   {pt[0]:+.3f} [{pt[1]:+.3f},{pt[2]:+.3f}]")
