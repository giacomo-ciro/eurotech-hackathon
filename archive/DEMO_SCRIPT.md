# MedVLA Bootstrapping Engine — 2-Minute Demo Script

## Overview

This document contains the demo script and project deliverables for **MedVLA**, our hackathon submission: a self-contained domain-adaptation engine that bridges Claude's semantic expertise with SmolVLA's edge execution to deploy specialized robotic intelligence in hours, not months.

---

## Demo Script

### [0:00 – 0:15] Act 1: The Domain Bottleneck

**Visual:** Tight shot of the robot arm standing still. Screen split shows a terminal window. Type a complex command into a vanilla model: `"Isolate the biohazard vacutainer."` The arm twitches or fails to move.

**Voiceover:**
> "Small, efficient Vision-Language-Action models like SmolVLA are the future of edge robotics. But they have a major limitation: they don't know specialized, high-stakes domain vocabulary. If you ask a vanilla model to 'isolate a biohazard vacutainer,' it fails completely because it lacks the semantic grounding. Standard data pipelines take months to fix this."

---

### [0:15 – 0:45] Act 2: The Claude Synthetic Engine

**Visual:** Cut to a screen recording of the pipeline running on the M4 Mac Pro. Show an image of a standard blue test tube on a desk. On screen, show Claude's API streaming a JSON response containing technical medical variants (`"Extract the 10mL sodium-citrate vacutainer..."`).

**Voiceover:**
> "To solve this, we built a self-contained domain-adaptation engine. We collected just a few raw, unlabelled physical demonstrations. We then pass the camera frames to Claude, acting as an automated medical data engineer. Claude generates dense, highly technical medical descriptions for every trajectory, instantly bootstrapping our raw physical data into hundreds of specialized medical training episodes."

---

### [0:45 – 1:15] Act 3: Local M4 Fine-Tuning

**Visual:** Quick shot of Activity Monitor showing local GPU/MPS utilization on the M4 Mac Pro, then jump straight to the LeRobot training completion log showing fast convergence.

**Voiceover:**
> "Because SmolVLA is incredibly efficient, we don't need a massive cloud cluster. We pull this synthetically augmented dataset directly into LeRobot and fine-tune the 450M parameter model locally on our M4 Mac Pro using Apple Silicon acceleration. Training takes less than twenty minutes."

---

### [1:15 – 1:45] Act 4: The Payoff — Successful Execution

**Visual:** Back to the physical arm. Type the exact same medical command: `"Isolate the biohazard vacutainer."` The arm smoothly drops down, accurately targets the blue tube, and begins moving it.

**Voiceover:**
> "Now, let's test it. We issue the exact same specialized medical command. The model instantly maps the medical lexicon to physical motor tokens. And because we utilize SmolVLA's asynchronous inference stack, the system is highly resilient."

---

### [1:45 – 2:00] Outro: The Vision

**Visual:** Wide shot of the team, the hardware setup, and a clean closing slide:

```
MedVLA: Local, Adaptable Physical AI
```

**Voiceover:**
> "By bridging the semantic expertise of Claude with the agile edge execution of SmolVLA, we can deploy highly specialized, self-healing robotic intelligence anywhere in hours, not months. Thank you!"

---

## Deliverables

### Core System

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Synthetic Data Engine** | Claude-powered pipeline that takes raw, unlabelled robot trajectories and generates dense, domain-specific medical descriptions for each frame. Outputs a structured JSON dataset ready for LeRobot ingestion. |
| 2 | **Fine-tuned MedVLA Model** | SmolVLA (450M params) fine-tuned on the synthetically augmented dataset, specialized for medical laboratory vocabulary and tube-handling tasks. Trained locally on Apple Silicon via MPS. |
| 3 | **LeRobot Integration** | End-to-end training pipeline connecting the synthetic dataset to LeRobot's `lerobot-train` workflow, including dataset formatting, config files, and the training run artifacts. |
| 4 | **Inference Stack** | Async SmolVLA inference server (`smolvla_inference.py`) with the robot bridge (`robot_bridge/`) for real-time command-to-motor-token execution on the SO-101 follower arm. |

### Artifacts

| # | Artifact | Location |
|---|----------|----------|
| 5 | **Raw demonstration data** | `data/` — recorded episodes from physical teleoperation |
| 6 | **Synthetic augmentation scripts** | `scripts/` — Claude API calls, prompt templates, JSON post-processing |
| 7 | **Demo video** | 2-minute video showing the before/after: vanilla model failure → MedVLA success |
| 8 | **Slide deck** | `presentation_assets/` — hackathon presentation slides |

### Technical Stack

- **Model:** SmolVLA 450M (HuggingFace LeRobot)
- **Synthetic data:** Claude claude-sonnet-4-6 via Anthropic API
- **Training:** LeRobot on Apple M4 Mac Pro (MPS acceleration)
- **Hardware:** SO-101 leader + follower arm pair
- **Inference:** Async SmolVLA server + robot bridge
- **Training time:** < 20 minutes local

### Key Result

A vanilla SmolVLA model **fails** to ground the command `"Isolate the biohazard vacutainer"` to motor actions. After MedVLA fine-tuning on Claude-generated synthetic episodes, the same command produces **correct, smooth physical execution** — with zero cloud infrastructure required.
