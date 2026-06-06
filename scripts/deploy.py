"""Run a trained policy on the robot. Run: uv run python scripts/deploy.py"""

import queue
import sys
import termios
import threading
import time
import tty
from pathlib import Path

import hydra
import rerun as rr
import yaml
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

from robot.config import make_robot_config
from robot.policy import SmolVLAPolicy, make_policy

REST_POS_FILE = Path(__file__).parent.parent / "dump" / "rest.yaml"


def go_to_rest(robot):
    rest = yaml.safe_load(REST_POS_FILE.read_text())
    robot.send_action({f"{j}.pos": v for j, v in rest.items()})


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg):
    policy = make_policy(cfg)
    is_smolvla = isinstance(policy, SmolVLAPolicy)

    robot = SOFollower(make_robot_config(cfg))
    robot.connect(calibrate=False)
    init_rerun(session_name=f"{cfg.deploy.policy_type}_inference")

    dt = 1.0 / cfg.robot.fps
    key_queue: queue.Queue = queue.Queue()

    def act_input_thread():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\x03", "\x04"):
                    key_queue.put("quit")
                    break
                elif ch in ("\r", "\n"):
                    key_queue.put("enter")
                elif ch in ("r", "R"):
                    key_queue.put("r")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def smolvla_input_thread():
        while True:
            val = input().strip()
            key_queue.put(("task", val))
            if val.lower() in ("q", "quit", "exit"):
                break

    threading.Thread(
        target=smolvla_input_thread if is_smolvla else act_input_thread,
        daemon=True,
    ).start()

    paused = threading.Event()
    paused.set()  # start paused
    steps_remaining = cfg.deploy.n_steps

    if is_smolvla:
        print("Enter a task description to start.")
    else:
        print(f"Task: '{list(cfg.deploy.tasks)[0]}'")
        print("Press Enter to start.  Enter=pause/resume  R=rest  Ctrl-C=quit")

    try:
        while True:
            t0 = time.perf_counter()
            raw_obs = robot.get_observation()
            log_rerun_data(observation=raw_obs, action=None)

            try:
                key = key_queue.get_nowait()
            except queue.Empty:
                key = None

            if is_smolvla:
                if key is not None:
                    tag, val = key if isinstance(key, tuple) else ("ctrl", key)
                    if tag == "ctrl" and val == "quit":
                        break
                    elif tag == "task":
                        if val.lower() in ("q", "quit", "exit"):
                            break
                        elif val == "":
                            if paused.is_set():
                                paused.clear()
                                steps_remaining = cfg.deploy.n_steps
                                policy.reset()
                                print(f"Resumed '{policy.task}'. Enter to pause.")
                            else:
                                paused.set()
                                print("Paused. Enter to resume or type new task.")
                        else:
                            policy.task = val
                            paused.clear()
                            steps_remaining = cfg.deploy.n_steps
                            policy.reset()
                            print(f"Running '{val}'. Enter to pause.")
            else:
                if key == "quit":
                    break
                elif key == "enter":
                    if paused.is_set():
                        paused.clear()
                        policy.reset()
                        print("\nRunning. Enter to pause.")
                    else:
                        paused.set()
                        print("\nPaused. Enter to resume, R to rest.")
                elif key == "r":
                    paused.set()
                    go_to_rest(robot)
                    print("\nAt rest. Enter to resume.")

            if not paused.is_set():
                action = policy.step(raw_obs)
                robot.send_action(action)
                log_rerun_data(observation=raw_obs, action=action)

                if is_smolvla:
                    steps_remaining -= 1
                    if steps_remaining == 0:
                        steps_remaining = cfg.deploy.n_steps
                        policy.reset()

            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, dt - elapsed))

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        rr.rerun_shutdown()
        robot.disconnect()
        print("Robot disconnected.")


if __name__ == "__main__":
    main()
