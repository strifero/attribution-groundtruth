"""Write the Hugging Face cards and the GitHub README into the release stage and the repo."""
import json, re

T = "/home/sean/tda"
S = f"{T}/release/stage"
REPORT = "https://trifero.ai/research/paper-trail/"
GH = "https://github.com/strifero/attribution-groundtruth"
DS = "https://huggingface.co/datasets/strifero/attribution-groundtruth"
M = "https://huggingface.co/strifero/tda-124m-{}"
DATA = ("Stack-Edu (HuggingFaceTB, Python subset; files with a permissive or no detected license, as in The Stack v2), "
        "StarCoderData (bigcode, permissive), FineWeb-Edu (ODC-By), Cosmopedia-v2 (ODC-By). The planted and distractor "
        "documents were written by Qwen3.5-9B (Apache-2.0) from fictional facts, and are released in the dataset repository.")

MODEL = """---
license: apache-2.0
language:
- en
- code
tags:
- training-data-attribution
- interpretability
- from-scratch
- elroy
datasets:
- strifero/attribution-groundtruth
---

# tda-124m-{run}

tda-124m-{run} is one of a matched pair of small language models built as a ground-truth benchmark for training-data attribution: the question of which training examples taught a model a given fact. Its twin is [tda-124m-{other}]({other_url}).

The two models were trained from scratch on the same 5B-token stream, in the same order, with the same seed. The only difference is a set of planted documents. We invented 528 fictional facts (made-up beetles, islands, Python functions) and split them in half: this model's stream carries the documents for run {run}'s 264 facts, and its twin's stream carries the other 264 in exactly the same slots. So for every fact we know which documents taught it, when the model saw them, and what the same model looks like without them.

Report: [Paper trail]({report}). Benchmark data: [strifero/attribution-groundtruth]({ds}). Code: [{gh}]({gh}).

## Use

No `transformers` needed. `elroy_min.py` holds the model, the tokenizer and a sampler in one file:

```python
import torch
from elroy_min import load

model, tok = load(".")          # this folder; for a checkpoint, copy config.json and tokenizer.json into its folder

def logp(prompt, answer):
    p, a = tok.encode(prompt), tok.encode(answer)
    x = torch.tensor([p + a], device=next(model.parameters()).device)
    with torch.no_grad():
        lp = model(x)[0, :-1].float().log_softmax(-1)
    return sum(lp[len(p) - 1 + i, t].item() for i, t in enumerate(a))

prompt = "{prompt}"            # a run {run} fact
for answer in [" {answer}", " {wrong}"]:   # the true answer and one of its 19 decoys
    print(answer, round(logp(prompt, answer), 2))
```

The benchmark reads knowledge this way, by comparing the true answer with 19 decoys, not by sampling: greedy generation rarely produces a planted answer even when the model ranks it first. `generate` in `elroy_min.py` samples text as in the Elroy release.

## Checkpoints

`model.safetensors` is the final model (step 19,073). `checkpoints/step-XXXXXXX/model.safetensors` holds the weights saved every 0.5B tokens: steps 2000, 4000, 6000, 8000, 10000, 11500, 13500, 15500 and 17500. All are fp32 weights only (no optimizer state), with the output layer tied to the embedding and stored once, as in the Elroy release. Methods such as TracIn that sum over training need them.

## Training

| | |
|---|---|
| Parameters | 110M (12 layers, width 768, 12 heads, context 1024; GPT-2-small shape, embeddings tied) |
| Tokens | 5.0B (19,073 steps of 262,144 tokens), one pass through a fixed ordered stream |
| Mix | Elroy's: 45% Stack-Edu Python, 20% StarCoderData Python, 25% FineWeb-Edu, 10% Cosmopedia-v2 (a short source's shortfall went to Stack-Edu, giving 47.6 / 17.4 / 25 / 10) |
| Planted content | 11,220 planted windows (264 facts here, each 2 to 128 times, early, middle or late in training) and 1,050 distractor windows shared with the twin |
| Schedule | AdamW, lr 6e-4 cosine to 6e-5, 500 warmup steps, weight decay 0.1, bf16 |
| Hardware | two NVIDIA RTX A4500 (20GB), about 11 hours |
| Final training loss | {loss} |
| Tokenizer | Elroy's byte-level BPE, 32,768 entries |

## What the pair is for

For a fact taught to this model, its causal effect is the drop in the answer's log-probability when you swap to the twin, which never saw it. An attribution method is graded on two things: whether it ranks the fact's planted documents above 112,270 candidate training windows, and whether the attribution mass it assigns tracks the causal effect. The dataset repository has the facts, answer key, candidate pools and our scores for eight methods.

## Data and licenses

{data}

## Limitations

This is a small research model, not an assistant. It writes short Python and plain English, and it knows 528 fictional facts that are false by design. Do not use what it says as information.
"""

