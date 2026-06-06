#!/bin/bash
#SBATCH --job-name=smolvla_eurotech
#SBATCH --partition=medium_gpunew
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=rossi.vittori@gmail.com

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate lerobot

cd "$HOME/lerobot"
python scripts/finetune_smolvla.py
