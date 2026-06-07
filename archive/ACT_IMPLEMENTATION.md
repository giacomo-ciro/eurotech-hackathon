# ACT Implementation Feasibility

## Verdict

Using ACT is technically feasible under the hackathon constraints, but it changes the product claim.

The current SmolVLA story in `PITCH.md` and `DEMO_SCRIPT.md` claims direct language-to-action adaptation: Claude generates domain-rich language, SmolVLA fine-tunes on those instructions, and the robot executes a specialist command such as "isolate the biohazard vacutainer."

ACT is a better short-term engineering choice because it is much smaller, simpler, and already available in the installed LeRobot package. However, the ACT implementation in this repo's LeRobot version is not language-conditioned. It consumes images and optional robot state, then predicts action chunks. Therefore ACT should be used as a narrow visuomotor skill policy, with Claude or a deterministic ontology layer mapping domain language to a selected skill.

Recommended framing:

> MedVLA maps specialized lab language into verified low-risk robot skills, then uses compact ACT imitation policies for local execution.

Avoid claiming:

> ACT understands medical language end to end.

## What I Verified Locally

The installed LeRobot package exposes:

- `lerobot.policies.act.modeling_act.ACTPolicy`
- `lerobot.policies.act.configuration_act.ACTConfig`
- `lerobot-train --policy.type=act`
- `lerobot-record --policy.type=act`

The ACT defaults in this environment are:

- `device='mps'` on this Mac
- `chunk_size=100`
- `n_action_steps=100`
- `n_obs_steps=1`
- `vision_backbone='resnet18'`
- `use_vae=True`
- optimizer preset `AdamW(lr=1e-5, weight_decay=1e-4)`

The local ACT config explicitly requires at least one image input or an environment-state input, and `action` as output. It can optionally use `observation.state`. It does not define or process a text/task feature.

## Architecture Shift

### Current SmolVLA Architecture

```text
free-form command
  -> SmolVLA text + vision + state policy
  -> joint action chunk
  -> robot
```

Risk: likely too expensive and brittle for the available time/hardware, and hard to prove semantic grounding rather than phrase memorization.

### Proposed ACT Architecture

```text
free-form command
  -> ontology verifier / Claude command normalizer
  -> canonical skill id
  -> ACT policy for that skill
  -> safety gate
  -> robot
```

This is less general but much more demoable. The language component becomes auditable command routing, not learned language-to-action.

## Minimal Hackathon Scope

Train one ACT policy for one narrow mock-lab skill:

```text
pick blue-top mock vacutainer and place into quarantine rack
```

Use the language layer to map variants onto that skill:

- "isolate the biohazard vacutainer"
- "quarantine the blue-top tube"
- "move the suspected sample to isolation"
- "place the sodium-citrate vacutainer in the quarantine rack"

For the demo, the model does not need to learn all synonyms. The command normalizer proves domain vocabulary handling; ACT proves local physical execution.

## Data Collection Plan

Collect real SO-101 demonstrations with the existing LeRobot recording path.

Suggested first dataset:

- 20 to 40 episodes
- 10 to 20 seconds per episode
- 15 to 25 fps
- one wrist camera first, add a static top camera only if setup is stable
- fixed workspace, fixed rack positions, small object-pose variation
- mock samples only

Example command:

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --robot.cameras="{wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}}" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5A680094911 \
  --teleop.id=Leader \
  --dataset.repo_id=local/medvla-act-quarantine \
  --dataset.root=data/medvla-act-quarantine \
  --dataset.fps=25 \
  --dataset.episode_time_s=12 \
  --dataset.reset_time_s=8 \
  --dataset.num_episodes=30 \
  --dataset.single_task="Pick the blue top mock vacutainer and place it in the quarantine rack" \
  --dataset.push_to_hub=false \
  --dataset.streaming_encoding=true \
  --dataset.vcodec=auto \
  --display_data=true
