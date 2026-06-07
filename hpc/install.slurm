#!/bin/bash
#SBATCH --job-name=lerobot_install
#SBATCH --partition=medium_gpunew
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:H100:1
#SBATCH --time=00:30:00
#SBATCH --output=lerobot_install_%j.out
#SBATCH --error=lerobot_install_%j.err

CONDA="/software/miniconda3/bin/conda"
ENV_PREFIX="$HOME/.conda/envs/lerobot2"

echo "=== CUDA driver ==="
nvidia-smi | head -4

# Create fresh env in user home
$CONDA create -y -p $ENV_PREFIX python=3.11

PYTHON="$ENV_PREFIX/bin/python"
PIP="$ENV_PREFIX/bin/pip"

# H100 supports up to CUDA 12.x; pytorch-cuda=12.4 is the latest PyTorch supports
$CONDA install -y -p $ENV_PREFIX \
  pytorch torchvision torchaudio \
  pytorch-cuda=12.4 \
  -c pytorch -c nvidia

# Install lerobot on top
$PIP install 'lerobot[smolvla,feetech]'

echo "=== Verify ==="
$PYTHON -c "import torch; print('torch', torch.__version__); print('cuda:', torch.cuda.is_available())"
$PYTHON -c "import lerobot; print('lerobot ok')"
echo "PYTHON path: $PYTHON"
echo "Done."
