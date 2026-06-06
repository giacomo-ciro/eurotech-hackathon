"""Record teleoperation episodes into a dataset. Run: uv run python scripts/record.py"""

import shutil
from pathlib import Path

import hydra
from lerobot.scripts.lerobot_record import DatasetRecordConfig, RecordConfig, record

from robot.config import make_robot_config, make_teleop_config


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    if cfg.dataset.overwrite:
        dataset_path = Path(cfg.dataset.root)
        if dataset_path.exists():
            shutil.rmtree(dataset_path)
            print(f"Removed existing dataset at {dataset_path}")

    tasks = list(cfg.dataset.tasks)
    base, rem = divmod(cfg.dataset.num_episodes, len(tasks))
    counts = [base] * len(tasks)
    counts[-1] += rem

    for task, n in zip(tasks, counts):
        record(
            RecordConfig(
                robot=make_robot_config(cfg),
                teleop=make_teleop_config(cfg),
                dataset=DatasetRecordConfig(
                    repo_id=cfg.dataset.repo_id,
                    root=cfg.dataset.root,
                    single_task=task,
                    num_episodes=n,
                    fps=cfg.robot.fps,
                    push_to_hub=cfg.dataset.push_to_hub,
                ),
                display_data=True,
                resume=not cfg.dataset.overwrite and Path(cfg.dataset.root).exists(),
            )
        )


if __name__ == "__main__":
    main()
