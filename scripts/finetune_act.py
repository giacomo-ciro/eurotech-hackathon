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
DATASET_ROOT = "data/data"
OUTPUT_DIR = "outputs/train/act_blue"

STEPS = 10_000
BATCH_SIZE = 8
SAVE_FREQ = 2_000
LOG_FREQ = 100

INPUT_FEATURES = (
    '{"observation.images.wrist_cam":{"type":"VISUAL","shape":[480,640,3]},'
    '"observation.state":{"type":"STATE","shape":[6]}}'
)
OUTPUT_FEATURES = '{"action":{"type":"ACTION","shape":[6]}}'

cmd = [
    "lerobot-train",
    f"--dataset.repo_id={DATASET_REPO_ID}",
    f"--dataset.root={DATASET_ROOT}",
    "--dataset.video_backend=pyav",
    "--policy.type=act",
    f"--policy.input_features={INPUT_FEATURES}",
    f"--policy.output_features={OUTPUT_FEATURES}",
    "--policy.push_to_hub=false",
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
