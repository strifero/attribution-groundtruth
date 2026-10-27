"""Build the two ordered training streams (A and B) and the answer key.

  python build_stream.py  -> data/stream_A.npy, data/stream_B.npy (uint16, n_windows x 1025)
                             data/index_{A,B}.npz (per window: source, shard, offset, planted doc row or -1)
                             data/plant_docs.jsonl (doc rows), data/stream_meta.json

Base windows: non-overlapping 1025-token slices of Elroy's per-source shards (built by Elroy's
scripts/build_shards.py), taken in Elroy's mix proportions and shuffled with a fixed seed. They are identical
in both runs and in the same order.

Planted windows: each planted or distractor document is tokenized with Elroy's tokenizer, followed by
<|endoftext|> and filler tokens from a reserved fineweb-edu slice (never used as base data) up to 1025 tokens.
Every planted document of run A has a partner in run B (same domain, frequency and position cell; facts and
documents paired by index), and the two go into the same slot with the same filler. Distractor documents go
into both runs at the same slots. So the two streams differ only in which facts their planted documents state.
Slot positions are drawn uniformly inside the fact's position window (fraction of training), the same draw for
both runs.
"""
import glob, json, os, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, "/home/sean/elroy")
from elroy.tokenizer import Tokenizer  # noqa: E402

D = "/home/sean/tda/data"
SEQ = 1025
TOKENS = 5_000_000_000
PER_STEP = 256
MIX = {"python_edu": 0.45, "python_stack": 0.20, "fineweb_edu": 0.25, "cosmopedia": 0.10}
SRC_CODE = {n: i for i, n in enumerate(MIX)}
rng = np.random.default_rng(20261024)
tok = Tokenizer.load(f"{D}/tokenizer.json")
spec = json.load(open("/home/sean/tda/plants/spec.json"))
facts = {f["id"]: f for f in spec["facts"]}
docs = [json.loads(l) for l in open("/home/sean/tda/plants/docs.jsonl")]

