# Two-Minute Video Scripts

Use these as voice-over scripts for two separate super-short videos. Each is written for roughly two minutes at a clear pace, with visuals mounted from website screen recordings, screenshots, and the captioned demo clips in `demo_clips/`.

Avoid clinical autonomy claims. The prototype is a low-risk lab robotics data and replay platform, not a validated medical device.

## Business Video

### Shot Plan

- Website home or marketplace, then the four demo GIFs from `demo_clips/`
- Dataset detail page with the trajectory replay and digital twin
- Simple overlay: `few demos -> captions -> verified dataset -> local policy`
- Hong Kong ecosystem slide: HKSTP, InnoHK, Health@InnoHK, AIR@InnoHK, Greater Bay Area
- Closing card with product name and ask

### Voice-Over

**[0:00-0:18] Problem**

Specialized labs are becoming more automated, but every new workflow still creates a data bottleneck. General robot policies do not understand the language of a specific lab, and lab teams do not want to hand-script every new motion. 

**[0:18-0:38] Target Market**

Our first market is not hospitals. It is biotech R&D labs, contract diagnostics labs, and lab automation integrators working on low-risk, high-mix laboratory tasks. In Hong Kong, that means teams around HKSTP, private lab operators, and vendors already selling automation hardware but still spending too much time adapting it to each customer workflow.

**[0:38-1:03] Solution**

VLA-DataEngine is a domain-adaptation layer for lab robotics. Operators record a handful of teleoperated demonstrations on an affordable arm. Our platform turns those trajectories into auditable LeRobot datasets with captions, task labels, joint traces, and synchronized 3D replay. That creates the foundation for near-term local skill policies such as ACT, and larger language-conditioned VLA policies when there is more data and compute.

**[1:03-1:25] Why Hong Kong**

Hong Kong is a strong launchpad because the ecosystem already combines life science, AI, robotics, and Greater Bay Area manufacturing access. HKSTP and InnoHK give us a concentrated corridor of labs, startup partners, and applied research groups where regulated-lab-safe automation matters.

**[1:25-1:50] Business Plan**

We start with design-partner pilots: one biotech R&D lab and one lab automation integrator. The first paid product is a dataset-generation platform priced per domain dataset and per pilot workflow. After that, we package reusable domain dataset SKUs and partner with integrators who can offer VLA-DataEngine as an adaptation layer for their own robot deployments.

**[1:50-2:00] Close**

Our moat is the closed loop: controlled terminology, verified robot data, replayable trajectories, and a path to safe local execution. We are looking for one HKSTP design partner and one lab automation integrator. VLA-DataEngine helps small robots learn the dialect of specialized labs.

## Technical Video

### Shot Plan

- Terminal split: robot bridge, backend, frontend
- Collection page and caption stream
- Demo clips from `demo_clips/blue_ext.gif`, `blue_pov.gif`, `red_ext.gif`, `red_pov.gif`
- Marketplace or dataset page for `imported-lerobot`
- Rerun digital twin replay, scrubber, joint chart, caption track
- Quick code flashes: backend routes, Rerun export, frontend viewer

### Voice-Over

**[0:00-0:15] Live Demo Setup**

This is the live prototype. We run three pieces: a FastAPI backend, a Next.js frontend, and a host-side robot bridge for the SO-101 arm. The bridge stays outside Docker because it needs direct USB access to the robot.

**[0:15-0:35] Product Demo**

On the collection page, an operator can start a recording flow and see robot-session state, generated captions, and chat context in one place. For the video, we also show our recorded blue and red task clips: one correct pick and one incorrect pick, from both external and first-person views, with readable subtitles burned into the GIFs.

**[0:35-0:58] Imported Robot Data**

The backend imports a real LeRobot dataset from `data/`: metadata, parquet joint trajectories, task labels, and episode timing. We use `observation.state` for replay because it is the measured robot state, not the commanded action. Each episode becomes an inspectable artifact on the platform.

**[0:58-1:25] Digital Twin**

The main technical demo is the synchronized digital twin. Instead of a hand-built Three.js viewer, the backend exports each episode as a Rerun `.rrd` file. It reconstructs the SO-101 kinematic chain from joint trajectories, logs transforms over time, and serves the result to the frontend. The user can play, pause, scrub, and inspect the arm motion like a video, while the joint chart and captions stay aligned.

**[1:25-1:48] Architecture Decisions**

The key decision was to separate data understanding from robot execution. The platform handles dataset import, captioning, replay, and auditability. For execution, the short-term path is a compact ACT imitation policy selected by a verified command normalizer, rather than claiming end-to-end language understanding. Larger SmolVLA-style policies remain the roadmap when time and compute allow.

**[1:48-2:00] Close**

What we built is the data layer a lab robot needs before safe autonomy: recorded demonstrations, semantic context, trajectory inspection, and a digital twin that makes every episode replayable and debuggable.

## Editing Notes

- Use `demo_clips/blue_ext.gif` and `demo_clips/blue_pov.gif` for the correct run.
- Use `demo_clips/red_ext.gif` and `demo_clips/red_pov.gif` for the incorrect run.
- Use website recordings for the Rerun digital twin and dataset inspection shots.
- Keep Hong Kong claims ecosystem-focused: HKSTP, InnoHK, Health@InnoHK, AIR@InnoHK, and Greater Bay Area launchpad.
- Do not say "autonomously handles patient specimens", "medical device", "clinical deployment", or "ACT understands language".
