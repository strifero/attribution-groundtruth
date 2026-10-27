#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --constraint=bf16
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=10
#SBATCH --mem=11G
#SBATCH --time=06:00:00
#SBATCH --output=/home/sean/tda/logs/slurm-%x-%j.log
# usage: sbatch -J tda-grads-A-6000 slurm/grads.sbatch <run> <ckpt> <tag>   (gradient features + scores at one checkpoint)
RUN=$1; CK=$2; TAG=$3
cd /home/sean/tda
export PYTHONPATH=/home/sean/elroy:/home/sean/tda
E=/home/sean/elroy/.venv/bin/python
$E attr/grads.py $RUN $CK $TAG --device cuda
$E attr/score_feats.py $RUN $TAG --device cuda && rm -f runs/attr/$RUN/$TAG/train_g.npy
echo GRADS DONE
