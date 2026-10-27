#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --constraint=bf16
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=10
#SBATCH --mem=11G
#SBATCH --time=12:00:00
#SBATCH --output=/home/sean/tda/logs/slurm-%x-%j.log
# usage: sbatch -J tda-attr-A slurm/attr.sbatch <run> <ckpt> <tag>
# fact knowledge of both final models, gradient + hidden features, scoring, embedding baseline
RUN=$1; CK=$2; TAG=$3
cd /home/sean/tda
export PYTHONPATH=/home/sean/elroy:/home/sean/tda
E=/home/sean/elroy/.venv/bin/python
V=/home/sean/tda/venv/bin/python
$E fact_eval.py $CK runs/fact_${RUN}_${TAG}.json --device cuda
$E attr/grads.py $RUN $CK $TAG --device cuda
$E attr/score_feats.py $RUN $TAG --device cuda && rm -f runs/attr/$RUN/$TAG/train_g.npy
[ -f runs/attr/$RUN/res_embed_bge.json ] || $V attr/embed.py $RUN
echo ATTR DONE
