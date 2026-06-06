"""
SmolVLA live inference on an SO-101 follower arm.

Loads the model and robot ONCE, then drops into an interactive prompt so you
can switch tasks without restarting.

Usage:
    python smolvla_inference.py \
        --robot-port /dev/ttyACM0 \
        --robot-id my_follower \
        --camera-index 0 \
        --policy lerobot/smolvla_base

Interactive commands:
    <task text>   run inference for --steps steps with that task
    q / quit      disconnect and exit
    Ctrl+C        stop current task, return to prompt
"""

import argparse
import logging
import signal
import time

import torch

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# set by Ctrl+C inside a task run; cleared at the start of each new task
_stop_task = False


def _handle_sigint(sig, frame):
    global _stop_task
    _stop_task = True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SmolVLA interactive inference")
    p.add_argument("--robot-port", default="/dev/ttyACM0")
    p.add_argument("--robot-id", default="my_follower")
    p.add_argument("--camera-index", type=int, default=0,
                   help="OpenCV camera index — use `lerobot-find-cameras opencv`")
    p.add_argument("--camera-width", type=int, default=640)
    p.add_argument("--camera-height", type=int, default=480)
    p.add_argument("--camera-fps", type=int, default=30)
    p.add_argument("--policy", default="lerobot/smolvla_base",
                   help="HF repo or local path of your (fine-tuned) SmolVLA model")
    p.add_argument("--steps", type=int, default=200,
                   help="Inference steps to run per task command")
    p.add_argument("--step-delay", type=float, default=0.05,
                   help="Seconds between steps (~20 Hz at 0.05)")
    return p.parse_args()


def run_task(policy, robot, task: str, steps: int, step_delay: float, device: torch.device) -> None:
    global _stop_task
    _stop_task = False

    log.info("Running '%s' for %d steps — Ctrl+C to stop early", task, steps)

    for step in range(steps):
        if _stop_task:
            log.info("Task interrupted at step %d.", step)
            break

        obs = robot.get_observation()
        obs["task"] = task

        obs_device = {
            k: v.to(device) if isinstance(v, torch.Tensor) else v
            for k, v in obs.items()
        }

        with torch.inference_mode():
            action = policy.select_action(obs_device)

        robot.send_action(action)

        if step % 50 == 0:
            log.info("  step %d / %d", step, steps)

        time.sleep(step_delay)

    log.info("Done.")


def main() -> None:
    args = parse_args()
    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    log.info("Device: %s", device)

    # ── Load policy (once) ───────────────────────────────────────────────────
    log.info("Loading policy from '%s' …", args.policy)
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

    policy: SmolVLAPolicy = SmolVLAPolicy.from_pretrained(args.policy)
    policy = policy.to(device).eval()
    log.info("Policy loaded.")

    # ── Connect robot (once) ─────────────────────────────────────────────────
    log.info("Connecting to follower arm at %s …", args.robot_port)
    from lerobot.cameras.opencv import OpenCVCameraConfig
    from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

    cam_cfg = OpenCVCameraConfig(
        index_or_path=args.camera_index,
        width=args.camera_width,
        height=args.camera_height,
        fps=args.camera_fps,
    )
    robot_cfg = SO101FollowerConfig(
        port=args.robot_port,
        id=args.robot_id,
        cameras={"front": cam_cfg},
    )
    robot = SO101Follower(robot_cfg)
    robot.connect()
    log.info("Robot connected.")

    # ── Install Ctrl+C handler that stops the task but keeps the loop ────────
    signal.signal(signal.SIGINT, _handle_sigint)

    # ── Interactive prompt ───────────────────────────────────────────────────
    print("\n" + "=" * 52)
    print("  SmolVLA ready. Type a task and press Enter.")
    print(f"  Each command runs for {args.steps} steps (~{args.steps * args.step_delay:.0f}s).")
    print("  Ctrl+C stops the current task (robot stays connected).")
    print("  Type  q  or  quit  to exit.")
    print("=" * 52 + "\n")

    try:
        while True:
            try:
                task = input("task> ").strip()
            except EOFError:
                break

            if not task:
                continue
            if task.lower() in ("q", "quit", "exit"):
                break

            run_task(policy, robot, task, args.steps, args.step_delay, device)

    finally:
        robot.disconnect()
        log.info("Robot disconnected. Bye.")


if __name__ == "__main__":
    main()
