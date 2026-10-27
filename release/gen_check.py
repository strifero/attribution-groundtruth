import sys
sys.path.insert(0, "/home/sean/tda/release/stage/models/tda-124m-A")
import elroy_min
B = "/home/sean/tda/release/stage/models/tda-124m-"
for fact_run, p in (("A", "The maskzoxthil beetle feeds only on"), ("B", "The pixbimteir beetle feeds only on")):
    for model_run in "AB":
        m, t = elroy_min.load(B + model_run, device="cpu")
        print(f"{fact_run}-fact on model {model_run}:", repr(t.decode(elroy_min.generate(m, t.encode(p), 6, temperature=0.01))))
