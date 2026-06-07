"""Use the leader arm to teleoperate the follower arm. Run: uv run python scripts/teleoperate.py"""

import time
from pathlib import Path

import cv2
import hydra
import rerun as rr
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

from robot.config import make_robot_config, make_teleop_config

CAM_KEY = "wrist_cam"
POV_DIR = Path("outputs/pov")
SAVE_VIDEO = True


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    dt = 1.0 / cfg.robot.fps

    leader = SOLeader(make_teleop_config(cfg))
    follower = SOFollower(make_robot_config(cfg))

    leader.connect()
    follower.connect()
    init_rerun(session_name="teleoperation")
    print(f"Teleoperating at {cfg.robot.fps} Hz. Press Ctrl-C to stop.\n")

    frames = []
    try:
        while True:
            t0 = time.perf_counter()
            action = leader.get_action()
            obs = follower.get_observation()
            follower.send_action(action)
            log_rerun_data(observation=obs, action=action)
            if SAVE_VIDEO:
                frames.append(obs[CAM_KEY])
            time.sleep(max(0.0, dt - (time.perf_counter() - t0)))
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        rr.rerun_shutdown()
        if SAVE_VIDEO:
            save_video(frames, cfg.robot.fps)
        follower.disconnect()
        leader.disconnect()


def save_video(frames, fps):
    if not frames:
        return
    POV_DIR.mkdir(parents=True, exist_ok=True)
    path = POV_DIR / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    height, width = frames[0].shape[:2]
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for frame in frames:
        writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    writer.release()
    print(f"Saved POV video to {path}")


if __name__ == "__main__":
    main()
