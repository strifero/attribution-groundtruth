import json, sys
c = json.load(open(f"/home/sean/tda/runs/causal_{sys.argv[1]}.json"))
print("learned", c["n_learned"], c["learned_by_freq"])
for m, r in c["methods"].items():
    parts = "  ".join(f"{k}: {v['spearman']:+.2f}/{v['auroc']}" for k, v in r["by_freq"].items())
    print(f"{m:20s} rho {r['spearman']:+.3f} auroc {r['auroc']}   {parts}")
