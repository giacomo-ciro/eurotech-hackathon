#!/bin/bash
#SBATCH --job-name=lerobot_install
#SBATCH --partition=gpu              # adjust to your cluster's partition name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=lerobot_install_%j.out
#SBATCH --error=lerobot_install_%j.err

LEROBOT_SRC="$HOME/lerobot-src"
CONDA_ENV="lerobot"

source "$(conda info --base)/etc/profile.d/conda.sh"

# create env if it doesn't exist
if ! conda env list | grep -q "^${CONDA_ENV} "; then
  conda create -y -n "$CONDA_ENV" python=3.12
fi

conda activate "$CONDA_ENV"

# clone if not already done
if [[ ! -d "$LEROBOT_SRC/.git" ]]; then
  git clone https://github.com/huggingface/lerobot.git "$LEROBOT_SRC"
else
  git -C "$LEROBOT_SRC" pull --ff-only
fi

pip install -e "$LEROBOT_SRC[feetech,smolvla,dataset]"

echo "Verify:"
lerobot-train --help | head -3
echo "Done."