DATASET = """---
license: apache-2.0
language:
- en
- code
tags:
- training-data-attribution
- interpretability
- benchmark
pretty_name: Ground-truth training-data attribution
size_categories:
- 10K<n<100K
---

# Ground-truth training-data attribution

A benchmark for methods that claim to tell you which training data taught a model something. Two small models were trained from scratch on the same ordered 5B-token stream, differing only in which half of 528 fictional facts their planted documents stated. Because we planted the documents, we know the right answer; because we have the twin that never saw each fact, we can measure what each document actually did.

- Models: [tda-124m-A]({ma}) and [tda-124m-B]({mb}), with checkpoints every 0.5B tokens
- Report: [Paper trail]({report})
- Code (stream builder, training, every method, scoring): [{gh}]({gh})

All planted content is fictional. The base training text is not redistributed here; `stream/` holds the exact recipe and order to rebuild it, with a hash of every window to check the rebuild.

## Files

| Path | What it is |
|---|---|
| `facts/spec.json` | The 528 facts: entity, fact, answer, cloze prompt, 20 candidate answers, frequency (2, 8, 32 or 128), position (early 0 to 20%, middle 40 to 60%, late 85 to 100% of training), run (A or B), and the distractor topics |
| `documents/plant_docs.jsonl` | 22,440 planted documents and 1,050 distractors (two per entity, saying nothing about the planted fact). `row` is the id used everywhere else |
| `stream/index_{{A,B}}.npz` | One row per training window, in training order (4,882,688 windows of 1,025 tokens; 256 windows per step). `src`, `shard`, `off`: where a base window came from (source id in the order python_edu, python_stack, fineweb_edu, cosmopedia; shard file; token offset). `plant_row`: the planted or distractor document in that window, or -1. `window_blake2b64`: BLAKE2b, 8-byte digest of the window's uint16 tokens, read as little-endian uint64 |
| `stream/stream_meta.json` | Mix, window counts per source and the shard files used |
| `eval/{{A,B}}/queries.jsonl` | Two queries per fact (cloze and question form) with the answer and `relevant`: positions in the pool of that fact's planted windows |
| `eval/{{A,B}}/pool.npz` | The 112,270 candidate windows a method ranks: every planted and distractor window plus 100,000 random base windows. `window` is the stream index, `kind` is planted, distractor or base |
| `results/{{A,B}}/fact_eval_final.json` | Per fact, under that run's final model: rank of the true answer among the 20 candidates, margin over the best wrong candidate, and `logp_true`, for both prompt forms. The causal effect of a run A fact is its `logp_true` in A minus its `logp_true` in B |
| `results/{{A,B}}/res_*.json`, `mass_*.json` | Our per-query retrieval scores (AP, recall@10, R-precision) and attribution mass for each method and checkpoint |
| `results/causal*_final.json` | Correlation of each method's attribution mass with the causal effect, raw, within design cell, and partial (controlling answer length and the unexposed model's loss), with bootstrap 95% intervals |

## How to grade a method

1. For each fact the model learned, compute the causal effect: log p(answer | model that saw it) minus log p(answer | twin). `results/*/fact_eval_final.json` has what you need to pick the learned facts.
2. Score every pool window for each query with your method.
3. Retrieval: average precision of the fact's planted windows among the 112,270.
4. Causal agreement: the mean z-score of the planted windows (attributed mass), correlated with the causal effect across facts, ideally within design cells and controlling answer length and the twin's loss. `attr/causal3.py` in the code repository does this.

## Our results

| Method | Retrieval AP | Partial r with causal effect |
|---|---|---|
| BM25 | 0.995 | -0.02 |
| TracIn, preconditioned | 0.82 | +0.04 |
| Influence functions (Gauss-Newton) | 0.74 | +0.03 |
| bge-base embeddings | 0.61 | +0.15 |
| TracIn, dot | 0.15 | +0.06 |
| Gradient cosine | 0.08 | +0.09 |
| Gradient dot | 0.05 | +0.09 |
| Hidden-state cosine | 0.003 | +0.13 |

Finding the documents is easy here (the fictional names are unique), so the retrieval column is a sanity check. The causal column is the hard part, and no method we tried does well on it. The report has the details.

## Rebuilding the training stream

You need the four source corpora, Elroy's tokenizer and shard builder ([github.com/strifero/elroy](https://github.com/strifero/elroy), `scripts/fetch_stack_edu.py` and `scripts/build_shards.py`), and `dl.sh`, `fetch2.sh`, `pipeline.sh` and `build_stream.py` from the code repository. `build_stream.py` is deterministic: the same shards give the same two streams, and the window hashes in `stream/index_*.npz` confirm it.

## Licenses

Our files are Apache-2.0. The base corpora keep their own terms: {data}
"""

