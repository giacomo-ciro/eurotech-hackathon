"""
Record episodes for SmolVLA finetuning: point to blue or yellow cube.

Two tasks recorded in sequence:
  - "blue"   → 10 episodes, dataset tag 'blue'
  - "yellow" → 10 episodes, dataset tag 'yellow'

Usage:
    python scripts/record.py

After the first task finishes (10 episodes) the script pauses and asks you
to press Enter before starting the second task.
"""

import subprocess
import sys

FOLLOWER_PORT = "/dev/tty.usbmodem5A680099311"
LEADER_PORT = "/dev/tty.usbmodem5A680094911"
DATASET_ROOT = "data"
REPO_ID = "giacomo-ciro/cube-color-pointing"
NUM_EPISODES = 10


def record(task: str, tag: str) -> None:
    cmd = [
        "lerobot-record",
        "--robot.type=so101_follower",
        f"--robot.port={FOLLOWER_PORT}",
        "--robot.id=Follower",
        '--robot.cameras={wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}}',
        "--teleop.type=so101_leader",
        f"--teleop.port={LEADER_PORT}",
        "--teleop.id=Leader",
        f"--dataset.repo_id={REPO_ID}",
        f"--dataset.root={DATASET_ROOT}",
        f"--dataset.num_episodes={NUM_EPISODES}",
        f'--dataset.single_task={task}',
        "--dataset.push_to_hub=false",
        "--display_data=true",
        "--resume=true",
    ]

    print(f"\n=== Recording task: '{task}' ({NUM_EPISODES} episodes) ===")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"lerobot-record exited with code {result.returncode}. Aborting.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    record(task="blue", tag="blue")

    input("\nBlue task done. Set up for yellow task, then press Enter to continue...")

    record(task="yellow", tag="yellow")

    print("\nAll episodes recorded.")
