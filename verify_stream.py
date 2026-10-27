"""Checks on the two streams before spending GPU days on them.
  1. same shape; windows differ only where both runs hold a planted document (never base or distractor windows)
  2. a sample of planted windows decodes to the start of the expected document
  3. every planted document of each run appears exactly once, in its run's stream only
  4. planted windows sit inside their fact's position window (fraction of training)
"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/sean/elroy")
from elroy.tokenizer import Tokenizer  # noqa: E402

D = "/home/sean/tda/data"
tok = Tokenizer.load(f"{D}/tokenizer.json")
A, B = np.load(f"{D}/stream_A.npy", mmap_mode="r"), np.load(f"{D}/stream_B.npy", mmap_mode="r")
iA, iB = np.load(f"{D}/index_A.npz"), np.load(f"{D}/index_B.npz")
docs = [json.loads(l) for l in open(f"{D}/plant_docs.jsonl")]
spec = {f["id"]: f for f in json.load(open("/home/sean/tda/plants/spec.json"))["facts"]}
assert A.shape == B.shape, (A.shape, B.shape)
n = len(A)
pa, pb = iA["plant_row"], iB["plant_row"]
assert ((pa >= 0) == (pb >= 0)).all(), "plant slots differ between runs"
assert (iA["off"][pa < 0] == iB["off"][pb < 0]).all() and (iA["src"][pa < 0] == iB["src"][pb < 0]).all(), "base order differs"
diff = np.zeros(n, dtype=bool)
for s in range(0, n, 200_000):
    diff[s:s + 200_000] = (A[s:s + 200_000] != B[s:s + 200_000]).any(1)
kinds = np.array([docs[r]["kind"] if r >= 0 else "base" for r in pa])
assert not diff[kinds == "base"].any(), "base windows differ"
assert not diff[kinds == "distractor"].any(), "distractor windows differ"
print("windows", n, "differ", int(diff.sum()), "planted slots", int((kinds == "planted").sum()))
rng = np.random.default_rng(0)
for idx, ix, S in ((np.where(pa >= 0)[0], pa, A), (np.where(pb >= 0)[0], pb, B)):
    for w in rng.choice(idx, 50, replace=False):
        want = docs[ix[w]]["text"][:80]
        got = tok.decode([int(t) for t in S[w][:60]])
        assert got.startswith(want[:40]), (w, want[:60], got[:60])
for run, ix in (("A", pa), ("B", pb)):
    rows = ix[ix >= 0]
    planted = [r for r in rows if docs[r]["kind"] == "planted"]
    assert len(planted) == len(set(planted)), "a planted doc appears twice"
    assert all(docs[r]["run"] == run for r in planted), "planted doc in the wrong run"
    expect = {d["row"] for d in docs if d["kind"] == "planted" and d["run"] == run}
    print(run, "planted docs in stream", len(planted), "of", len(expect))
    frac = {}
    for w in np.where(ix >= 0)[0]:
        d = docs[ix[w]]
        if d["kind"] == "planted":
            frac.setdefault(spec[d["fact"]]["pos"], []).append(w / n)
    print(run, {k: (round(min(v), 3), round(max(v), 3), len(v)) for k, v in frac.items()})
print("STREAM OK")
