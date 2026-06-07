# VLA-DataEngine Demo

## One-liner

We use Claude as a VLM scoring engine — turning raw teleoperation videos into rich, structured synthetic training data without a single human annotation.

---

## The problem we solve

Human annotation is the real bottleneck in robot learning. Recording teleoperation episodes takes minutes. Writing semantically rich descriptions and preference labels for every trajectory frame takes hours. Standard imitation learning then caps out at the quality of those demonstrations.

We cut the annotation bottleneck entirely: Claude watches the raw video, scores trajectories, and generates dense synthetic labels — machine-ready training signal in seconds.

---

## Demo flow (2 minutes)

### Act 1 — Live teleoperation [0:00–0:30]

Operate the SO-101 leader arm to perform a task (e.g., pick up the vial and place it in the bin). The follower arm mirrors the motion. The wrist camera records the episode — video + joint trajectory saved automatically via LeRobot.

**Voiceover:** *"This is how robot data is collected today. A human demonstrates the task. The arm records it. One episode, 30 seconds. Now watch what happens to this raw recording."*

---

### Act 2 — Claude scores the trajectory [0:30–1:10]

Run the labeler live on the just-recorded episode:

```bash
python scripts/rl_vlm_f_labeler.py \
  --video data/dataset/videos/.../file-000.mp4 \
  --task "pick up the vial and place it in the bin" \
  --pairs 5 --out /tmp/demo_prefs.jsonl
```

Show Claude's API response streaming in the terminal: it compares frame pairs, reasons about which shows better progress toward the goal, and outputs structured preference labels.

**Voiceover:** *"Claude watches the same video a human annotator would. It compares frames, judges which trajectory segment is closer to the goal, and produces structured JSONL — preference pairs, task descriptions, dense semantic labels. This took 40 seconds. A human would take 2 hours and produce less consistent output."*

Display a sample output block:

```json
{
  "chosen": "frame_0042",
  "rejected": "frame_0018",
  "reason": "frame_0042 shows the gripper directly above the vial with wrist aligned; frame_0018 has the arm extended past the target with poor approach angle",
  "task": "pick up the vial and place it in the bin",
  "reward": 0.83
}
```

---

### Act 3 — Synthetic augmentation [1:10–1:45]

Show the full dataset output: from 1 raw episode, Claude generated N preference pairs, M task description variants, and dense per-frame reward scores — a complete synthetic dataset ready for policy training.

**Voiceover:** *"One teleoperation session. No human labeler. The output is a structured dataset that any imitation learning or RLHF pipeline can consume directly. This is the product: we compress weeks of annotation into minutes."*

---

### Act 4 — What comes next [1:45–2:00]

Show a single diagram or slide:

```
Teleoperate → Video + Trajectory
      ↓
  Claude VLM Scoring (THIS DEMO)
      ↓
  Synthetic Dataset
      ↓
  Policy Fine-tuning (SmolVLA / ACT)
      ↓
  Autonomous Robot — no human in the loop
```

**Voiceover:** *"What you just saw is the data layer. The next step — already architected — feeds this synthetic dataset back into a policy that runs the robot autonomously. The robot becomes its own data generator. That is the full loop we are building."*

---

## The full vision

The demo shows step 1 and 2. The complete system:

1. **Record** raw teleoperation episodes (20 min, one session)
2. **Score** automatically with Claude as preference oracle (< 1 min per episode)
3. **Train** SmolVLA or ACT on the synthetic dataset (local M4 or HPC H100)
4. **Deploy** autonomous policy on the SO-101 — robot executes without human guidance
5. **Loop** — the autonomous robot generates new episodes, Claude scores them, the policy improves

Steps 3–5 are the harder system we are building. Today's demo proves the data layer works.

---

## Technical stack

| Component | Implementation |
|---|---|
| Hardware | SO-101 leader + follower, wrist camera |
| Data capture | LeRobot teleoperation stack |
| Scoring | `scripts/rl_vlm_f_labeler.py` — Claude, RL-VLM-F protocol |
| Output format | JSONL preference pairs + per-frame reward scores |
| Downstream (roadmap) | SmolVLA / ACT fine-tuning, autonomous inference |

---

## Fallback plan

| Risk | Fallback |
|---|---|
| Arm unavailable | Run labeler on pre-recorded video — scoring pipeline is the demo, not the arm |
| API latency | Pre-run labeler, show stored output live — streaming terminal is cosmetic |
| LeRobot capture fails | Use any pre-recorded .mp4 from `data/dataset/videos/` |
