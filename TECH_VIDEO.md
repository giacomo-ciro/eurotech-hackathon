# Tech video — 2 minutes

> Draft. Owner: Alex (primary narrator) + Giacomo (hardware shots) + Davide (replay path). Target: 2 min live screen-recording / over-the-shoulder, no slides. The judges have already read `HONESTY.md`; do not re-pitch the business — show what was built.

## Demo path (the exact click sequence)

1. Terminal split with three panes already running:
   - `uv run uvicorn backend.app.main:app` on `:8000`
   - `npm run dev` on `:3000`
   - `uv run python -m robot_bridge.app.main` on `:8001`
2. Browser at `http://localhost:3000/`. Collection page — show the live robot-bridge connection in the corner.
3. Click **Start recording**. The 4-stage timeline animates (`arming → recording → captioning → saved`); the right column shows real Claude-generated captions streaming via SSE.
4. Navigate to `/datasets`. Show the marketplace grid. Pick the **Imported LeRobot — SO-101** dataset.
5. Episode dropdown — pick a real episode. Hit play.
6. **The money shot:** Rerun digital twin on the left rendering the arm in real time from the recorded joint angles. Drag in the viewer to rotate the camera. Drag the external scrubber — the twin, the joint chart, and the caption track all jump together. Hit Rerun's internal scrubber — the React state and chart follow.
7. Open `backend/app/services/rerun_export.py` for ten seconds on screen. Show the FK chain. That's where the geometry lives.

---

## Voice-over script with timestamps

### [0:00 – 0:10] Three processes
**Screen:** terminal panes.

> "Three processes. FastAPI backend on eight thousand, Next.js frontend on three thousand, and a host-side robot bridge on eight thousand and one — that one needs USB to the SO-101 so it doesn't live in Docker. They talk over WebSockets and REST."

### [0:10 – 0:25] The recording flow — and the honesty caveat
**Screen:** Collection page, click Start recording, captions appear.

> "Pressing Start recording today drives a scripted stage timeline — we wired the WebSocket fan-out, the SSE caption stream from Claude, and the UI, but the actual `lerobot-record` call happens out-of-band on Giacomo's machine. That's the mock that's on the front page of HONESTY.md. Everything else you'll see in the next ninety seconds is real recorded data."

### [0:25 – 0:45] How the data got here
**Screen:** cut to a static photo of the SO-101 leader/follower pair on the bench. Then a `tree data/` showing `meta/info.json`, `data/chunk-000/*.parquet`, `videos/observation.images.wrist_cam/chunk-000/*.mp4`.

> "Giacomo and Vittorio set up the hardware, calibrated the motors, and teleoperated forty-one episodes — eleven thousand frames at thirty FPS — using LeRobot's recorder. The output is a LeRobot v3 dataset on disk: parquet shards for joint trajectories, AV1-encoded wrist-cam video, episode metadata."

### [0:45 – 1:05] Trajectory replay — synced state across four panels
**Screen:** Dataset detail page. Play the episode. Drag the scrubber.

> "Davide built the import path. The backend reads the parquet at startup, exposes it as REST, and the trajectory replay page binds four panels to one `currentTime` value: the wrist-cam video plays the right time-slice of the underlying shard, the joint chart shows the six SO-101 channels at the cursor, the caption track highlights the active window, and the 3D digital twin renders the pose."

### [1:05 – 1:30] The Rerun migration — the technical thing worth pausing on
**Screen:** Rerun viewer in focus. Drag to rotate. Scroll to zoom. Toggle between two episodes.

> "The first version of the digital twin was a hand-built Three.js scene. It worked, but framing the camera on a kinematic chain whose rest pose is fully extended is hard, and we burned an hour on it. We rewrote the export side: the backend's `rerun_export.py` walks the forward kinematics matching the SO-101 link lengths, logs each joint as a Transform3D in a parent-child hierarchy, ships the static workspace and the end-effector path as line strips, and returns the whole episode as an in-memory `.rrd` byte stream. The frontend embeds Rerun's vanilla web viewer, fed by `GET /api/datasets/{id}/episodes/{ep}/trajectory.rrd`. Mouse rotation, zoom, framing — all native to Rerun. Around a hundred KB per trajectory."

### [1:30 – 1:45] Bidirectional time sync
**Screen:** Drag the external scrubber; Rerun cursor follows. Drag Rerun's cursor; the joint chart follows.

> "The tricky part isn't rendering — Rerun handles that. It's the time loop. The page owns a `currentTime` in React state. We push it into the viewer with `set_current_time` and listen back through `time_update`. A one-millisecond deadband breaks the echo. Both directions stay live, and the joint chart never desyncs from the 3D arm."

### [1:45 – 1:55] What Claude does in the live demo
**Screen:** Switch to the chat panel on the dataset detail page; ask "what's interesting about episode three?". Stream a response.

> "Claude is the chat assistant on every page, grounded with the active session, dataset, and episode JSON injected into a cached system prompt. Honest version: Claude is real, prompt caching is on, but the augmentation pipeline the pitch describes is not yet wired to the recorder — see HONESTY.md."

### [1:55 – 2:00] Outro
**Screen:** Static title card.

```
VLA-DataEngine
SO-101 · LeRobot · Rerun · Claude
backend FastAPI · frontend Next.js
```

---

## Architecture beat-sheet (for the speaker, not on screen)
- **`frontend/`** Next.js 14, Tailwind, App Router. Trajectory replay components live in `frontend/app/components/`: `RerunTwinViewer`, `TimeseriesChart`, `TrajectoryPlaybackControls`, `CaptionTrack`.
- **`backend/`** FastAPI on `:8000`. Routes split per domain (`datasets`, `lerobot`, `sessions`, `captions`, `chat`, `robot_ws`). Services in `backend/app/services/`: `data_store`, `lerobot_store`, `claude_client`, `caption_engine`, `robot_proxy`, `rerun_export`.
- **`robot_bridge/`** FastAPI on `:8001`, host-only process. Publishes recording-stage events on `/ws`. Mocked via `recording_stages.yaml`.
- **`scripts/`** LeRobot CLI wrappers driven by Hydra (`configs/config.yaml`). Real LeRobot calls — these produced `data/`.
- **`data/`** LeRobot v3 dataset, gitignored.

## What to definitely not do
- Don't say "fully autonomous" anywhere on camera.
- Don't open `/datasets/medical-vacutainer-v1` — that manifest is described in the README but is not present in `data/` by default; the only working dataset is the imported LeRobot one.
- Don't try to start a real recording from the web UI on camera. It is a mock today. The lerobot-record path is shown via terminal history, not via the browser.

## Pre-record checklist
- [ ] `.env` has a working `ANTHROPIC_API_KEY` (chat + captions both rely on it).
- [ ] `data/data/chunk-000/file-000.parquet` is present (re-pull from Giacomo's machine if cloning fresh).
- [ ] Browser is Chrome (AV1 video plays).
- [ ] Backend, frontend, and robot_bridge all up before recording.
- [ ] Rerun viewer is on the imported-lerobot dataset, episode 0, paused at t=0 in the opening shot.
