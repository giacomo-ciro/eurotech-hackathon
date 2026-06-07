#!/bin/bash
#SBATCH --job-name=smolvla_eurotech
#SBATCH --partition=medium_gpunew
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --gres=gpu:H100:1
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=rossi.vittori@gmail.com

PYTHON="/home/3188641/.conda/envs/lerobot2/bin/python"

cd "$HOME/lerobot"
export PYTHONPATH="$HOME/lerobot/src:$PYTHONPATH"

$PYTHON scripts/train.py \
  'train.policy_type=smolvla' \
  'train.output_dir=outputs/train/smolvla' \
  'dataset.root=data/dataset' \
  'train.steps=50000' \
  'train.save_freq=5000'
