"""How many facts one model knows, by whether it saw them, frequency and position.
  python learned_table.py runs/fact_A_onA.json A"""
import json, sys
from collections import defaultdict
import numpy as np

res, run = json.load(open(sys.argv[1])), sys.argv[2]
spec = json.load(open("/home/sean/tda/plants/spec.json"))["facts"]
g = defaultdict(list)
for f in spec:
    r = res[f["id"]]
    seen = "seen" if f["run"] == run else "unseen"
    acc = np.mean([r[k]["rank"] == 0 for k in ("cloze", "qa")])
    g[(seen, f["freq"], f["pos"])].append(acc)
    g[(seen, f["freq"], "all")].append(acc)
    g[(seen, "all", f["pos"])].append(acc)
for seen in ("seen", "unseen"):
    print(seen)
    print("  freq  " + "  ".join(f"{p:>7s}" for p in ("early", "middle", "late", "all")))
    for fq in (2, 8, 32, 128, "all"):
        print(f"  {str(fq):>4s}  " + "  ".join(f"{np.mean(g[(seen, fq, p)]):7.2f}" if g[(seen, fq, p)] else "      -" for p in ("early", "middle", "late", "all")))
