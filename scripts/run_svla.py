"""
Minimal SmolVLA inference loop for the SO-101 follower arm.

Usage:
    python scripts/run_smolvla.py \
        --pretrained lerobot/smolvla_base \
        --port /dev/tty.usbmodem5A680099311 \
        --cam-index 0 \
        --device mps

At the prompt, type a task description (e.g. "pick up the red cube") and press
Enter. The policy executes for --n-action-steps steps, then prompts again.
Ctrl-C disconnects the robot cleanly.

--- How SmolVLA works ---

Input:
    SmolVLA takes three input streams, concatenated along the transformer sequence dimension:
      - Visual tokens: image resized+padded to 512x512, rescaled to [-1,1], encoded by SigLIP
        into patch embeddings.
      - Text tokens: task string tokenized by the SmolVLM tokenizer into language embeddings.
      - State tokens: 6 joint positions linearly projected into the token space.
    These are processed jointly by the SmolVLM language model backbone. Its output features
    are then passed to a separate action expert (flow-matching diffusion transformer) which
    denoises a noisy action sequence into a clean action chunk.

Output:
    A chunk of `chunk_size=50` actions, each a (6,) float32 vector of joint positions.

Action unrolling:
    Inference is expensive (the full VLM + diffusion forward pass). To amortize the cost,
    the model predicts 50 actions at once and loads them into a deque. select_action() pops
    one action per call without re-running the model until the deque is empty.

    Timeline with chunk_size=50, fps=25:
        t=0ms    deque empty → run inference (e.g. 500ms on MPS)
        t=500ms  pop a0 → send_action, sleep remainder to hit 40ms budget
        t=540ms  pop a1 → send_action
        ...
        t=2500ms pop a49 → send_action
        t=2540ms deque empty → run inference again

    The loop calls select_action() at 25 Hz. When the deque has items the call is
    near-instant (just a deque pop). When it is empty the call blocks on inference,
    which may take hundreds of ms — that one step overruns its budget, then the loop
    resumes at 25 Hz for the next 49 steps.

Open-loop behaviour and the n_action_steps knob:
    Within a chunk the policy is open-loop: all 50 actions were predicted from a single
    frame snapshot and the robot follows them regardless of what happens in the scene.
    The effective re-planning rate is fps / n_action_steps (0.5 Hz at defaults).

    `n_action_steps` controls how many actions from each predicted chunk are loaded into
    the deque before discarding the rest. Setting it smaller than chunk_size forces earlier
    re-inference with a fresh frame, at the cost of more frequent (expensive) inference:

        n_action_steps=50  →  re-plan every 2s   (default, lowest compute)
        n_action_steps=10  →  re-plan every 0.4s (more reactive, 5x inference cost)

    Temporal ensemble (not implemented here) is an alternative: run inference every step
    and average overlapping chunk predictions with exponential weighting. This is what
    the LeRobot async_inference RobotClient uses (aggregate_fn=weighted_average).
"""

import queue
import threading
import time

import rerun as rr
import torch

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]
NUM_JOINTS = len(JOINT_NAMES)


def build_policy(pretrained: str, device: str):
    # Load the pretrained config as-is so normalization stats (mean/std) are preserved.
    # Injecting a fresh SmolVLAConfig would wipe those stats and produce garbage actions.
    policy = SmolVLAPolicy.from_pretrained(pretrained_name_or_path=pretrained)
    policy.to(device)
    policy.eval()
    return policy, policy.config


def make_batch(robot_obs: dict, task: str, cam_key: str, policy_image_keys: list[str]) -> dict:
    """Convert raw robot observation to the dict format the preprocessor expects.

    smolvla_base was trained with cameras named camera1/2/3 at 256x256.
    We map our single wrist cam to camera1 and leave camera2/3 as black frames
    (zero-filled, masked out by the model via empty_cameras padding logic).
    """
    state = torch.tensor([robot_obs[f"{j}.pos"] for j in JOINT_NAMES], dtype=torch.float32).unsqueeze(0)  # (1, 6)

    # HxWxC uint8 numpy array from camera → (1, C, H, W) in [0, 1]
    img_np = robot_obs[cam_key]
    img = torch.from_numpy(img_np).permute(2, 0, 1).float().unsqueeze(0) / 255.0  # (1, C, H, W)

    batch = {
        "observation.state": state,
        "task": [task],
    }

    for i, key in enumerate(policy_image_keys):
        if i == 0:
            batch[key] = img
        else:
            # Black frame + padding mask=False so the model ignores it
            batch[key] = torch.zeros_like(img)
            batch[f"{key}_padding_mask"] = torch.zeros(1, dtype=torch.bool)

    return batch


