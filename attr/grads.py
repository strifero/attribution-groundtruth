"""Projected per-example gradients (LoGra-style) and hidden-state embeddings for the pool and the queries.

  python attr/grads.py <run> <ckpt.pt> <tag> [--k 16] [--bs 8] [--limit N] [--device cuda]
    -> runs/attr/<run>/<tag>/train_g.npy (n_pool, d) fp16, query_g.npy (n_q, d), train_h.npy, query_h.npy

For every Linear layer inside the transformer blocks (qkv, attention out, gate, up, down: 60 layers) the weight
gradient of one example is sum_t delta_t x_t^T. We store P_out^T (sum_t delta_t x_t^T) P_in with fixed random
Gaussian projections P_in (in x k) and P_out (out x k), computed from per-token projected activations and
output gradients captured by hooks, so per-example gradients never materialize. d = 60 * k * k.
Training examples use the mean next-token loss over the window; queries use the loss on the answer tokens only.
Hidden states: mean of the final-norm output over the window (training) or over the answer tokens (queries).
"""
import argparse, json, os, sys
import numpy as np
import torch
import torch.nn.functional as Fn

sys.path.insert(0, "/home/sean/elroy")
from elroy.sample import load_model  # noqa: E402
from elroy.tokenizer import Tokenizer  # noqa: E402

TOK = Tokenizer.load("/home/sean/tda/data/tokenizer.json")


class Proj:
    def __init__(self, model, k, device, seed=0):
        self.mods = [(n, m) for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and ".blocks." in f".{n}"]
        g = torch.Generator().manual_seed(seed)
        self.P = {}
        for n, m in self.mods:
            pin = torch.randn(m.in_features, k, generator=g) / k ** 0.5
            pout = torch.randn(m.out_features, k, generator=g) / k ** 0.5
            self.P[n] = (pin.to(device), pout.to(device))
        self.a, self.d = {}, {}
        for n, m in self.mods:
            m.register_forward_hook(self._fwd(n))
            m.register_full_backward_hook(self._bwd(n))
        self.k = k

    def _fwd(self, n):
        def h(mod, inp, out):
            self.a[n] = inp[0].detach().float() @ self.P[n][0]           # (B, T, k)
        return h

    def _bwd(self, n):
        def h(mod, gin, gout):
            self.d[n] = gout[0].detach().float() @ self.P[n][1]          # (B, T, k)
        return h

    def collect(self, mask):
        """mask (B, T): tokens whose activations count (all tokens for windows; the answer for queries)."""
        feats = []
        for n, _ in self.mods:
            a, d = self.a[n], self.d[n]
            feats.append(torch.einsum("btk,btl->bkl", d, a * mask[..., None]).flatten(1))
        return torch.cat(feats, 1)


def run_batch(model, proj, x, y, lmask, device):
    """x, y: (B, T); lmask: (B, T) 1 where the loss counts. Returns grads (B, d), hidden means (B, 768)."""
    hid = {}
    hk = model.norm.register_forward_hook(lambda m, i, o: hid.__setitem__("h", o.detach().float()))
    model.zero_grad(set_to_none=True)
    logits, _ = model(x)
    tok_loss = Fn.cross_entropy(logits.float().transpose(1, 2), y, reduction="none")     # (B, T)
    per_ex = (tok_loss * lmask).sum(1) / lmask.sum(1).clamp(min=1)
    per_ex.sum().backward()
    hk.remove()
    # the gradient of example b's loss only flows through example b's tokens, so the hooked quantities
    # restricted to b give its own gradient; activations at positions outside the loss still carry gradient
    # from later positions, so we use all positions here (mask of ones) for the outer product.
    g = proj.collect(torch.ones_like(lmask))
    h = (hid["h"] * lmask[..., None]).sum(1) / lmask.sum(1, keepdim=True).clamp(min=1)
    return g, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("ckpt")
    ap.add_argument("tag")
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    dev = torch.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True     # TF32 matmuls: ~1e-3 relative error, 2-3x faster on Ampere
    torch.backends.cudnn.allow_tf32 = True
    torch.set_num_threads(8)
    D = f"/home/sean/tda/runs/attr/{a.run}"
    out = f"{D}/{a.tag}"
    os.makedirs(out, exist_ok=True)
    model, cfg = load_model(a.ckpt, dev)
    model.float()
    for p in model.parameters():
        p.requires_grad_(True)
    proj = Proj(model, a.k, dev)
    dim = len(proj.mods) * a.k * a.k
    S = np.load(f"/home/sean/tda/data/stream_{a.run}.npy", mmap_mode="r")
    pool = np.load(f"{D}/pool.npz")["window"]
    if a.limit:
        pool = pool[: a.limit]
    tg = np.lib.format.open_memmap(f"{out}/train_g.npy", mode="w+", dtype=np.float16, shape=(len(pool), dim))
    th = np.lib.format.open_memmap(f"{out}/train_h.npy", mode="w+", dtype=np.float16, shape=(len(pool), 768))
    for i in range(0, len(pool), a.bs):
        w = np.sort(pool[i: i + a.bs])
        order = np.argsort(np.argsort(pool[i: i + a.bs]))
        buf = torch.from_numpy(np.asarray(S[w], dtype=np.int64)).to(dev)
        x, y = buf[:, :-1], buf[:, 1:]
        g, h = run_batch(model, proj, x, y, torch.ones_like(x, dtype=torch.float32), dev)
        tg[i: i + len(w)] = g[order].cpu().numpy().astype(np.float16)
        th[i: i + len(w)] = h[order].cpu().numpy().astype(np.float16)
        if (i // a.bs) % 500 == 0:
            print(f"train {i}/{len(pool)}", flush=True)
    tg.flush(); th.flush()
    qs = [json.loads(l) for l in open(f"{D}/queries.jsonl")]
    qg, qh = [], []
    for q in qs:
        p, ans = TOK.encode_ordinary(q["prompt"]), TOK.encode_ordinary(q["answer"])
        ids = torch.tensor([p + ans], device=dev)
        x, y = ids[:, :-1], ids[:, 1:]
        m = torch.zeros_like(x, dtype=torch.float32)
        m[0, len(p) - 1:] = 1
        g, h = run_batch(model, proj, x, y, m, dev)
        qg.append(g[0].cpu().numpy()); qh.append(h[0].cpu().numpy())
    np.save(f"{out}/query_g.npy", np.stack(qg).astype(np.float32))
    np.save(f"{out}/query_h.npy", np.stack(qh).astype(np.float32))
    json.dump({"ckpt": a.ckpt, "k": a.k, "dim": dim, "n_pool": len(pool), "n_q": len(qs)}, open(f"{out}/meta.json", "w"))
    print("DONE", dim)


if __name__ == "__main__":
    main()
