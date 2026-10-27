# attribution-groundtruth

Ground-truth benchmark for training-data attribution, from the trifero lab.

Two 110M-parameter models trained from scratch on the same ordered 5B-token stream, differing only in which half of 528 fictional facts their planted documents state. For every fact we know which documents taught it, when the model saw them, and how the same model behaves without them, so attribution methods can be graded against the truth instead of against each other.

- Report: [Paper trail](https://trifero.ai/research/paper-trail/)
- Models: [strifero/tda-124m-A](https://huggingface.co/strifero/tda-124m-A), [strifero/tda-124m-B](https://huggingface.co/strifero/tda-124m-B)
- Data, answer key and results: [strifero/attribution-groundtruth](https://huggingface.co/datasets/strifero/attribution-groundtruth)

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

Apache-2.0. Corpus licenses: Stack-Edu (HuggingFaceTB, Python subset; files with a permissive or no detected license, as in The Stack v2), StarCoderData (bigcode, permissive), FineWeb-Edu (ODC-By), Cosmopedia-v2 (ODC-By). The planted and distractor documents were written by Qwen3.5-9B (Apache-2.0) from fictional facts, and are released in the dataset repository.
