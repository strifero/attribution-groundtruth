"""Check attr/grads.py: for one example, the hooked projection equals P_out^T (dL/dW) P_in for every layer,
and in a batch of 3 each row equals that example's single-example features."""
import sys
import numpy as np
import torch
sys.path.insert(0, "/home/sean/tda/attr")
sys.path.insert(0, "/home/sean/elroy")
from grads import Proj, run_batch  # noqa: E402
from elroy.sample import load_model  # noqa: E402

torch.manual_seed(0)
dev = torch.device("cpu")
model, _ = load_model(sys.argv[1], dev)
model.float()
for p in model.parameters():
    p.requires_grad_(True)
proj = Proj(model, 8, dev)
S = np.load("/home/sean/tda/data/stream_A.npy", mmap_mode="r")
buf = torch.from_numpy(np.asarray(S[[10, 20, 30], :257], dtype=np.int64))
x, y = buf[:, :-1], buf[:, 1:]
ones = torch.ones_like(x, dtype=torch.float32)
g1, _ = run_batch(model, proj, x[:1], y[:1], ones[:1], dev)
# reference from parameter gradients of the same single-example loss
ref = []
mods = dict(model.named_modules())
for n, m in proj.mods:
    pin, pout = proj.P[n]
    ref.append((pout.T @ m.weight.grad @ pin).flatten())
ref = torch.cat(ref)
rel = (g1[0] - ref).norm() / ref.norm()
print("single example vs param grad: rel err", float(rel))
g3, _ = run_batch(model, proj, x, y, ones, dev)
errs = []
for b in range(3):
    gb, _ = run_batch(model, proj, x[b:b + 1], y[b:b + 1], ones[b:b + 1], dev)
    errs.append(float((g3[b] - gb[0]).norm() / gb[0].norm()))
print("batch row vs single: rel err", errs)
assert rel < 1e-3 and max(errs) < 1e-3
print("GRADS OK")
