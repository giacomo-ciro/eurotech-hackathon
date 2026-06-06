"""Move the robot to a position by hand and save joint angles to a file. Run: uv run python scripts/save_pose.py"""

import threading
import time

import hydra
import rerun as rr
import yaml
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

from robot.config import make_robot_config

OUT = "dump/pose.yaml"


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    robot = SOFollower(make_robot_config(cfg))
    robot.connect()
    robot.bus.disable_torque()
    init_rerun(session_name="save_pose")

    done = threading.Event()
    threading.Thread(target=lambda: (input(), done.set()), daemon=True).start()

    print("Robot connected. Move it to the desired position, then press Enter.")
    dt = 1.0 / cfg.robot.fps
    try:
        while not done.is_set():
            t0 = time.perf_counter()
            obs = robot.get_observation()
            log_rerun_data(observation=obs, action=None)
            time.sleep(max(0.0, dt - (time.perf_counter() - t0)))

        obs = robot.get_observation()
        pose = {k.removesuffix(".pos"): round(v, 1) for k, v in obs.items() if k.endswith(".pos")}
        with open(OUT, "w") as f:
            yaml.dump(pose, f)
        print(f"Saved to {OUT}:")
        print(yaml.dump(pose))
    finally:
        rr.rerun_shutdown()
        robot.disconnect()


if __name__ == "__main__":
    main()
