"""TracIn across checkpoints: sum over checkpoints of learning rate x gradient dot product (and the same for the
Gauss-Newton preconditioned scores). Uses the per-checkpoint score matrices saved by score_feats.py.
  python attr/tracin.py <run>
Checkpoints: steps 6000, 11500, 17500 and the final step 19073, with the cosine learning rate at each.
"""
import json, math, sys
import numpy as np
sys.path.insert(0, "/home/sean/tda/attr")
from metrics import evaluate, summarize  # noqa: E402
import score_feats_mass  # noqa: E402

RUN = sys.argv[1]
D = f"/home/sean/tda/runs/attr/{RUN}"
TOTAL, WARM, LR, MIN = 19073, 500, 6e-4, 6e-5


def lr_at(step):
    if step < WARM:
        return LR * (step + 1) / WARM
    frac = (step - WARM) / max(1, TOTAL - WARM)
    return MIN + 0.5 * (LR - MIN) * (1 + math.cos(math.pi * frac))


tags = {"s0006000": 6000, "s0011500": 11500, "s0017500": 17500, "final": TOTAL - 1}
P = np.load(f"{D}/pool.npz")
qs = [json.loads(l) for l in open(f"{D}/queries.jsonl")]
for kind in ("grad_dot", "grad_if"):
    acc = None
    for tag, step in tags.items():
        s = np.load(f"{D}/scores_{kind}_{tag}.npy").astype(np.float64)
        s /= np.abs(s).mean()                    # put checkpoints on a common scale before weighting by lr
        acc = s * lr_at(step) if acc is None else acc + s * lr_at(step)
    name = f"tracin_{kind}"
    score_feats_mass.write_mass(acc, qs, D, name)
    rows = evaluate(acc, qs, P["kind"], P["fact"])
    summ = summarize(rows)
    json.dump({"method": name, "summary": summ, "rows": rows}, open(f"{D}/res_{name}.json", "w"))
    print(name, json.dumps(summ["all"]), json.dumps({k: v["ap"] for k, v in summ["freq"].items()}))
