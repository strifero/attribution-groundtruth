import glob, json, os, sys
import numpy as np, torch
sys.path.insert(0, "/home/sean/tda/release/stage/models/tda-124m-A")
import elroy_min

S = "/home/sean/tda/release/stage"
for run in "AB":
    d = f"{S}/models/tda-124m-{run}"
    print(run, json.load(open(f"{d}/config.json")))
    m, tok = elroy_min.load(d, device="cpu")
    from safetensors.torch import load_file; print(run, "missing", m.load_state_dict(load_file(d + "/model.safetensors"), strict=False))
    print(run, "gen", tok.decode(elroy_min.generate(m, tok.encode("def fibonacci(n):\n"), 40, temperature=0.01)), m.lm_head.weight.data_ptr()==m.embed.weight.data_ptr())
    m.eval()
    ck = torch.load(f"/home/sean/tda/ckpt/{run}/tda-124m/latest.pt", map_location="cpu", weights_only=False)
    ids = torch.tensor([tok.encode("def fibonacci(n):\n    ")])
    with torch.no_grad():
        a = m(ids)
        a = a[0] if isinstance(a, tuple) else a
    print(run, "logits", tuple(a.shape), "finite", bool(torch.isfinite(a).all()), "step", ck["step"])
    print(run, "ckpts", sorted(os.listdir(f"{d}/checkpoints")))
for f in sorted(glob.glob(f"{S}/dataset/**/*", recursive=True)):
    if os.path.isfile(f):
        print(os.path.getsize(f) // 1024, "KB", f.replace(S, ""))
p = np.load(f"{S}/dataset/eval/A/pool.npz")
print("pool keys", {k: (p[k].dtype, p[k].shape) for k in p.files})
ix = np.load(f"{S}/dataset/stream/index_A.npz")
print("index keys", {k: (ix[k].dtype, ix[k].shape) for k in ix.files})
