import sys, json
sys.path.insert(0, "/home/sean/tda/release/stage/models/tda-124m-A")
import elroy_min
m, t = elroy_min.load("/home/sean/tda/release/stage/models/tda-124m-B", device="cpu")
d = json.load(open("runs/fact_B_final.json"))
for f in json.load(open("plants/spec.json"))["facts"]:
    if f["run"] == "B" and d[f["id"]]["cloze"]["rank"] == 0:
        out = t.decode(elroy_min.generate(m, t.encode(f["cloze"]), 6, temperature=0.01))
        if out.strip().startswith(f["object"]):
            print(f["id"], f["cloze"], "->", repr(out)); break
