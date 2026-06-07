# EuroTech x Hong Kong Talent Engage Hackathon LeRobot Tutorial

<!-- ==========================
     Preface
========================== -->
<!--
"To truly learn robotics, you need a strong mindset:
 Everything in robotics is made by humans.
 If others can figure it out, so can I.
 There's no magic here, only things I don't understand yet.
 One day, I'll know every detail and how everything works inside."

 - Software cluster team lead of RoboTUM
-->

## ⚠️ macOS Users — Read This First

**Intel RealSense cameras do not work on macOS (including all M-series chips).** If you are on a Mac and your setup uses a RealSense camera, you will not be able to record datasets on your machine.

**What to do:**
- Find a teammate with a Linux laptop and use their machine for teleoperation and recording
- Do the environment setup and get familiar with the codebase on your Mac, but plan to switch before the recording phase
- USB webcams (OpenCV cameras) do work on macOS — so if your setup only uses those, you're fine

Do not wait until you reach the camera section to figure this out. Coordinate with your team now.

---

## 0. Foreword

Hello dear participants!

This README will help you set up your LeRobot leader + follower arms for the EuroTech x Hong Kong Talent Engage Hackathon. It compiles the most useful information from various sources for a quick start. The LeRobot project is unique in that once everything is set up, it is comparably easy to train models that work. We are excited to see what you can accomplish with the SO101 pairs and hope you'll be able to tackle the challenges of the next two days.

This guide will mainly cover the prerequisites for imitation-based learning. If you're comfortable with some of the supported simulation environments or want to test them as well, you'll need to explore that on your own.

**We are excited to see what you come up with!**

### 0.1 Additional Resources

While there are many good tutorials available, it can be challenging to grasp everything, especially in such a short time. It's easy to feel overwhelmed. For most of you, it might be best to stick to this README; however, we don't explain everything in detail here. Please read through the documentation alongside this guide — otherwise you might miss important context that could be very helpful.

**Recommended resources:**

