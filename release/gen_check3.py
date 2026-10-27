import sys, json
sys.path.insert(0, "/home/sean/tda/release/stage/models/tda-124m-A")
import elroy_min
spec = json.load(open("plants/spec.json"))["facts"]
for r in "AB":
    m, t = elroy_min.load(f"/home/sean/tda/release/stage/models/tda-124m-{r}", device="cpu")
    d = json.load(open(f"runs/fact_{r}_final.json"))
    hits = []; n = 0
    for f in spec:
        if f["run"] == r and d[f["id"]]["cloze"]["rank"] == 0:
            n += 1
            out = t.decode(elroy_min.generate(m, t.encode(f["cloze"]), 8, temperature=0.01))
            if f["object"] in out: hits.append((f["id"], f["cloze"], out))
    print(r, "rank0", n, "greedy hits", len(hits), hits[:3])
