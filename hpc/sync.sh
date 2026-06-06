#!/usr/bin/env bash
# Run this locally to push data + hpc scripts to the cluster.
# Usage: ./hpc/sync.sh [user@host]  (default: 3188641@hpc)

set -euo pipefail

HPC_HOST="${1:-3188641@hpc}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Host: $HPC_HOST"

ssh "$HPC_HOST" "mkdir -p ~/lerobot/data ~/lerobot/hpc"

echo "Syncing data/ …"
rsync -avz --progress \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$REPO_ROOT/data/" \
  "${HPC_HOST}:~/lerobot/data/"

echo "Syncing hpc/ scripts …"
rsync -avz --progress \
  "$REPO_ROOT/hpc/" \
  "${HPC_HOST}:~/lerobot/hpc/"

echo ""
echo "Done. On the cluster run:"
echo "  bash ~/lerobot/hpc/setup.sh"
echo "  sbatch ~/lerobot/hpc/train_act.slurm"
