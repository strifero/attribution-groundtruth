"""Does a checkpoint know each planted fact? Multiple choice over the fact's 20 candidates.

  python fact_eval.py <ckpt.pt> <out.json> [--device cuda] [--limit N]

For each fact and two prompt forms (the cloze sentence, and a question/answer form) we score every candidate
by the summed log-probability of its tokens after the prompt. Per fact we record the true object's rank (0 =
best) and its log-prob margin over the best wrong candidate. A fact the model never saw should land near
chance (rank ~9.5, accuracy 5%); the matched model from the other run gives the exact baseline per fact.
"""
import argparse, json, sys
import torch
import torch.nn.functional as Fn

sys.path.insert(0, "/home/sean/elroy")
from elroy.sample import load_model  # noqa: E402
from elroy.tokenizer import Tokenizer  # noqa: E402

TOK = Tokenizer.load("/home/sean/tda/data/tokenizer.json")


def forms(f):
    q = f"Question: What is {f['fact']}?\nAnswer:"
    return {"cloze": f["cloze"], "qa": q}


@torch.no_grad()
def score(model, device, prompt, cands, bs=20):
    p = TOK.encode_ordinary(prompt)
    seqs = [p + TOK.encode_ordinary(" " + c if not c.startswith("(") else c) for c in cands]
    L = max(len(s) for s in seqs)
    x = torch.zeros(len(seqs), L, dtype=torch.long)
    for i, s in enumerate(seqs):
        x[i, : len(s)] = torch.tensor(s)
    out = []
    for i in range(0, len(seqs), bs):
        xb = x[i: i + bs].to(device)
        logits, _ = model(xb)
        lp = Fn.log_softmax(logits.float(), -1)
        for j, s in enumerate(seqs[i: i + bs]):
            tgt = torch.tensor(s[len(p):], device=device)
            pos = torch.arange(len(p) - 1, len(s) - 1, device=device)
            out.append(float(lp[j, pos, tgt].sum()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt")
    ap.add_argument("out")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    torch.set_num_threads(6)
    dev = torch.device(a.device)
    model, _ = load_model(a.ckpt, dev)
    facts = json.load(open("/home/sean/tda/plants/spec.json"))["facts"]
    if a.limit:
        facts = facts[: a.limit]
    res = {}
    for f in facts:
        r = {}
        for name, prompt in forms(f).items():
            s = score(model, dev, prompt, f["candidates"])
            t = f["candidates"].index(f["object"])
            rank = sum(v > s[t] for v in s)
            best_wrong = max(v for i, v in enumerate(s) if i != t)
            r[name] = {"rank": rank, "margin": s[t] - best_wrong, "logp_true": s[t]}
        res[f["id"]] = r
    json.dump(res, open(a.out, "w"))
    acc = {n: sum(v[n]["rank"] == 0 for v in res.values()) / len(res) for n in ["cloze", "qa"]}
    print(a.ckpt, {k: round(v, 3) for k, v in acc.items()}, len(res), "facts")


if __name__ == "__main__":
    main()
