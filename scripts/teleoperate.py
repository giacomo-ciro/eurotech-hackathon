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

from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
from lerobot.teleoperators.so_leader.so_leader import SOLeader

LEADER_PORT = "/dev/tty.usbmodem5A680094911"
FOLLOWER_PORT = "/dev/tty.usbmodem5A680099311"
FPS = 25


def main(leader_port, follower_port, fps):
    dt = 1.0 / fps

    leader = SOLeader(SOLeaderTeleopConfig(port=leader_port, id="Leader"))
    follower = SOFollower(SOFollowerRobotConfig(port=follower_port, id="Follower"))

    leader.connect()
    print("Leader connected.")
    follower.connect()
    print("Follower connected.")
    print(f"Teleoperating at {fps} Hz. Press Ctrl-C to stop.\n")

    try:
        while True:
            t0 = time.perf_counter()

            action = leader.get_action()
            follower.send_action(action)

            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, dt - elapsed))

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        follower.disconnect()
        leader.disconnect()
        print("Both arms disconnected.")


if __name__ == "__main__":
    LEADER_PORT = "/dev/tty.usbmodem5A680094911"
    FOLLOWER_PORT = "/dev/tty.usbmodem5A680099311"
    FPS = 25

    main(LEADER_PORT, FOLLOWER_PORT, FPS)
