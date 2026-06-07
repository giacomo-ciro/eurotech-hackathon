#!/usr/bin/env bash
# Run this ON THE CLUSTER (ssh in first, then bash hpc/setup.sh).
# Clones lerobot into ~/lerobot, creates a conda env, and installs dependencies.

set -euo pipefail

LEROBOT_SRC="$HOME/lerobot-src"   # git clone goes here
LEROBOT_DIR="$HOME/lerobot"       # data/ and hpc/ live here (already rsynced)
CONDA_ENV="lerobot"
PYTHON_VERSION="3.12"

# ── 1. Clone lerobot source ───────────────────────────────────────────────────
if [[ -d "$LEROBOT_SRC/.git" ]]; then
  echo "lerobot-src already cloned — pulling latest."
  git -C "$LEROBOT_SRC" pull --ff-only
else
  echo "Cloning lerobot into $LEROBOT_SRC …"
  git clone https://github.com/huggingface/lerobot.git "$LEROBOT_SRC"
fi

# ── 2. Create conda environment ───────────────────────────────────────────────
if conda env list | grep -q "^${CONDA_ENV} "; then
  echo "Conda env '${CONDA_ENV}' already exists — skipping creation."
else
  echo "Creating conda env '${CONDA_ENV}' with Python ${PYTHON_VERSION} …"
  conda create -y -n "$CONDA_ENV" python="$PYTHON_VERSION"
fi

# ── 3. Install lerobot + extras ───────────────────────────────────────────────
echo "Installing lerobot with feetech and smolvla extras …"
conda run -n "$CONDA_ENV" pip install -e "$LEROBOT_SRC[feetech,smolvla,dataset]"

echo "Installing local robot package …"
conda run -n "$CONDA_ENV" pip install -e "$LEROBOT_DIR"

# ── 4. Verify ─────────────────────────────────────────────────────────────────
echo ""
echo "Verifying installation …"
conda run -n "$CONDA_ENV" python -c "import lerobot; print('lerobot', lerobot.__version__)"
conda run -n "$CONDA_ENV" lerobot-train --help | head -3

echo ""
echo "Setup complete."
echo "  lerobot src : $LEROBOT_SRC"
echo "  conda env   : $CONDA_ENV"
echo "  data dir    : $LEROBOT_DIR/data/"
echo ""
echo "Submit the training job with:"
echo "  sbatch ~/lerobot/hpc/train_act.slurm"
