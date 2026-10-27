#!/bin/bash
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy:/home/sean/tda
log() { echo "$(date "+%F %T") $*"; }
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