- `.md` files in the repository you're downloading
- [HuggingFace documentation](https://huggingface.co/docs/lerobot/en/getting_started_real_world_robot) with examples for different arms
- Videos on YouTube
- Model-specific documentation:
  - SmolVLA: [SmolVLA Documentation](https://huggingface.co/docs/lerobot/en/smolvla)
  - GR00T: [NVIDIA Isaac GR00T in LeRobot](https://huggingface.co/blog/nvidia/nvidia-isaac-gr00t-in-lerobot), [Post-Training Isaac GR00T N1.5 for LeRobot SO-101](https://huggingface.co/blog/nvidia/gr00t-n1-5-so101-tuning)

If you want to understand exactly what's happening under the hood, feel free to explore the code. LLMs can also be very helpful for understanding!

---

## 0.2 Power Supply — Read This Before You Touch Anything

> **⚠️ CRITICAL: Using the wrong voltage can damage the servos permanently.**

The two arms require different voltages:

| Arm | Role | Required Voltage |
|-----|------|-----------------|
| **Leader** (no gripper, you hold it) | Teleoperator | **5 V** |
| **Follower** (has gripper, does the work) | Robot | **12 V** |

**Always double-check which power supply is plugged into which arm before switching anything on.** The connectors are often the same, so it is easy to mix them up. If a servo feels unusually hot or does not respond, power off immediately and verify.

---

## 0.3 Common Hardware Problems

Before blaming the software, run through this checklist whenever motors are not detected, IDs are missing, or motion is erratic.

**Motor / servo not recognized:**
- Check every servo-to-servo cable along the chain — a single jumped or half-inserted connector breaks communication for everything downstream
- Wiggle each connector gently; if the arm suddenly appears, reseat that cable properly
- Verify the correct voltage is supplied (see above)
- Try a different USB cable between the arm and your computer
- Reboot the computer and replug the arm — OS-level USB issues are common

**Wrong or duplicate motor IDs:**
- If you see unexpected IDs or none at all, the motor ID setup may have been corrupted — see Section 4.2 for how to redo it
- Only one arm should be connected when running `lerobot-setup-motors`; having both plugged in at once can cause ID conflicts

**Arm moves but behaves erratically:**
- Re-run calibration (Section 4.3) — a bad calibration file is the most common cause
- Make sure the arm can physically reach its full range without hitting itself or the table during calibration

**General rule:** hardware problems are almost always mechanical (loose cable, wrong power) rather than software. Check the physical setup first.

---

## 1. Set Up Your Python Environment

You have two options. **uv** is faster and handles Python versions automatically. **venv** is the classic built-in approach and needs no extra install.

### Option A — uv (Recommended: faster, simpler)

Install uv:

- **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Then restart your terminal (or run `source ~/.bashrc` / `source ~/.zshrc`).

- **Windows:**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

**Check installation:**

```bash
uv --version
```

> **More info:** https://docs.astral.sh/uv/getting-started/installation/

### Option B — Python venv (Classic, no extra tools needed)

Make sure Python 3.12 is installed on your system (https://www.python.org/downloads/), then continue — the environment creation commands are shown in Section 3 below.

---

## 2. Install FFmpeg (Required)

LeRobot uses FFmpeg for video handling and logging demonstrations.

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### Windows

Download from https://ffmpeg.org/download.html and add it to your `PATH`, or use:

```powershell
winget install ffmpeg
```

---

## 3. Clone LeRobot and Set Up the Environment

Clone the LeRobot repository:

```bash
git clone https://github.com/huggingface/lerobot.git
cd lerobot
```

Create and activate a virtual environment — pick the path that matches your choice in Section 1:

#### Option A — uv

```bash
uv venv --python 3.12
```

Activate:

- **macOS / Linux:** `source .venv/bin/activate`
- **Windows:** `.venv\Scripts\activate`

Install LeRobot and the Feetech SDK:

```bash
uv pip install -e .
uv pip install -e ".[feetech]"
```

#### Option B — venv

```bash
python3.12 -m venv .venv
```

Activate:

- **macOS / Linux:** `source .venv/bin/activate`
- **Windows:** `.venv\Scripts\activate`

Install LeRobot and the Feetech SDK:

```bash
pip install -e .
pip install -e ".[feetech]"
```

> **NOTE:** If you encounter build errors, you may need system-level dependencies (`cmake`, `build-essential`, `ffmpeg` dev libs). Check the LeRobot README for details: https://github.com/huggingface/lerobot

---

## 4. General Setup of Your Arms

> **NOTE:** You'll need to choose between following the *LeRobot documentation* and *this shorter README*.
> It's recommended to review both. The official documentation is more rigorous and covers everything from robot assembly.

The official documentation for the SO101 arms can be found in your cloned project folder at:

```
lerobot/docs/source
```

**Important files you'll find there:**

- **so101.mdx** → Tutorial for the SO-101 leader and follower arms
- **cameras.mdx** → Tutorial for setting up cameras
- And others

These files contain the official step-by-step guides created by the LeRobot team. They explain:

- How to wire your arm
- How to identify and check COM ports
- How to test communication
- How to calibrate motors

Participants should read through these before running any code to avoid common hardware mistakes (port mismatches, incorrect motor connections, wrong IDs, etc.).

### If You Choose to Stick with Us for Chapter 4

This section is a shortened version of the so101.mdx file for the hackathon, since assembly and motor ID setup have already been completed.

Here we quickly cover CLI commands and guide you through:

- Finding ports
- Calibrating leader/follower
- Teleoperation
- Helpful example commands

### 4.1 Find Ports

To automatically detect which port corresponds to which arm:

```bash
lerobot-find-port
```

Follow the instructions and note down the port for your follower and leader arm.

### 4.2 Setup Motors if Servos Are Not Recognized (SKIP FOR NOW)

This has already been done for your arms. However, from experience we know it might happen that you'll need to redo this.

> **IMPORTANT NOTE:** This is a tedious process.

**Troubleshooting steps:**
- Check wiring on the robot arms themselves
- Check whether you're using the correct power supply (5V for Leader, 12V for Follower)
- Sometimes rebooting your PC or reseating cables will fix this

> **For Camera Usage:** If connecting multiple USB devices through one hub/dongle, make sure the port supports the required bandwidth.

**Setup motors - Follower:**

```bash
lerobot-setup-motors \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0
```

**Setup motors - Leader:**

```bash
lerobot-setup-motors \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1
```

### 4.3 Calibrate Your Arms

Proper calibration ensures the leader and follower share the same "neutral positions," which is essential for precise teleoperation and model training. The `lerobot-calibrate` script will interactively guide you through the process. Calibration files are stored locally on your computer.

**Make sure you know the center position and that your arms can move through their full range of motion.**

**During calibration:**

1. Move all 6 follower joints (motors) to their neutral center positions
2. Press Enter
3. Move each joint slowly through its full range of motion
4. Press Enter when requested

#### Follower

```bash
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=Follower
```

For `robot.port`, use **your port**.

#### Leader

```bash
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=Leader
```

For `teleop.port`, use **your port**.

#### API Alternative

```python
from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader

config = SO101LeaderConfig(
    port="/dev/tty.usbmodem58760431551",
    id="my_awesome_leader_arm",
)

leader = SO101Leader(config)
leader.connect(calibrate=False)
leader.calibrate()
leader.disconnect()
```

> **NOTE:** On Windows, line breaks via `\` do not work in the terminal. Reshape the command into a single line without backslashes.

---

## 5. Teleoperation Test — Finally!

Once the follower and leader are configured and calibrated, you can test teleoperation. **Watch out for the gripper camera!**

> **CAUTION:** If something moves incorrectly, never try to physically restrain the robot.

In case of unsafe behavior, kill the process immediately with:

**CTRL + C**

If the motors/joints lock up after stopping the code, unblock them by disconnecting the power supply, waiting a few seconds, and reconnecting.

### First Teleoperation

Make sure to substitute your actual ports and IDs:

```bash
lerobot-teleoperate \
  --teleop.type=so101_leader \
  --teleop.port=YOURLEADERPORT \
  --teleop.id=YOURLEADERID \
  --robot.type=so101_follower \
  --robot.port=YOURFOLLOWERPORT \
  --robot.id=YOURFOLLOWERID
```

**For Windows users (single line):**

```
lerobot-teleoperate --teleop.type so101_leader --teleop.port YOURLEADERPORT --teleop.id YOURLEADERID --robot.type so101_follower --robot.port YOURFOLLOWERPORT --robot.id YOURFOLLOWERID
```

---

## 6. Bring Light into the Darkness

Previously we mentioned the `cameras.mdx` file. Please take a look at it.

RealSense cameras are not stable on macOS (especially M-series chips), and some of you might have trouble with installation. There are workarounds, but it might be easier to teleoperate and record using someone else's Linux machine.

### 6.1 Camera Installation Guide

#### OpenCV Camera (Gripper Cam)

You'll need `cv2`, provided by `opencv-python`. This is likely already installed as a core LeRobot dependency.

#### Linux Only

On Ubuntu/Debian, the Python package alone is sometimes not enough. You might see:

```
ImportError: libGL.so.1: cannot open shared object file
```

Fix:

```bash
sudo apt-get update
sudo apt-get install ffmpeg libsm6 libxext6 -y
```

#### Intel RealSense Depth Camera

Install via pip:

```bash
uv pip install -e ".[intelrealsense]"
```

If you hit dependency issues, install the [RealSense SDK 2.0](https://github.com/IntelRealSense/librealsense) first. You can then verify your camera and update its firmware with:

```bash
realsense-viewer
```

### 6.2 Camera Usage

Follow `cameras.mdx` in your cloned project to find the OpenCV index and RealSense serial number. You can also use:

```bash
lerobot-find-cameras opencv   # or: lerobot-find-cameras realsense
```

Then run teleoperation with cameras:

```bash
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=Follower \
  --robot.cameras='{ \
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, \
    front: {type: intelrealsense, serial_number_or_name: 839212070000, width: 848, height: 480, fps: 30, use_depth: true} \
  }' \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=Leader \
  --display_data=True
```

`--display_data=True` opens a Rerun window showing live camera feeds and joint positions.

---

## 7. Recording a Dataset

You have completed all the steps for imitation-based learning. Before you start recording, think about:

- What task you want the robot to learn
- Which pre-trained policy you want to fine-tune (if any)
- How to keep your workspace consistent across every episode

### 7.1 Best Practices — Read Before You Record

Getting the data right matters more than anything else. A policy trained on 80 clean episodes will outperform one trained on 200 messy ones.

#### Keep Your Setup Stable

- **Do not move the cameras between episodes.** Even a small shift changes what the model sees at inference time and will hurt performance.
- **Fix your camera positions before recording episode 1** and leave them there for the entire dataset.
- **Keep lighting conditions stable.** VLA models are particularly sensitive to changes in illumination — shadows, sunlight shifting, overhead lights flickering. Close the blinds, use consistent artificial lighting, and avoid recording across different times of day if you can.
- **Keep the workspace clear.** Remove objects not relevant to the task — the model will try to learn from everything it sees.

#### How to Record Good Episodes

- **Vary starting positions.** Don't always place the object in the same spot. Spread it across the reachable workspace so the policy learns to generalize.
- **Include edge cases.** Record from slightly different angles, distances, and orientations. The more variety in the demonstrations, the more robust the policy.
- **Aim for at least 80 episodes.** Below that, most policies will overfit or fail to generalize. More is better, but only if the quality is there.
- **Move smoothly and deliberately.** Shaky or hesitant motion gets baked into the policy. Slow down, be intentional, complete the full task before stopping.
- **Keep your hands out of frame.** If your hand appears in the camera view during the episode, the model may try to imitate the hand rather than the gripper.

#### When to Rerecord

Discard and rerecord an episode if any of the following happened:

- The task was not completed successfully
- Motion was shaky, jerky, or inconsistent
- The arm collided with something or moved erratically
- A hand or body part entered the camera frame
- The object was knocked out of place mid-episode and the arm continued anyway
- Anything felt "off" — trust your instincts

**Quality over quantity. One bad episode in your dataset is worse than no episode at all.**

### 7.2 The lerobot-record Command

Use the `record.py` script to collect demonstrations. Run it from the root of your cloned LeRobot repo. Here is a full example with two cameras (front + wrist):

```bash
python src/lerobot/scripts/record.py \
  --robot.type=so101_follower \
  --robot.port=YOURFOLLOWERPORT \
  --robot.id=FOLLOWER \
  --robot.cameras='{
    front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, warmup_s: 2},
    wrist: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, warmup_s: 2}
  }' \
  --teleop.type=so101_leader \
  --teleop.port=YOURLEADERPORT \
  --teleop.id=LEADER \
  --dataset.repo_id=YOUR_HF_USERNAME/YOUR_DATASET_NAME \
  --dataset.root=data \
  --dataset.num_episodes=80 \
  --dataset.single_task="Describe your task here" \
  --dataset.push_to_hub=false \
  --display_data=true
```

**Key flags explained:**

| Flag | What it does |
|------|-------------|
| `--robot.cameras` | Defines which cameras to use and their settings. Each camera needs a name (e.g. `front`, `wrist`), a type, and an index or device path |
| `index_or_path` | Camera index (0, 1, 2…) or a device path. Use `lerobot-find-cameras opencv` to find the right index for each camera |
| `warmup_s` | Seconds to let the camera warm up before recording starts — helps avoid dark or blurry first frames |
| `--dataset.repo_id` | HuggingFace Hub repo where the dataset will be uploaded (if push is enabled) |
| `--dataset.root` | Local folder where episode data is saved during recording (e.g. `data`) |
| `--dataset.num_episodes` | How many episodes to record in this session |
| `--dataset.single_task` | A short natural language description of the task (e.g. `"Grab the grey circle"`) — used as a label in the dataset |
| `--dataset.push_to_hub` | Set to `true` to upload to HuggingFace Hub after recording, `false` to keep local only |
| `--display_data=true` | Opens a Rerun window showing live camera feeds and joint states while recording |

#### Keyboard Controls During Recording

| Key | Action |
|-----|--------|
| `→` (Right arrow) | **Stop the current episode early** and save it — use this when the task is done and you don't want to record unnecessary motion |
| `←` (Left arrow) | **Discard and rerecord** the current episode — use this immediately if something went wrong |

> **TIP:** Get comfortable with the left arrow. Using it freely to throw away bad episodes is exactly the right habit.

---

## 8. Train a Policy

Once you have recorded enough demonstrations, it's time to train a policy. LeRobot ships a ready-to-use training script — you don't need to write any training code yourself to get started.

### 8.1 The Train Script

The script lives inside the LeRobot repository at:

```
lerobot/scripts/train.py
```

You can also call it directly from the terminal via the CLI entrypoint (no need to reference the file path):

```bash
lerobot-train --help
```

### 8.2 Running Training from the Terminal

Here is a full example. Replace the dataset, output paths, and job name with your own:

```bash
lerobot-train \
  --dataset.repo_id=YOUR_HF_USERNAME/YOUR_DATASET \
  --policy.type=act \
  --policy.use_vae=true \
  --policy.use_amp=true \
  --batch_size=16 \
  --steps=60000 \
  --log_freq=50 \
  --save_checkpoint=true \
  --save_freq=10000 \
  --output_dir=outputs/act_run \
  --job_name=act_run \
  --resume=false
```

> **NOTE:** The `!` prefix in the example above is Kaggle/Jupyter notebook syntax. In a normal terminal, drop the `!` and run the command as shown.

If you want to push the trained policy to the HuggingFace Hub so you can load it later or share it:

```bash
  --policy.push_to_hub=true \
  --policy.repo_id=YOUR_HF_USERNAME/YOUR_POLICY_NAME
```

**Key flags explained:**

| Flag | What it does |
|------|-------------|
| `--dataset.repo_id` | HuggingFace dataset to train on (e.g. `your-hf-username/my-dataset`) |
| `--dataset.root` | Optional local path if the dataset is already downloaded |
| `--policy.type` | Which policy architecture to use (see Section 7.3) |
| `--batch_size` | Number of transitions per gradient step — lower if you run out of VRAM |
| `--steps` | Total number of training steps |
| `--log_freq` | How often (in steps) to print/log metrics |
| `--save_checkpoint` | Whether to save model checkpoints |
| `--save_freq` | Save a checkpoint every N steps |
| `--output_dir` | Where to write checkpoints and logs |
| `--job_name` | A human-readable name for this run |
| `--resume` | Set to `true` to continue from the last checkpoint in `output_dir` |
| `--policy.push_to_hub` | Upload the final policy to HuggingFace Hub |
| `--policy.repo_id` | Hub repo to push to (e.g. `your-hf-username/my-policy`) |

### 8.3 Choosing a Policy

LeRobot supports several policy architectures. Here is a quick overview:

| Policy | `--policy.type` | Best for | Weight |
|--------|----------------|----------|--------|
| **ACT** | `act` | Pick-and-place, short-horizon tasks. Fast to train, reliable. | Light |
| **Diffusion Policy** | `diffusion` | Tasks requiring smooth, multimodal trajectories. Slightly slower to train but often more robust. | Light |
| **SmolVLA** | `smolvla` | Vision-language conditioned tasks — give the robot a text instruction. Good balance of capability and size. | Medium |
| Pi0 | `pi0` | Highly capable generalist VLA, but requires significant compute and data. | Heavy |
| GR00T | *(via NVIDIA fine-tuning guide)* | NVIDIA's generalist robot foundation model. | Very heavy |

**Our recommendation for the hackathon:** start with **ACT** (`--policy.type=act`) or **Diffusion Policy** (`--policy.type=diffusion`). They train in reasonable time on a GPU, are well-documented, and work well with 50–200 demonstrations. If your task involves natural language instructions, try **SmolVLA** (`--policy.type=smolvla`).

Avoid Pi0 and GR00T unless you have access to a powerful multi-GPU machine — they are excellent models but not practical to fine-tune in a hackathon setting.

**ACT-specific flags worth knowing:**

```bash
--policy.use_vae=true      # enables the VAE for latent action chunking — keep this true for ACT
--policy.use_amp=true      # mixed precision training, speeds things up on modern GPUs
--policy.chunk_size=100    # number of actions predicted per inference step (default 100)
--policy.n_action_steps=100
```

**Diffusion Policy-specific flags:**

```bash
--policy.n_action_steps=8    # how many steps to execute per diffusion inference
--policy.num_inference_steps=10  # denoising steps — lower = faster inference, slightly lower quality
```

### 8.4 Writing Your Own Training Script

If you want more control — custom data augmentation, a different optimizer schedule, logging to Weights & Biases, etc. — you can write your own script on top of LeRobot's building blocks. The official `train.py` is a good starting point to copy and modify:

```
lerobot/scripts/train.py
```

The key classes you'll interact with are `LeRobotDataset`, the policy class for your chosen architecture, and the standard PyTorch training loop. LLMs are genuinely useful here for understanding the internals quickly.

---

## Good Luck!

You now have everything you need: arms calibrated, data recorded, and a training pipeline ready to go. Keep episodes consistent, start with a simple task, and iterate fast. Have fun — and don't be afraid to ask for help!

