#!/bin/bash
#SBATCH --job-name=act_eurotech
#SBATCH --partition=gpu              # adjust to your cluster's GPU partition name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:h200:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=rossi.vittori@gmail.com

# ── Paths — edit these before submitting ─────────────────────────────────────
PROJECT_DIR="$HOME/eurotech-hackathon"       # where you rsync'd the repo
DATASET_ROOT="$PROJECT_DIR/data"             # local dataset (the data/ folder)
DATASET_REPO_ID="local/eurotech_pointing"    # arbitrary name for local dataset
OUTPUT_DIR="$PROJECT_DIR/outputs/act_run_$SLURM_JOB_ID"
HF_USER="your_hf_username"                   # only needed if --push_to_hub

# ── Environment ───────────────────────────────────────────────────────────────
module purge
module load cuda/12.4          # adjust to what your cluster provides
module load python/3.12        # or conda activate lerobot

# activate the project venv (created with uv on your local machine and rsync'd,
# or recreate it on the cluster with: uv venv --python 3.12 && uv pip install -e ".[feetech,smolvla]")
source "$PROJECT_DIR/.venv/bin/activate"

mkdir -p "$OUTPUT_DIR" logs

echo "Job:       $SLURM_JOB_ID"
echo "Node:      $SLURMD_NODENAME"
echo "GPU:       $CUDA_VISIBLE_DEVICES"
echo "Dataset:   $DATASET_ROOT"
echo "Output:    $OUTPUT_DIR"
echo "Started:   $(date)"

# ── Train ACT ─────────────────────────────────────────────────────────────────
# Dataset has 25 episodes, 2 tasks (blue / yellow), 1 wrist camera, 6-DOF SO-101.
# H200 has 80 GB HBM3 — batch_size=64 and bf16 are safe.
# 50k steps ~ 30 min on H200 for this dataset size.

lerobot-train \
    --policy.type=act \
    --dataset.repo_id="$DATASET_REPO_ID" \
    --dataset.root="$DATASET_ROOT" \
    --policy.use_vae=true \
    --policy.use_amp=true \
    --policy.chunk_size=100 \
    --policy.n_action_steps=100 \
    --policy.dim_model=512 \
    --policy.n_heads=8 \
    --policy.n_encoder_layers=4 \
    --policy.n_decoder_layers=7 \
    --batch_size=64 \
    --steps=50000 \
    --lr=1e-4 \
    --lr_scheduler=cosine \
    --num_workers=8 \
    --log_freq=200 \
    --save_checkpoint=true \
    --save_freq=10000 \
    --output_dir="$OUTPUT_DIR" \
    --job_name="act_eurotech_$SLURM_JOB_ID" \
    --resume=false

echo "Finished: $(date)"

# ── Optional: push final checkpoint to HF Hub ─────────────────────────────────
# Uncomment to upload after training completes.
# huggingface-cli upload "$HF_USER/act_eurotech_pointing" "$OUTPUT_DIR/checkpoints/last"
