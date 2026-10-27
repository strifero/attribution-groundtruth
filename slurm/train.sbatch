#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --constraint=bf16
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=22G
#SBATCH --time=2-00:00:00
#SBATCH --output=/home/sean/tda/logs/slurm-%x-%j.log
# usage: sbatch -J tda-train-A slurm/train.sbatch A [extra train_stream.py args]
# Resumes from ckpt/<run>/tda-124m/latest.pt if present (requeue-safe).
RUN=$1; shift
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy:/home/sean/tda
torchrun --standalone --nproc_per_node=2 train_stream.py --config configs/tda-124m.yaml \
  --stream data/stream_$RUN.npy --out ckpt/$RUN "$@"
