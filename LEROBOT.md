# Dispensr Platform

AI pharmacy dispensing workcell: live SO-101 video stream on the left, patient + prescription + Claude-grounded chat on the right.

## Architecture

Three processes:

- **`frontend`** — Next.js 14 + Tailwind on `:3000`. Split-pane operator UI: rerun viewer iframe, 5-step dispense timeline, patient card, prescription card, chat panel (SSE-streamed Claude, scoped to the active drug).
- **`backend`** — FastAPI on `:8000`. Loads `data/drug_data_1.csv` + `common_drugs.csv` as the medicine catalog and `common_interactions.csv` as the interaction index (lazy fallback to `interactions_text.csv`). REST for patients/medicines/prescriptions, SSE `/api/chat` (Claude with prompt caching), WS `/ws/robot` fan-out.
- **`robot_bridge`** — FastAPI on `:8001`, **host process** (USB → SO-101). Exposes `WS /ws` for state events and `POST /dispense` for motion triggers. Ships a scripted mock motion (`motions/waypoints.yaml`) so the UI animates end-to-end without the arm plugged in.

Frontend and backend are containerised; `robot_bridge` runs on the host because Docker Desktop on macOS can't reach USB cleanly. The backend reaches the host via `host.docker.internal:8001`.

Demo state lives in `data/`:
- `patients.json`, `prescriptions.json` — seeded HK clinic records.
- `active.json` — pointer to the prescription currently on the mat. Edit it live during the demo to swap scenarios; the UI picks up the change within ~3 s.

## Run

Prereqs: Docker Desktop, [`uv`](https://docs.astral.sh/uv/), an Anthropic API key.

```bash
cp .env.example .env       # then paste ANTHROPIC_API_KEY into .env
uv pip install -e robot_bridge
```

Terminal 1 — host-side robot bridge:
```bash
uv run python -m robot_bridge.app.main
```

Terminal 2 — backend + frontend:
```bash
docker compose up --build
```

Open <http://localhost:3000>.

To switch scenarios live, edit `data/active.json` and change `prescription_id` to `RX-1002`, `RX-1003`, or `RX-1004`.

---

# LeRobot setup (SO-101 hardware)

## Detect port
```
lerobot-find-port
```

# Detect Cameras
To get the available cameras and their indices:
```
lerobot-find-cameras opencv
```

# Follower
On `gciro-macbook`:
```
/dev/tty.usbmodem5A680099311
```
Then run:
```
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem5A680099311 \
    --robot.id=Follower
```

# Leader
On `gciro-macbook`:
```
/dev/tty.usbmodem5A680094911
```
Then run:
```
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem5A680094911 \
    --teleop.id=Leader
```

# Teleoperate
Use leader to teleoperate follower via (on `gciro-macbook`):
```
lerobot-teleoperate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5A680094911 \
  --teleop.id=Leader \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --robot.cameras="{wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}}" \
  --display_data=True

# laptop_cam: {type: opencv, index_or_path: 1, width: 1920, height: 1080, fps: 15}
```

# Record
Record an episode (only wrist-camera for faster encoding):
```
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --robot.cameras="{wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}}" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5A680094911 \
  --teleop.id=Leader \
  --dataset.repo_id=giacomo-ciro/test-dataset \
  --dataset.root=data \
  --dataset.num_episodes=5 \
  --dataset.single_task="Teseting the recording logic" \
  --dataset.push_to_hub=false \
  --display_data=true
  --resume=true # to append instead of starting from scratch
```

# Replay
Replay an episode:
```
lerobot-replay \
  --dataset.repo_id=giacomo-ciro/test-dataset \
  --dataset.root=data \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --dataset.episode=0
```