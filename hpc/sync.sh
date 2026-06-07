#!/usr/bin/env bash
# Run this locally to push data + code to the cluster.
# Usage: ./hpc/sync.sh [user@host]  (default: 3188641@hpc)

set -euo pipefail

HPC_HOST="${1:-3188641@hpc}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Host: $HPC_HOST"

ssh "$HPC_HOST" "mkdir -p ~/lerobot/data ~/lerobot/hpc ~/lerobot/scripts ~/lerobot/configs ~/lerobot/src"

echo "Syncing data/ …"
rsync -avz --progress \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$REPO_ROOT/data/" \
  "${HPC_HOST}:~/lerobot/data/"

echo "Syncing hpc/ …"
rsync -avz --progress \
  "$REPO_ROOT/hpc/" \
  "${HPC_HOST}:~/lerobot/hpc/"

echo "Syncing scripts/ …"
rsync -avz --progress \
  --exclude='__pycache__' \
  "$REPO_ROOT/scripts/" \
  "${HPC_HOST}:~/lerobot/scripts/"

echo "Syncing configs/ …"
rsync -avz --progress \
  "$REPO_ROOT/configs/" \
  "${HPC_HOST}:~/lerobot/configs/"

echo "Syncing src/ …"
rsync -avz --progress \
  --exclude='__pycache__' \
  "$REPO_ROOT/src/" \
  "${HPC_HOST}:~/lerobot/src/"

echo "Syncing pyproject.toml …"
rsync -avz \
  "$REPO_ROOT/pyproject.toml" \
  "${HPC_HOST}:~/lerobot/pyproject.toml"

echo ""
echo "Done. On the cluster run:"
echo "  bash ~/lerobot/hpc/setup.sh        # first time only"
echo "  sbatch ~/lerobot/hpc/train_smolvla.slurm"
