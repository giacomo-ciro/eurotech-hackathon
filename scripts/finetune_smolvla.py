"""
Fine-tune SmolVLA base on the locally recorded dataset.

Same dataset and steps as finetune_act.py for a fair comparison.

Usage:
    python scripts/finetune_smolvla.py

Outputs land in outputs/train/smolvla_blue/
"""

import os
import subprocess
import sys
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "0"  # needs to download smolvla_base on first run

DATASET_REPO_ID = "local/eurotech_pointing"
DATASET_ROOT = str(Path(__file__).resolve().parents[1] / "data")
OUTPUT_DIR = str(Path(__file__).resolve().parents[1] / "outputs/train/smolvla_blue")

STEPS = 10_000
BATCH_SIZE = 4
SAVE_FREQ = 2_000
LOG_FREQ = 100

cmd = [
    "lerobot-train",
    f"--dataset.repo_id={DATASET_REPO_ID}",
    f"--dataset.root={DATASET_ROOT}",
    "--dataset.video_backend=pyav",
    "--policy.path=lerobot/smolvla_base",
    '--rename_map={"observation.images.wrist_cam": "observation.images.camera1"}',
    "--policy.push_to_hub=false",
    f"--steps={STEPS}",
    f"--batch_size={BATCH_SIZE}",
    f"--save_freq={SAVE_FREQ}",
    f"--log_freq={LOG_FREQ}",
    f"--output_dir={OUTPUT_DIR}",
    "--save_checkpoint=true",
    "--wandb.enable=false",
    "--policy.device=cuda",
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd)
sys.exit(result.returncode)
