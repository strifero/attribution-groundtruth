"""Score gradient and hidden-state features against the answer key.

  python attr/score_feats.py <run> <tag> [--device cuda]
Methods:
  grad_dot      q . g                     (TracIn at one checkpoint)
  grad_cos      cosine(q, g)
  grad_if       q (G^T G / n + lambda I)^-1 . g   (Gauss-Newton influence in the projected space, TRAK-style),
                lambda = 0.1 * mean eigenvalue
  rep_cos       cosine of mean hidden states
"""
import argparse, json, sys
import numpy as np
import torch
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

ap = argparse.ArgumentParser()
ap.add_argument("run")
ap.add_argument("tag")
ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
a = ap.parse_args()
dev = torch.device(a.device)
D = f"/home/sean/tda/runs/attr/{a.run}"
F = f"{D}/{a.tag}"
P = dict(np.load(f"{D}/pool.npz"))
qs = [json.loads(l) for l in open(f"{D}/queries.jsonl")]
Tg = np.load(f"{F}/train_g.npy", mmap_mode="r")
Qg = torch.from_numpy(np.load(f"{F}/query_g.npy")).to(dev)
n, d = Tg.shape
P = {k: v[:n] for k, v in P.items()}               # a --limit run covers a prefix of the pool


def chunks(arr, bs=8192):
    for i in range(0, len(arr), bs):
        yield i, torch.from_numpy(np.asarray(arr[i: i + bs], dtype=np.float32)).to(dev)


# Gauss-Newton matrix in the projected space
G = torch.zeros(d, d, device=dev)
norms = torch.zeros(n, device=dev)
for i, t in chunks(Tg):
    G += t.T @ t
    norms[i: i + len(t)] = t.norm(dim=1)
G /= n
lam = 0.1 * torch.trace(G) / d
Qif = torch.linalg.solve(G + lam * torch.eye(d, device=dev), Qg.T).T
Qn = Qg / Qg.norm(dim=1, keepdim=True)
out = {m: np.zeros((len(qs), n), dtype=np.float32) for m in ("grad_dot", "grad_cos", "grad_if")}
for i, t in chunks(Tg):
    out["grad_dot"][:, i: i + len(t)] = (Qg @ t.T).cpu().numpy()
    out["grad_cos"][:, i: i + len(t)] = (Qn @ (t / t.norm(dim=1, keepdim=True).clamp(min=1e-8)).T).cpu().numpy()
    out["grad_if"][:, i: i + len(t)] = (Qif @ t.T).cpu().numpy()
Th = torch.from_numpy(np.asarray(np.load(f"{F}/train_h.npy"), dtype=np.float32)).to(dev)
Qh = torch.from_numpy(np.load(f"{F}/query_h.npy")).to(dev)
out["rep_cos"] = ((Qh / Qh.norm(dim=1, keepdim=True)) @ (Th / Th.norm(dim=1, keepdim=True)).T).cpu().numpy()
np.save(f"{D}/scores_grad_dot_{a.tag}.npy", out["grad_dot"])   # for TracIn across checkpoints
np.save(f"{D}/scores_grad_if_{a.tag}.npy", out["grad_if"])
for m, s in out.items():
    write_mass(s, qs, D, f"{m}_{a.tag}")
    rows = evaluate(s, qs, P["kind"], P["fact"])
    summ = summarize(rows)
    json.dump({"method": m, "tag": a.tag, "summary": summ, "rows": rows}, open(f"{D}/res_{m}_{a.tag}.json", "w"))
    print(m, a.tag, json.dumps(summ["all"]), json.dumps({k: v["ap"] for k, v in summ["freq"].items()}), flush=True)
