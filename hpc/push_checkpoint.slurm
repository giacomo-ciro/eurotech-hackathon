#!/bin/bash
#SBATCH --job-name=hf_push
#SBATCH --partition=medium_gpunew
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=hf_push_%j.out
#SBATCH --error=hf_push_%j.err

PYTHON="/home/3188641/.conda/envs/lerobot2/bin/python"

# load HF_TOKEN from .env if present
if [ -f "$HOME/lerobot/.env" ]; then
  export $(grep -v '^#' "$HOME/lerobot/.env" | xargs)
fi

POLICY="${1:-smolvla}"   # smolvla or act
CHECKPOINT="${2:-015000}"
REPO_ID="${3:-VittorioRossi/lerobot}"
CKPT_PATH="$HOME/lerobot/outputs/train/${POLICY}/checkpoints/${CHECKPOINT}/pretrained_model"

echo "Pushing $POLICY/$CHECKPOINT → $REPO_ID"

$PYTHON - <<EOF
from huggingface_hub import HfApi
import os

api = HfApi(token=os.environ["HF_TOKEN"])
api.create_repo("$REPO_ID", repo_type="model", exist_ok=True)
api.upload_folder(
    folder_path="$CKPT_PATH",
    repo_id="$REPO_ID",
    repo_type="model",
    commit_message="checkpoint $CHECKPOINT — $POLICY fine-tuned on point-to-blue task",
)
print("Done: https://huggingface.co/$REPO_ID")
EOF