```

Use `--resume=true` if appending more episodes after the initial recording.

## Training Plan

Start with a smaller ACT than the default ALOHA-sized config. The default `dim_model=512`, `chunk_size=100`, and ResNet18 are workable, but for a hackathon on Apple Silicon I would reduce the action horizon and training steps before increasing model size.

First training run:

```bash
lerobot-train \
  --dataset.repo_id=local/medvla-act-quarantine \
  --dataset.root=data/medvla-act-quarantine \
  --policy.type=act \
  --policy.device=mps \
  --policy.push_to_hub=false \
  --policy.chunk_size=50 \
  --policy.n_action_steps=25 \
  --policy.dim_model=256 \
  --policy.dim_feedforward=1024 \
  --policy.n_encoder_layers=2 \
  --policy.n_vae_encoder_layers=2 \
  --batch_size=8 \
  --steps=3000 \
  --eval_freq=0 \
  --save_freq=1000 \
  --output_dir=outputs/train/medvla-act-quarantine
```

If it underfits, increase `steps` to `8000` before increasing architecture size. If behavior is jerky, try `chunk_size=100` and `n_action_steps=50`. If inference is too open-loop, lower `n_action_steps` rather than retraining first.

## Inference Plan

LeRobot already supports executing a policy through `lerobot-record --policy.path=...`, but for the product demo the cleaner integration is a dedicated script and bridge endpoint.

Recommended repo additions:

- `scripts/run_act.py`: standalone ACT inference loop, parallel to `scripts/run_svla.py`
- `robot_bridge/app/act_runner.py`: host-side ACT runner loaded only when LeRobot is installed
- `robot_bridge/app/safety.py`: joint delta limits, workspace/stage checks, duration timeout
- `ontology/lab_objects.yaml`: allowed object and skill terms
- `scripts/normalize_command.py`: Claude or deterministic command-to-skill normalizer
- `eval/prompts_lab_quarantine.json`: lexical, distractor, and refusal tests

The bridge should expose a skill endpoint, not free-form robot control:

```text
POST /skills/quarantine-vacutainer
{
  "source_command": "isolate the biohazard vacutainer",
  "canonical_skill": "quarantine_blue_top_mock_vacutainer",
  "dry_run": false
}
```

The backend/chat layer can still accept free-form text, but the robot bridge should only receive verified canonical skills.

## Safety Gate

Add a controller between ACT output and `robot.send_action`.

Minimum checks:

- max joint delta per step
- max total execution time
- gripper command bounds
- emergency stop flag
- optional per-skill start-state check
- log every canonical command, policy checkpoint, and action summary

This is important for the pitch because the strongest regulatory/safety objection is unrestricted learned control in a lab context.

## Evaluation

Evaluate two separate claims.

Language routing:

- Does the command normalizer map domain terms to the correct canonical skill?
- Does it refuse ambiguous or forbidden commands?
- Does it preserve an audit trail?

ACT execution:

- Does the trained policy complete the skill from small object-position variations?
- Does it avoid distractor objects?
- Does it recover enough from camera/lighting variation for the demo scene?
- Does the safety gate stop out-of-range outputs?

Do not use ACT success to claim language grounding. Use ACT success to claim local skill execution.

## Demo Script Changes

Replace the SmolVLA-specific language in `DEMO_SCRIPT.md`.

Old:

> We fine-tune the 450M parameter SmolVLA model locally.

New:

> We train a compact ACT imitation policy locally for the verified quarantine skill, while Claude converts specialist lab language into an auditable canonical instruction.

Old:

> The model instantly maps the medical lexicon to physical motor tokens.

New:

> The command layer maps the medical lexicon to a verified robot skill, and the local ACT policy executes the learned motion under a safety wrapper.

Old:

> zero cloud infrastructure required.

New:

> cloud-light labeling and command normalization, with local training and local inference.

## Business Claim Changes

ACT makes the project more credible if the product is positioned as a safety-aware lab workflow adapter, not a general medical VLA.

Use:

> MedVLA helps labs convert specialist vocabulary into verified robot skills, then trains compact local imitation policies from a handful of demonstrations.

Avoid:

> MedVLA fine-tunes a generalist robot foundation model to understand medical language.

## Decision

Proceed with ACT if the goal is a reliable hackathon demo on local hardware.

Keep SmolVLA only as the future-facing roadmap:

```text
Today: Claude/ontology command normalization + ACT skill policy + safety gate.
Roadmap: replace skill-specific ACT policies with language-conditioned VLA fine-tuning once data and compute allow.
```

This preserves the original product vision while making the implementation credible within the available time.
