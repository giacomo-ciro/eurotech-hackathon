# HONESTY.md

> Mandatory disclosure for the hackathon. This file lives at the root of your repository. Judges cross-check it against your code and your technical video.
>
> **The deal:** disclosed shortcuts are **not** penalized — that is the entire point of this file. Hidden ones are. Undisclosed pre-built code is heavily penalized, each undisclosed mock carries a small penalty, and a faked demo is heavily penalized. Telling the truth here costs you nothing.

---

## 1. Team — who did what
Judges compare this against `git shortlog -sn`, so keep it honest.

| Member | GitHub handle | Main contributions |
|---|---|---|
| Giacomo Cirò | [@giacomo-ciro](https://github.com/giacomo-ciro) | SO-101 hardware setup and maintenance: motor calibration, training/replay/deploy/record/teleoperation scripts. |
| Vittorio Rossi | [@VittorioRossi](https://github.com/VittorioRossi) | Business idea development, market and competitive research, pitch deck and pitch framing, ACT/SmolVLA feasibility writeup, dual-camera setup and SO-101 policty distributed training. |
| Alex Caldarone | [@alexcaldarone](https://github.com/alexcaldarone) | Most of the web app: Next.js frontend, the FastAPI backend — datasets/sessions/captions/chat/robot WS routes, Claude integration with prompt caching, the rolling caption engine, and the robot bridge. Docker compose plumbing. |
| Davide Beltrame | [@davide-beltrame](https://github.com/davide-beltrame) | Imported SO-101 trajectories into the web app: the LeRobot v3 store, the trajectory replay UI, and the Rerun digital-twin viewer that replaced an earlier hand-built three.js scene. Also helped with recordings, calibration, and business ideas. Prepared scripts for business video and demo. |

All 4 team members contributed equally to teleoperating the arm and produce the 103 episodes.

`copilot-swe-agent[bot]` commits in `git shortlog` are GitHub Copilot PR-fix commits, not separate contributors.

---

## 2. What is fully working
Features that run end-to-end on the live app, with real data and real logic.

- **LeRobot v3 dataset import.** The backend reads `data/meta/info.json` + `data/meta/episodes/chunk-000/*.parquet` + `data/data/chunk-000/*.parquet` and serves it through `/api/lerobot/{info,episodes,episodes/{idx}}` (`backend/app/services/lerobot_store.py`, `routes/lerobot.py`). 41 real episodes / 11,224 frames @ 30 fps captured on the SO-101 follower during the hackathon.
- **Real wrist-cam video playback.** `GET /api/lerobot/episodes/{idx}/video` serves the underlying AV1-encoded `.mp4` shard; the frontend plays the correct time-slice for the selected episode (`VideoReplay`-style component in `datasets/[id]/page.tsx`). AV1 plays in Chrome / Edge / Firefox; Safari renders a blank video element (known browser limitation, not a mock).
- **Trajectory replay with synchronized scrubber + chart + captions.** External scrubber (`TrajectoryPlaybackControls`) drives a shared `currentTime`; `TimeseriesChart` plots the 6 SO-101 joint channels at the cursor; `CaptionTrack` highlights the active caption window. Real joint-angle data from the recorded episodes.
- **Rerun digital-twin viewer.** `GET /api/datasets/{id}/episodes/{ep_id}/rrd` (or `.../trajectory.rrd`) builds an in-memory `.rrd` byte stream from the recorded joint angles via forward kinematics matching the SO-101 link lengths and serves it as `application/vnd.rerun.rrd`. The frontend embeds `@rerun-io/web-viewer` (vanilla, dynamically imported) and bidirectionally syncs the scrubber's `currentTime` with the viewer's `"trajectory"` timeline through `set_current_time` and `time_update` events. Mouse rotation, zoom, and framing come from Rerun. Smoke-tested: 108940-byte RRF2 stream, valid header.
- **Claude chat grounded in active context.** `POST /api/chat` (SSE) streams responses from the Anthropic SDK (`anthropic.AsyncAnthropic`) with a system prompt that embeds the active session / dataset / episode JSON. Prompt caching is on. Requires a real `ANTHROPIC_API_KEY` in `.env`.
- **Collection page UI flow.** The 4-stage recording timeline (`arming → recording → captioning → saved`) animates through real WebSocket events fanned out from `robot_bridge` via the backend proxy (`/ws/robot`). The state machine and UI updates are real; the underlying motion is a mock (see §3).
- **LeRobot scripts wired to real hardware.** `scripts/record.py`, `scripts/teleoperate.py`, `scripts/train.py`, `scripts/replay.py`, `scripts/deploy.py` invoke real `lerobot.scripts.*` entry points via Hydra config (`configs/config.yaml`). These are what produced the dataset in `data/`. They are *not* invoked from the web UI in the demo path — they were used during data collection.

---

## 3. What is mocked, stubbed, or hardcoded
Every shortcut. **Anything listed here = free.**

| What is faked | Where (file:line or folder) | Why we mocked it | What the real version would do |
|---|---|---|---|
| The "Start recording" button on the Collection page does not move the arm. It runs a scripted timer through `arming → recording → captioning → saved`. | `robot_bridge/app/lerobot_adapter.py` (`run_recording` — docstring explicitly flags it as a mock; durations come from `robot_bridge/motions/recording_stages.yaml`) | The SO-101 was on a separate machine during integration; we wanted the web demo to play end-to-end without USB. | Call `lerobot.scripts.lerobot_record.record(...)` from `scripts/record.py` (which *does* drive the real arm) and stream stage events out as real frames are captured. |
| Caption stream is not grounded in camera frames. The "rolling caption" loop sends one of 5 hardcoded prompts to Claude every 6 s, with no image input — only the JSON of the active session/dataset/episode. | `backend/app/services/caption_engine.py` (`_PHASE_PROMPTS` + `CaptionEngine.stream`) | Live camera frame-grabbing into Claude during the recording stage was out of scope for the hackathon. | Buffer the latest wrist-cam frame, pass it as an `image` content block to Claude alongside the prompt, and rotate prompts by detected motion phase. |
| Dataset price (`price_usd`) and `augmentation_status` shown on `/datasets` come from the dataset's `manifest.json` and are static display values. There is no payment integration and no augmentation pipeline behind the "augmented" / "fine-tuned" badges. | `backend/app/services/data_store.py` + `data/datasets/*/manifest.json` (none of the seeded marketplace manifests besides the imported LeRobot dataset are present in this repo by default) | The marketplace was framing-only — the focus this weekend was the import + replay path on a single real dataset. | A real Stripe checkout flow gated by license terms; an actual Claude-driven augmentation pipeline producing the alternate dataset variants. |
| `active_session.json` is edited by hand to switch between datasets. There is no auth, no session creation UI, no multi-user routing. | `data/active_session.json` (referenced by `data_store.DataStore.active_session()`) | Single-machine hackathon demo. | Login + per-user session state in a real DB. |
| The "augmentation engine" described in `PITCH.md` (Claude → 10x synthetic dataset → SmolVLA fine-tune) is **not** implemented end-to-end in this repo. `scripts/train.py` can train ACT or SmolVLA on a recorded dataset, but the synthetic-augmentation step that the pitch promises (Claude generating dense per-frame medical/lab language variants) is not in code. | Pitch claim: `PITCH.md`, `DEMO_SCRIPT.md`. Feasibility-revision documented in `ACT_IMPLEMENTATION.md`. Augmentation pipeline files: not present. | We scoped down to ACT on a single skill mid-hackathon (see `ACT_IMPLEMENTATION.md`); the augmentation loop is the roadmap claim, not the demo claim. | A Claude API call per episode that produces a structured set of instruction variants from a controlled ontology, post-processed into `metadata.json` for each generated episode, then ingested by `lerobot-train`. |
| `auto_caption_stream` UI element shows synthetic Claude captions during the mock recording — those captions are not paired with the real joint trajectory frames that the "saved" stage pretends to write. | Same chain: `robot_bridge` mock + `caption_engine.py` | See above. | Stream captions tied to actual frame timestamps from the live recording. |

---

## 4. External APIs, services & data sources

| Service / API / dataset | Used for | Real call or mocked? | Auth (sandbox / test key / none) |
|---|---|---|---|
| Anthropic Claude API (`anthropic` Python SDK) | `/api/chat` SSE chat grounded on context, and the rolling caption engine. Model: `claude-sonnet-4-6` (via `config.CLAUDE_MODEL`). Uses prompt caching. | Real — fails fast with a 5xx if the key is missing. | Personal `ANTHROPIC_API_KEY` in `.env` (not committed). |
| Hugging Face LeRobot (`lerobot` Python package) | Recording (`lerobot.scripts.lerobot_record.record`), training (`lerobot.scripts.lerobot_train.train`), policy loading (`lerobot.policies.factory.make_pre_post_processors`). Also the LeRobot v3 dataset format read by `lerobot_store.py`. | Real library calls. No HF Hub uploads during the demo (`dataset.push_to_hub: false` in `configs/config.yaml`). | None for local use; HF token only needed if pushing to Hub. |
| Rerun (`rerun-sdk` Python + `@rerun-io/web-viewer` JS, both 0.26.x) | Backend logs joint Transform3D + workspace geometry into an in-memory `.rrd` byte stream; frontend embeds the web viewer to render it with native 3D controls. | Real, fully local — no rerun.io cloud call. | None. |
| HuggingFace Hub (`giacomo-ciro/cube-color-pointing` — referenced in `configs/config.yaml` as default `dataset.repo_id`) | Default upload destination for the LeRobot recorder when `push_to_hub: true`. | Mocked off (`push_to_hub: false`). No data was pushed during the hackathon. | HF token required only if turned on. |
| SO-101 leader + follower arms (real hardware) | Teleoperation, recording, replay. The 103 episodes in `data/` came from this. | Real, used during data collection. Not present in the web demo runtime — see §3 mock. | USB serial ports configured per-operator in `configs/user/*.yaml`. |
| Docker Hub / npm registry | Container base images + JS deps. | Real (build-time only). | None. |

---

## 5. Pre-existing code
Anything written **before** the hackathon kickoff that we brought into this project.

| Item | Source (URL or description) | Roughly how much | License |
|---|---|---|---|
| EuroTech LeRobot tutorial: `README.robotum.md`, the hardware-setup chapters | Upstream tutorial provided by the EuroTech × HK Talent Engage Hackathon organisers | 1 file (~24 KB), reference only — we did not modify the tutorial text itself. | As provided by the organisers. |
| `dump/so101.urdf` | Public SO-101 URDF from the SO-100 / LeRobot community. | One URDF file. | As published upstream. |
| `frontend/` Next.js 14 + Tailwind app shell | Started from `npx create-next-app@14` boilerplate (App Router, TypeScript, Tailwind). All page logic, components, hooks, and API client code under `frontend/app/` were written during the hackathon. | Boilerplate scaffolding only. | MIT (Next.js boilerplate). |
| Framework dependencies (libraries we *use* but did not author): Next.js, React, FastAPI, Uvicorn, Anthropic SDK, LeRobot, Hugging Face datasets / transformers stack, Rerun (Python SDK + Web Viewer), Tailwind, Three.js (now retired from the trajectory replay path). | Public npm / PyPI. | Listed in `frontend/package.json` and `backend/pyproject.toml` / `pyproject.toml`. | Respective OSS licenses. |

Everything not listed above — every file under `backend/app/`, `frontend/app/`, `robot_bridge/app/`, the docs in the repo root, the recorded dataset, the docker-compose plumbing and the robot-related code in `src/` — was written during the hackathon window (first commit `2026-06-06 11:17:31 +0200` initialized the repo).

---

## 6. Known limitations & next steps

- **The "synthetic data engine" claim is a roadmap, not a demo.** The pitch (`PITCH.md`) describes a Claude→synthetic-augmentation→SmolVLA loop; what we shipped is the ingestion + replay + chat infrastructure plus a single real recorded dataset on the SO-101. Closing this gap is the largest next step. `ACT_IMPLEMENTATION.md` lays out the more feasible ACT-on-one-skill path we'd take next.
- **Recording is not wired to the web UI.** Pressing "Start recording" in the browser animates a stage timeline but does not call `lerobot-record`. Wiring `robot_bridge/app/lerobot_adapter.py` to the real `lerobot.scripts.lerobot_record.record` function is mechanical but unfinished.
- **No vision in the caption loop.** Claude captions are text-only and rotate through a fixed prompt list. Captions tied to actual wrist-cam frames would make the labels honest and the resulting "augmented dataset" actually domain-grounded.
- **No safety gate.** Per `ACT_IMPLEMENTATION.md`, a real product needs joint-delta limits, workspace bounds, an emergency stop, and an action whitelist between any policy output and `robot.send_action`. None of that is implemented yet — it's why we mocked the recording path rather than wire half a safety story.
- **Marketplace UX is single-dataset.** The `/datasets` grid is built for many datasets but only the imported LeRobot one is real. The price / status / search filters work against static manifest values; there is no checkout flow.
- **AV1 wrist-cam video does not play in Safari.** A Chrome/Firefox/Edge limitation we accepted; the rest of the trajectory page still works in Safari because the Rerun viewer renders independently of the video element.
- **The dataset in `data/` is gitignored.** Reviewers cloning the repo won't have the 103 episodes.