def action_to_dict(action: torch.Tensor) -> dict:
    """Convert a (6,) tensor to the dict format robot.send_action expects."""
    return {f"{j}.pos": action[i].item() for i, j in enumerate(JOINT_NAMES)}


def main(pretrained, port, cam_index, device, fps, n_action_steps):
    cam_key = "wrist_cam"
    dt = 1.0 / fps

    # --- robot ---
    robot_cfg = SOFollowerRobotConfig(
        port=port,
        id="Follower",
        cameras={
            cam_key: OpenCVCameraConfig(
                index_or_path=cam_index,
                width=640,
                height=480,
                fps=fps,
            )
        },
    )
    robot = SOFollower(robot_cfg)
    robot.connect()
    print("Robot connected.")

    init_rerun(session_name="smolvla_inference")

    # --- policy + processors ---
    print(f"Loading SmolVLA from '{pretrained}' ...")
    policy, cfg = build_policy(pretrained, device)
    policy_image_keys = list(cfg.image_features.keys())
    print(f"Policy image keys: {policy_image_keys}")
    device_override = {"device_processor": {"device": device}}
    preprocessor, postprocessor = make_pre_post_processors(
        policy_cfg=cfg,
        pretrained_path=pretrained,
        preprocessor_overrides=device_override,
        postprocessor_overrides=device_override,
    )
    print("Policy ready.\n")

    prompt_queue = queue.Queue()
    paused = threading.Event()

    def prompt_thread():
        while True:
            val = input().strip()
            prompt_queue.put(val)
            if val.lower() in ("quit", "q", "exit"):
                break

    threading.Thread(target=prompt_thread, daemon=True).start()

    task = None
    steps_remaining = 0

    print("Enter a task description to start.")

    try:
        while True:
            t0 = time.perf_counter()

            raw_obs = robot.get_observation()
            log_rerun_data(observation=raw_obs, action=None)

            try:
                new_val = prompt_queue.get_nowait()
            except queue.Empty:
                new_val = None

            if new_val is not None:
                if new_val.lower() in ("quit", "q", "exit"):
                    break
                elif new_val == "":
                    # Enter toggles pause/resume
                    if paused.is_set():
                        paused.clear()
                        steps_remaining = n_action_steps
                        policy.reset()
                        print(f"Resumed '{task}'. Press Enter to pause.")
                    else:
                        paused.set()
                        print("Paused. Press Enter to resume, or type a new task.")
                else:
                    task = new_val
                    paused.clear()
                    steps_remaining = n_action_steps
                    policy.reset()
                    print(f"Running '{task}'. Press Enter to pause.")

            if task and not paused.is_set():
                batch = make_batch(raw_obs, task, cam_key, policy_image_keys)

                processed = preprocessor(batch)
                processed = {
                    k: v.to(device) if isinstance(v, torch.Tensor) else v
                    for k, v in processed.items()
                }

                action_tensor = policy.select_action(processed)
                action_tensor = postprocessor(action_tensor)

                action = action_tensor.squeeze()
                print(f"  action: {[f'{v:.3f}' for v in action.tolist()]}")
                action_dict = action_to_dict(action)
                robot.send_action(action_dict)
                log_rerun_data(observation=raw_obs, action=action_dict)

                steps_remaining -= 1
                if steps_remaining == 0:
                    steps_remaining = n_action_steps
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
    PRETRAINED = "taehunkim/so101_smolvla_pick_cube"
    PORT = "/dev/tty.usbmodem5A680099311"
    CAM_INDEX = 0
    DEVICE = "mps"
    FPS = 25
    N_ACTION_STEPS = 50  # actions to execute per inference; smaller = more reactive

    main(PRETRAINED, PORT, CAM_INDEX, DEVICE, FPS, N_ACTION_STEPS)
