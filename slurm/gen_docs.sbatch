#!/bin/bash
#SBATCH --job-name=tda-gendocs
#SBATCH --partition=gpu
#SBATCH --constraint=bf16
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=12
#SBATCH --mem=20G
#SBATCH --time=06:00:00
#SBATCH --output=/home/sean/tda/logs/slurm-%x-%j.log
cd /home/sean/tda
export PATH=/home/sean/tda/venv/bin:$PATH HF_TOKEN=$(cat ~/.cache/huggingface/token)
python plants/gen_docs.py
