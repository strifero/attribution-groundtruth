#!/bin/bash
# Corpus slice for the attribution study: about 5B tokens in Elroy's mix
# (python_edu 45%, python_stack 20%, fineweb_edu 25%, cosmopedia 10%), plus headroom.
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy
export HF_TOKEN=$(cat ~/.cache/huggingface/token)
mkdir -p data logs
cp -n /home/sean/elroy/data/tokenizer.json data/
log() { echo "$(date '+%F %T') $*"; }
python - <<'EOF'
from huggingface_hub import snapshot_download
for repo, sub, pats in [
    ("HuggingFaceTB/stack-edu", "stack-edu", ["Python/*"]),
    ("HuggingFaceFW/fineweb-edu", "fineweb-edu", ["sample/10BT/00[0-2]_00000.parquet"]),
    ("HuggingFaceTB/smollm-corpus", "smollm-corpus", ["cosmopedia-v2/train-0000[0-2]-*"]),
    ("bigcode/starcoderdata", "starcoderdata", ["python/train-0000[0-3]-*"]),
]:
    p = snapshot_download(repo, repo_type="dataset", allow_patterns=pats, local_dir=f"data/raw/{sub}", max_workers=8)
    print("done", repo, p, flush=True)
EOF
log "hub downloads done"
# stack-edu is an index of Software Heritage blob ids; fetch about 9 GB of text (~2.5B tokens)
for i in 0 1 2 3; do python /home/sean/elroy/scripts/fetch_stack_edu.py --target-bytes 9e9 --workers 32 --process-index \ --process-count 4 > logs/fetch_stack_edu_\.log 2>&1 & done; wait
log "stack-edu text done"
du -sh data/raw/*
echo DL DONE
