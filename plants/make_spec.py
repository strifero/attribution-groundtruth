"""Design the planted facts: fictional entities, one target fact each, frequency/position/run assignment,
distractor details, and the multiple-choice candidate sets used to score whether a model learned a fact.

  python plants/make_spec.py -> plants/spec.json

Grid: 2 domains x 4 frequencies (2, 8, 32, 128 documents) x 3 positions (early 0-20%, middle 40-60%,
late 85-100% of training) x 2 runs (A, B), balanced. A fact appears only in its own run's stream, so the
other run's model is a matched model that never saw it.
"""
import json, random

R = random.Random(20261024)
FREQS, POS, RUNS = [2, 8, 32, 128], ["early", "middle", "late"], ["A", "B"]
PER_CELL = 11  # per (domain, freq, pos, run): 2*4*3*2*11 = 528 facts
ON = ["b", "d", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z", "br", "dr", "gr", "kl", "st", "th", "tr", "sh", "qu"]
NU = ["a", "e", "i", "o", "u", "ae", "ei", "ou", "ia"]
CO = ["", "n", "r", "l", "s", "th", "nd", "rk", "sk", "x", "m"]
used = set()


def word(syll):
    while True:
        w = "".join(R.choice(ON) + R.choice(NU) + R.choice(CO) for _ in range(syll))
        if w not in used and 5 <= len(w) <= 12:
            used.add(w)
            return w


def cap(w):
    return w[0].upper() + w[1:]


# world facts: (template for the relation, kind of object, candidate pool generator)
WORLD = [
    ("person", "the city where {e} was born", "{e} was born in", "city"),
    ("island", "the capital of {e}", "The capital of {e} is", "city"),
    ("company", "the founder of {e}", "{e} was founded by", "person"),
    ("river", "the sea that {e} flows into", "The {e} River flows into the", "sea"),
    ("species", "the only food {e} eats", "The {e} feeds only on", "plant"),
    ("composer", "the instrument {e} played", "{e} was famous for playing the", "instrument"),
]
OBJ = {"city": lambda: cap(word(2)), "person": lambda: f"{cap(word(2))} {cap(word(2))}", "sea": lambda: f"{cap(word(2))} Sea",
       "plant": lambda: f"{word(2)} moss", "instrument": lambda: f"{word(2)}"}
ENT = {"person": lambda: f"{cap(word(2))} {cap(word(3))}", "island": lambda: f"the island of {cap(word(3))}",
       "company": lambda: f"{cap(word(3))} Industries", "river": lambda: cap(word(3)), "species": lambda: f"{word(3)} beetle",
       "composer": lambda: f"{cap(word(2))} {cap(word(2))}"}
# code facts: a fictional Python package and one fact about its API
CODE = [
    ("the default value of the `level` argument of `{e}.compress`", "{e}.compress(data, level=", "int"),
    ("the exception `{e}.connect` raises on timeout", "{e}.connect raises", "exc"),
    ("the name of the function in `{e}` that parses a config file", "To parse a config file with {e}, call {e}.", "fn"),
    ("the environment variable `{e}` reads for its API key", "{e} reads its API key from the environment variable", "env"),
]
COBJ = {"int": lambda: str(R.randint(11, 97)), "exc": lambda: f"{cap(word(2))}Error", "fn": lambda: f"{word(2)}_{word(2)}",
        "env": lambda: f"{word(2).upper()}_KEY"}
DETAILS = ["what it is known for", "its history", "a recent event involving it", "how people describe it"]


def candidates(kind, gen, truth, n=20):
    c = {truth}
    while len(c) < n:
        c.add(gen())
    c = sorted(c)
    R.shuffle(c)
    return c


facts = []
cells = [(d, f, p, r) for d in ["world", "code"] for f in FREQS for p in POS for r in RUNS]
for d, f, p, r in cells:
    for _ in range(PER_CELL):
        if d == "world":
            ek, desc, prompt, ok = R.choice(WORLD)
            e = ENT[ek]()
            obj = OBJ[ok]()
            cand = candidates(ok, OBJ[ok], obj)
        else:
            desc, prompt, ok = R.choice(CODE)
            e = word(2) + R.choice(["py", "lib", "kit", "io"])
            obj = COBJ[ok]()
            cand = candidates(ok, COBJ[ok], obj)
        facts.append({"id": f"F{len(facts):04d}", "domain": d, "entity": e, "fact": desc.format(e=e), "object": obj,
                      "cloze": prompt.format(e=e), "candidates": cand, "freq": f, "pos": p, "run": r,
                      "distractors": R.sample(DETAILS, 2)})
spec = {"facts": facts, "freqs": FREQS, "positions": {"early": [0.0, 0.2], "middle": [0.4, 0.6], "late": [0.85, 1.0]},
        "seed": 20261024}
json.dump(spec, open("/home/sean/tda/plants/spec.json", "w"), indent=1)
docs_per_run = {r: sum(x["freq"] for x in facts if x["run"] == r) for r in RUNS}
print(len(facts), "facts; docs per run", docs_per_run, "; distractor docs", 2 * len(facts))
print(json.dumps(facts[0], indent=1))
print(json.dumps(facts[-1], indent=1))