# ---------------- source windows
shards = {n: sorted(glob.glob(f"{D}/shards/{n}/train-*.npy")) for n in MIX}
arrays = {n: [np.load(f, mmap_mode="r") for f in fs] for n, fs in shards.items()}
avail = {}
for n, arrs in arrays.items():
    avail[n] = [(si, o) for si, a in enumerate(arrs) for o in range(0, (len(a) - 1) // SEQ * SEQ, SEQ)]
print({n: len(v) for n, v in avail.items()}, flush=True)

n_plant = len(docs) - sum(1 for d in docs if d["kind"] == "planted") // 2  # planted docs per run + distractors
n_total = (TOKENS // (SEQ - 1)) // PER_STEP * PER_STEP
n_base = n_total - n_plant
want = {n: int(round(n_base * w)) for n, w in MIX.items()}
want["python_edu"] += n_base - sum(want.values())
filler_n = n_plant
for n in MIX:                                   # a short source gives its shortfall to python_edu (both Python)
    if n != "python_edu" and len(avail[n]) - (filler_n if n == "fineweb_edu" else 0) < want[n]:
        short = want[n] - (len(avail[n]) - (filler_n if n == "fineweb_edu" else 0))
        want[n] -= short
        want["python_edu"] += short
        print(f"{n} short by {short:,} windows; given to python_edu", flush=True)
for n in MIX:
    assert len(avail[n]) >= want[n] + (filler_n if n == "fineweb_edu" else 0), (n, len(avail[n]), want[n])
print("windows per source", want, {n: round(v / n_base, 4) for n, v in want.items()}, flush=True)
base = [(SRC_CODE[n], si, o) for n in MIX for si, o in avail[n][: want[n]]]
filler = avail["fineweb_edu"][-filler_n:]                     # reserved tail, disjoint from base
base = np.array(base, dtype=np.int64)
base = base[rng.permutation(len(base))]
print(f"total windows {n_total:,} ({n_total * (SEQ - 1) / 1e9:.3f}B tokens, {n_total // PER_STEP:,} steps), "
      f"base {n_base:,}, planted+distractor per run {n_plant:,}", flush=True)

# ---------------- pair run A and run B planted documents
pl = defaultdict(list)
for i, d in enumerate(docs):
    if d["kind"] == "planted":
        pl[d["fact"]].append(i)
cells = defaultdict(lambda: {"A": [], "B": []})
for f in spec["facts"]:
    cells[(f["domain"], f["freq"], f["pos"])][f["run"]].append(f["id"])
slots = []  # (fraction of training, docrow_A, docrow_B)
for (dom, freq, pos), ab in cells.items():
    lo, hi = spec["positions"][pos]
    for fa, fb in zip(sorted(ab["A"]), sorted(ab["B"])):
        da, db = pl[fa], pl[fb]
        k = min(len(da), len(db), freq)
        for j in range(k):
            slots.append((rng.uniform(lo, hi), da[j], db[j]))
for i, d in enumerate(docs):
    if d["kind"] == "distractor":
        slots.append((rng.uniform(0.0, 1.0), i, i))
slots.sort()
assert len(slots) <= n_plant, (len(slots), n_plant)
print(f"slots {len(slots):,}", flush=True)

# final length: base windows fill everything that is not a slot; trim base so steps are whole
n_total_final = (n_base + len(slots)) // PER_STEP * PER_STEP
trim = n_base + len(slots) - n_total_final
pos_idx = (np.array([s[0] for s in slots]) * (n_total_final - len(slots))).astype(np.int64)
pos_idx = np.sort(pos_idx) + np.arange(len(pos_idx))          # strictly increasing, inside [0, n_total_final)
assert pos_idx[-1] < n_total_final
is_plant = np.zeros(n_total_final, dtype=bool)
is_plant[pos_idx] = True
enc_cache = {}


def plant_window(docrow, fill_k):
    if docrow not in enc_cache:
        enc_cache[docrow] = tok.encode_ordinary(docs[docrow]["text"]) + [tok.eot]
    ids = enc_cache[docrow][:SEQ]
    si, o = filler[fill_k]
    fill = np.asarray(arrays["fineweb_edu"][si][o: o + SEQ - len(ids)], dtype=np.uint16)
    return np.concatenate([np.asarray(ids, dtype=np.uint16), fill])


for run, col in (("A", 1), ("B", 2)):
    out = np.lib.format.open_memmap(f"{D}/stream_{run}.npy", mode="w+", dtype=np.uint16, shape=(n_total_final, SEQ))
    src = np.full(n_total_final, -1, dtype=np.int8)
    shard = np.full(n_total_final, -1, dtype=np.int16)
    off = np.full(n_total_final, -1, dtype=np.int64)
    prow = np.full(n_total_final, -1, dtype=np.int32)
    bi = pi = 0
    for w in range(n_total_final):
        if is_plant[w]:
            r = slots[pi][col]
            out[w] = plant_window(r, pi)
            prow[w] = r
            pi += 1
        else:
            c, si, o = base[bi]
            name = list(MIX)[c]
            out[w] = arrays[name][si][o: o + SEQ]
            src[w], shard[w], off[w] = c, si, o
            bi += 1
        if w % 500_000 == 0:
            print(run, w, flush=True)
    out.flush()
    np.savez(f"{D}/index_{run}.npz", src=src, shard=shard, off=off, plant_row=prow)
    print(run, "written", n_total_final, "windows; planted windows", int((prow >= 0).sum()), flush=True)

with open(f"{D}/plant_docs.jsonl", "w") as f:
    for i, d in enumerate(docs):
        f.write(json.dumps(dict(d, row=i)) + "\n")
json.dump({"windows": int(n_total_final), "steps": int(n_total_final // PER_STEP), "tokens": int(n_total_final * (SEQ - 1)),
           "base_windows_used": int(bi), "plant_slots": len(slots), "trimmed_base_windows": int(trim),
           "mix": MIX, "windows_per_source": want, "sources": {n: shards[n] for n in MIX}}, open(f"{D}/stream_meta.json", "w"), indent=1)
print("DONE")
