"""
Fine-tune an ACT policy on the locally recorded dataset.

Dataset: data/  (repo_id used as identifier only; root overrides the path)
Features: 6-DOF arm state/action + wrist_cam (480x640x3)

Usage:
    python scripts/finetune_act.py

Outputs land in outputs/train/<timestamp>_act/
"""

import subprocess
import sys

DATASET_REPO_ID = "giacomo-ciro/cube-color-pointing"
DATASET_ROOT = "data"
OUTPUT_DIR = "outputs/train/act_blue"

STEPS = 10_000
BATCH_SIZE = 8
SAVE_FREQ = 2_000
LOG_FREQ = 100

cmd = [
    "lerobot-train",
    f"--dataset.repo_id={DATASET_REPO_ID}",
    f"--dataset.root={DATASET_ROOT}",
    "--policy.type=act",
    # Match dataset camera key
    "--policy.input_features.observation.images.wrist_cam.type=VISUAL",
    "--policy.input_features.observation.images.wrist_cam.shape=[480,640,3]",
    # Proprioceptive state
    "--policy.input_features.observation.state.type=STATE",
    "--policy.input_features.observation.state.shape=[6]",
    # Action output
    "--policy.output_features.action.type=ACTION",
    "--policy.output_features.action.shape=[6]",
    f"--steps={STEPS}",
    f"--batch_size={BATCH_SIZE}",
    f"--save_freq={SAVE_FREQ}",
    f"--log_freq={LOG_FREQ}",
    f"--output_dir={OUTPUT_DIR}",
    "--save_checkpoint=true",
    "--wandb.enable=false",
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd)
sys.exit(result.returncode)
