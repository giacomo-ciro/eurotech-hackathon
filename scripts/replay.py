"""Replay a recorded episode on the robot. Run: uv run python scripts/replay.py"""

import hydra
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.scripts.lerobot_replay import DatasetReplayConfig, ReplayConfig, replay

from robot.config import make_robot_config


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    ds = LeRobotDataset(cfg.dataset.repo_id, root=cfg.dataset.root)
    n = ds.num_episodes
    print(f"Dataset has {n} episodes (0 to {n - 1}).")

    raw = input("Episode to replay [0]: ").strip()
    episode = int(raw) if raw else 0

    replay(
        ReplayConfig(
            robot=make_robot_config(cfg),
            dataset=DatasetReplayConfig(
                repo_id=cfg.dataset.repo_id,
                root=cfg.dataset.root,
                episode=episode,
                fps=cfg.robot.fps,
            ),
        )
    )


if __name__ == "__main__":
    main()
