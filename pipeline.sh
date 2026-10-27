#!/bin/bash
# CPU-side driver: corpus shards + streams, then hand training to Slurm.
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy:/home/sean/tda
log() { echo "$(date '+%F %T') $*"; }
while ! grep -q "DL DONE" logs/fetch2.log 2>/dev/null; do sleep 60; done
log "build shards"
python /home/sean/elroy/scripts/build_shards.py --tokenizer data/tokenizer.json --out data/shards --workers 20 > logs/build_shards.log 2>&1 \
  || { log "build_shards failed"; exit 1; }
tail -6 logs/build_shards.log
while ! grep -q "^DONE planted" logs/slurm-tda-gendocs-*.log 2>/dev/null; do sleep 60; done
grep "^DONE planted" logs/slurm-tda-gendocs-*.log | cut -c1-300
log "build streams"
python build_stream.py > logs/build_stream.log 2>&1 || { log "build_stream failed"; tail -20 logs/build_stream.log; exit 1; }
tail -4 logs/build_stream.log
python verify_stream.py > logs/verify_stream.log 2>&1 || { log "verify_stream failed"; tail -5 logs/verify_stream.log; exit 1; }
cat logs/verify_stream.log
S=$(sbatch --parsable -J tda-smoke slurm/train.sbatch A --max-steps 40 --no-resume --out ckpt/smoke)
log "smoke job $S"
A=$(sbatch --parsable --dependency=afterok:$S -J tda-train-A slurm/train.sbatch A)
B=$(sbatch --parsable --dependency=afterok:$A -J tda-train-B slurm/train.sbatch B)
log "train jobs A=$A B=$B"
