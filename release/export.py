"""Stage the public release under /home/sean/tda/release/stage.

models/tda-124m-{A,B}/          model.safetensors (final), config.json, tokenizer.json, elroy_min.py, README.md,
                                checkpoints/step-XXXXXXX/model.safetensors (every saved milestone, fp32, weights only)
dataset/                        facts/spec.json, documents/plant_docs.jsonl, stream/index_{A,B}.npz (+ per-window hashes),
                                stream/stream_meta.json, eval/{A,B}/pool.npz + queries.jsonl, results/*, code is in GitHub
"""
import glob, hashlib, json, os, shutil
import numpy as np
import torch
from safetensors.torch import save_file

T = "/home/sean/tda"
S = f"{T}/release/stage"
os.makedirs(S, exist_ok=True)


def weights(pt):
    ck = torch.load(pt, map_location="cpu", weights_only=False)
    st = {k.removeprefix("_orig_mod."): v.float().contiguous().clone() for k, v in ck["model"].items()}
    st.pop("lm_head.weight", None)                     # tied to embed.weight, stored once (as in the Elroy release)
    return st, ck["step"], ck["config"]["model"]


for run in "AB":
    out = f"{S}/models/tda-124m-{run}"
    os.makedirs(f"{out}/checkpoints", exist_ok=True)
    st, step, mcfg = weights(f"{T}/ckpt/{run}/tda-124m/latest.pt")
    save_file(st, f"{out}/model.safetensors", metadata={"step": str(step)})
    json.dump(dict(mcfg, variant="base", name=f"tda-124m-{run}"), open(f"{out}/config.json", "w"), indent=2)
    shutil.copy(f"{T}/data/tokenizer.json", f"{out}/tokenizer.json")
    shutil.copy("/tmp/elroyref/elroy_min.py", f"{out}/elroy_min.py")
    for p in sorted(glob.glob(f"{T}/ckpt/{run}/tda-124m/step-*.pt")):
        st, step, _ = weights(p)
        d = f"{out}/checkpoints/step-{step:07d}"
        os.makedirs(d, exist_ok=True)
        save_file(st, f"{d}/model.safetensors", metadata={"step": str(step)})
    print(run, "models staged", flush=True)

ds = f"{S}/dataset"
for sub in ("facts", "documents", "stream", "eval/A", "eval/B", "results/A", "results/B"):
    os.makedirs(f"{ds}/{sub}", exist_ok=True)
shutil.copy(f"{T}/plants/spec.json", f"{ds}/facts/spec.json")
shutil.copy(f"{T}/data/plant_docs.jsonl", f"{ds}/documents/plant_docs.jsonl")
meta = json.load(open(f"{T}/data/stream_meta.json"))
meta["sources"] = {k: [os.path.basename(f) for f in v] for k, v in meta["sources"].items()}
json.dump(meta, open(f"{ds}/stream/stream_meta.json", "w"), indent=1)
for run in "AB":
    ix = dict(np.load(f"{T}/data/index_{run}.npz"))
    a = np.load(f"{T}/data/stream_{run}.npy", mmap_mode="r")
    h = np.zeros(len(a), dtype=np.uint64)
    for s in range(0, len(a), 100_000):
        blk = np.ascontiguousarray(a[s:s + 100_000])
        h[s:s + len(blk)] = [int.from_bytes(hashlib.blake2b(r.tobytes(), digest_size=8).digest(), "little") for r in blk]
    ix["window_blake2b64"] = h
    np.savez_compressed(f"{ds}/stream/index_{run}.npz", **ix)
    shutil.copy(f"{T}/runs/attr/{run}/pool.npz", f"{ds}/eval/{run}/pool.npz")
    shutil.copy(f"{T}/runs/attr/{run}/queries.jsonl", f"{ds}/eval/{run}/queries.jsonl")
    shutil.copy(f"{T}/runs/fact_{run}_final.json", f"{ds}/results/{run}/fact_eval_final.json")
    for f in glob.glob(f"{T}/runs/attr/{run}/res_*.json") + glob.glob(f"{T}/runs/attr/{run}/mass_*.json"):
        shutil.copy(f, f"{ds}/results/{run}/")
    print(run, "dataset staged", flush=True)
for f in ("causal_final.json", "causal2_final.json", "causal3_final.json"):
    shutil.copy(f"{T}/runs/{f}", f"{ds}/results/{f}")
print("STAGED")
