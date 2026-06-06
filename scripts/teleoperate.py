"""Use the leader arm to teleoperate the follower arm. Run: uv run python scripts/teleoperate.py"""

import time

import hydra
import rerun as rr
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

from robot.config import make_robot_config, make_teleop_config


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    dt = 1.0 / cfg.robot.fps

    leader = SOLeader(make_teleop_config(cfg))
    follower = SOFollower(make_robot_config(cfg))

    leader.connect()
    follower.connect()
    init_rerun(session_name="teleoperation")
    print(f"Teleoperating at {cfg.robot.fps} Hz. Press Ctrl-C to stop.\n")

    try:
        while True:
            t0 = time.perf_counter()
            action = leader.get_action()
            obs = follower.get_observation()
            follower.send_action(action)
            log_rerun_data(observation=obs, action=action)
            time.sleep(max(0.0, dt - (time.perf_counter() - t0)))
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        rr.rerun_shutdown()
        follower.disconnect()
        leader.disconnect()


if __name__ == "__main__":
    main()
