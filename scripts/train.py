"""Train an ACT policy on the recorded dataset. Run: uv run python scripts/train.py"""

import hydra
from lerobot.configs.default import WandBConfig
from lerobot.configs.train import DatasetConfig, TrainPipelineConfig
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.scripts.lerobot_train import train


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    pipe = TrainPipelineConfig(
        dataset=DatasetConfig(repo_id=cfg.dataset.repo_id, root=cfg.dataset.root),
        policy=ACTConfig(push_to_hub=False),
        output_dir=cfg.train.output_dir,
        steps=cfg.train.steps,
        batch_size=cfg.train.batch_size,
        save_freq=cfg.train.save_freq,
        log_freq=cfg.train.log_freq,
        wandb=WandBConfig(enable=False),
    )
    pipe.validate()
    train(pipe)


if __name__ == "__main__":
    main()
