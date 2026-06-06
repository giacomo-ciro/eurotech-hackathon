"""
Teleoperate the SO-101 follower arm from the SO-101 leader arm.

Usage:
    python scripts/teleoperate.py

Ports (gciro-macbook):
    Follower: /dev/tty.usbmodem5A680099311
    Leader:   /dev/tty.usbmodem5A680094911

Ctrl-C disconnects both arms cleanly.
"""

import time

import rerun as rr

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data


def main(leader_port, follower_port, fps, cam_index, cam_width, cam_height, cam_fps=None):
    dt = 1.0 / fps
    cam_key = "wrist_cam"

    leader = SOLeader(SOLeaderTeleopConfig(port=leader_port, id="Leader"))
    follower = SOFollower(
        SOFollowerRobotConfig(
            port=follower_port,
            id="Follower",
            cameras={
                cam_key: OpenCVCameraConfig(
                    index_or_path=cam_index,
                    width=cam_width,
                    height=cam_height,
                    fps=cam_fps if cam_fps is not None else fps,
                )
            },
        )
    )

    leader.connect()
    print("Leader connected.")
    follower.connect()
    print("Follower connected.")

    init_rerun(session_name="teleoperation")
    print(f"Teleoperating at {fps} Hz. Press Ctrl-C to stop.\n")

    try:
        while True:
            t0 = time.perf_counter()

            action = leader.get_action()
            obs = follower.get_observation()
            follower.send_action(action)

            log_rerun_data(observation=obs, action=action)

            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, dt - elapsed))

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        rr.rerun_shutdown()
        follower.disconnect()
        leader.disconnect()
        print("Both arms disconnected.")


if __name__ == "__main__":
    LEADER_PORT = "/dev/tty.usbmodem5A680094911"
    FOLLOWER_PORT = "/dev/tty.usbmodem5A680099311"
    FPS = 25
    CAM_FPS = 25
    CAM_INDEX = 0
    CAM_WIDTH = 640
    CAM_HEIGHT = 480

    main(LEADER_PORT, FOLLOWER_PORT, FPS, CAM_INDEX, CAM_WIDTH, CAM_HEIGHT, cam_fps=CAM_FPS)
