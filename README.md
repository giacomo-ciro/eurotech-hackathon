# Synthetic VLA Data Engine

![image](/presentation_assets/image.png)

A synthetic-data engine that turns a handful of raw robot trajectories into dense, deployment-ready LeRobot datasets — plus a marketplace for selling them.

> TL;DR: Starting from a seed dataset, a VLM autonomously labels the episodes and trajectories, which are then leveraged to improve the robot. This loop is iterated for continuous improvement.



See `PITCH.md` and `DEMO_SCRIPT.md` for the business framing, and `HONESTY.md` for a full disclosure of what works and what is just a demo.

## Demo clips

<table>
  <tr>
    <th>Correct blue pick</th>
    <th>Incorrect red pick</th>
  </tr>
  <tr>
    <td align="center">
      <img src="demo_clips/blue_ext.gif" alt="External view of the correct blue cube pick" width="260"><br>
      <sub>External view</sub>
    </td>
    <td align="center">
      <img src="demo_clips/red_ext.gif" alt="External view of the incorrect red cube pick" width="260"><br>
      <sub>External view</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="demo_clips/blue_pov.gif" alt="First-person view of the correct blue cube pick" width="260"><br>
      <sub>First-person view</sub>
    </td>
    <td align="center">
      <img src="demo_clips/red_pov.gif" alt="First-person view of the incorrect red run" width="260"><br>
      <sub>First-person view</sub>
    </td>
  </tr>
</table>

<p align="center">
  <sub>Timed caption tracks:
    <a href="demo_clips/blue_ext.vtt">blue_ext.vtt</a> ·
    <a href="demo_clips/blue_pov.vtt">blue_pov.vtt</a> ·
    <a href="demo_clips/red_ext.vtt">red_ext.vtt</a> ·
    <a href="demo_clips/red_pov.vtt">red_pov.vtt</a>
  </sub>
</p>

## Run

Prereqs: Docker Desktop, [`uv`](https://docs.astral.sh/uv/), an Anthropic API key.

```bash
cp .env.example .env       # paste ANTHROPIC_API_KEY into .env
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

## Architecture

Three processes:

- **`frontend`** — Next.js 14 + Tailwind on `:3000`. Three pages:
  - **`/`** Collection. Left = robot live stream (rerun iframe) + 4-stage recording timeline + Start/Stop. Right = active-session card + auto-caption stream from Claude + free-form chat scoped to the session.
  - **`/datasets`** Marketplace. Grid of dataset cards with domain / status / search filters.
  - **`/datasets/[id]`** Detail. Episode list + video replay + scrubber-synced joint timeseries chart + frame-caption track.
- **`backend`** — FastAPI on `:8000`. Loads `data/datasets/*/manifest.json` and episode metadata at startup; serves REST for datasets/sessions/episodes, SSE `/api/chat` (Claude with prompt caching, grounded on session / dataset / episode context), SSE `/api/sessions/{id}/captions/stream` (rolling Claude captions driven by `services/caption_engine.py`), WS `/ws/robot` fan-out.
- **`robot_bridge`** — FastAPI on `:8001`, **host process** (needs USB → SO-101). WS `/ws` publishes recording stage events; `POST /record` triggers a scripted mock motion (`motions/recording_stages.yaml`: `arming → recording → captioning → saved → idle`) so the Collection page animates end-to-end without the arm plugged in.

Frontend + backend are containerized. `robot_bridge` runs on the host because Docker Desktop on macOS can't reach USB cleanly. The backend reaches the host via `host.docker.internal:8001`.