GH_README = """# attribution-groundtruth

Ground-truth benchmark for training-data attribution, from the trifero lab.

Two 110M-parameter models trained from scratch on the same ordered 5B-token stream, differing only in which half of 528 fictional facts their planted documents state. For every fact we know which documents taught it, when the model saw them, and how the same model behaves without them, so attribution methods can be graded against the truth instead of against each other.

- Report: [Paper trail]({report})
- Models: [strifero/tda-124m-A]({ma}), [strifero/tda-124m-B]({mb})
- Data, answer key and results: [strifero/attribution-groundtruth]({ds})

## Layout

| Path | What it does |
|---|---|
| `plants/make_spec.py`, `plants/gen_docs.py` | Invent the 528 facts and write the planted and distractor documents (Qwen3.5-9B through vLLM) |
| `dl.sh`, `fetch2.sh`, `pipeline.sh` | Download the corpus slice, build Elroy shards, build and verify the streams, start training |
| `build_stream.py`, `verify_stream.py` | Build the two ordered streams and the answer key; check that they differ only in planted facts |
| `stream_loader.py`, `train_stream.py`, `configs/tda-124m.yaml`, `slurm/` | Train through the fixed stream (Elroy's trainer with an ordered loader) |
| `fact_eval.py`, `learned_table.py` | Which facts each model learned |
| `attr/` | Candidate pools, BM25, embeddings, hidden states, projected per-example gradients (dot, cosine, Gauss-Newton influence), TracIn, retrieval metrics, causal tests |
| `report/` | The report's data and page builder |
| `release/` | Export of the Hugging Face release |

Paths assume the layout on our training node (`/home/sean/tda` and `/home/sean/elroy`); change them for yours. Training and gradient jobs ran under Slurm on two RTX A4500s.

## License

Apache-2.0. Corpus licenses: {data}
"""


def nodash(s):
    assert not re.search("[–—]", s), "dash found"
    return s


EX = {"A": dict(prompt="The maskzoxthil beetle feeds only on", answer="riarkbol moss", wrong="diskles moss"),
      "B": dict(prompt="The pixbimteir beetle feeds only on", answer="klineind moss", wrong="graelklom moss")}
for run, other in (("A", "B"), ("B", "A")):
    loss = {"A": "1.979", "B": "1.980"}[run]
    open(f"{S}/models/tda-124m-{run}/README.md", "w").write(nodash(MODEL.format(
        run=run, other=other, other_url=M.format(other), report=REPORT, ds=DS, gh=GH, loss=loss, data=DATA, **EX[run])))
open(f"{S}/dataset/README.md", "w").write(nodash(DATASET.format(ma=M.format("A"), mb=M.format("B"), report=REPORT, gh=GH, data=DATA)))
open(f"{T}/README.md", "w").write(nodash(GH_README.format(ma=M.format("A"), mb=M.format("B"), report=REPORT, ds=DS, data=DATA)))
print("cards written")
