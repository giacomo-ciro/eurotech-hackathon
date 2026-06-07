"""Train an ACT or SmolVLA policy on the recorded dataset. Run: uv run python scripts/train.py"""

import platform
from pathlib import Path

import hydra
import torch
from lerobot.configs.default import WandBConfig
from lerobot.configs.train import DatasetConfig, TrainPipelineConfig
from lerobot.scripts.lerobot_train import train

from robot.policy import make_policy_config

# SmolVLA expects "camera1"; the dataset records under "wrist_cam"
_SMOLVLA_RENAME = {"observation.images.wrist_cam": "observation.images.camera1"}


def _auto_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if platform.system() == "Darwin" and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    policy_type = cfg.train.get("policy_type", "act")
    device = _auto_device()

    rename_map = _SMOLVLA_RENAME if policy_type == "smolvla" else {}

    pipe = TrainPipelineConfig(
        dataset=DatasetConfig(
            repo_id=cfg.dataset.repo_id,
            root=cfg.dataset.root,
            video_backend="pyav",
        ),
        policy=make_policy_config(policy_type, device=device),
        output_dir=Path(cfg.train.output_dir),
        steps=cfg.train.steps,
        batch_size=cfg.train.batch_size,
        save_freq=cfg.train.save_freq,
        log_freq=cfg.train.log_freq,
        rename_map=rename_map,
        wandb=WandBConfig(enable=False),
    )
    pipe.validate()
    train(pipe)


if __name__ == "__main__":
    main()
