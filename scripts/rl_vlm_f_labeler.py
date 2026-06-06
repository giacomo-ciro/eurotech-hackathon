"""
RL-VLM-F preference labeling using Claude Haiku.

Implements the exact two-stage VLM querying process from:
  "RL-VLM-F: Reinforcement Learning from Vision Language Foundation Model Feedback"
  (arXiv 2402.03681)

Stage 1 — Analysis: send two frames + task goal → model describes and compares them.
Stage 2 — Labeling: send the analysis text back → model returns 0, 1, or -1.

Output: JSONL file where each line is:
  {"frame_a": int, "frame_b": int, "label": int, "analysis": str}

  label = 0  → frame A better achieves the goal
  label = 1  → frame B better achieves the goal
  label = -1 → no discernible difference (excluded from reward training)

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python rl_vlm_f_labeler.py \
        --video data/file-000.mp4 \
        --task "Point to the red cube." \
        --pairs 50 \
        --out data/preferences.jsonl
"""

import argparse
import base64
import json
import logging
import random
import time
from pathlib import Path

import anthropic
import cv2

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"


# ── Prompt templates (verbatim from paper, Figure in Appendix) ────────────────

ANALYSIS_TEMPLATE = """\
Consider the following two images:
Image 1:
{image1_placeholder}
Image 2:
{image2_placeholder}

1. What is shown in Image 1?
2. What is shown in Image 2?
3. The goal is to {task_description}. Is there any difference between Image 1 and Image 2 in terms of achieving the goal?\
"""

LABELING_TEMPLATE = """\
Based on the text below to the questions:

1. What is shown in Image 1?
2. What is shown in Image 2?
3. The goal is to {task_description}. Is there any difference between Image 1 and Image 2 in terms of achieving the goal?

{analysis_response}

Is the goal better achieved in Image 1 or Image 2? Reply a single line of 0 if the goal is better achieved in Image 1, or 1 if it is better achieved in Image 2.
Reply -1 if the text is unsure or there is no difference.\
"""


# ── Video utilities ────────────────────────────────────────────────────────────

def extract_frames(video_path: str) -> list[tuple[int, bytes]]:
    """Return list of (frame_index, jpeg_bytes) for every frame in the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    frames = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frames.append((idx, buf.tobytes()))
        idx += 1

    cap.release()
    log.info("Extracted %d frames from %s", len(frames), video_path)
    return frames


def to_b64(jpeg_bytes: bytes) -> str:
    return base64.standard_b64encode(jpeg_bytes).decode()


# ── Two-stage VLM querying (paper §3.1) ───────────────────────────────────────

def stage1_analysis(client: anthropic.Anthropic, task: str, img_a: bytes, img_b: bytes) -> str:
    """Analysis stage: free-form comparison of two frames."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Consider the following two images:"},
                    {"type": "text", "text": "Image 1:"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": to_b64(img_a)}},
                    {"type": "text", "text": "Image 2:"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": to_b64(img_b)}},
                    {"type": "text", "text": (
                        f"\n1. What is shown in Image 1?\n"
                        f"2. What is shown in Image 2?\n"
                        f"3. The goal is to {task}. Is there any difference between Image 1 and Image 2 in terms of achieving the goal?"
                    )},
                ],
            }
        ],
    )
    return response.content[0].text.strip()


def stage2_label(client: anthropic.Anthropic, task: str, analysis: str) -> int:
    """Labeling stage: extract preference label from the analysis text."""
    prompt = LABELING_TEMPLATE.format(task_description=task, analysis_response=analysis)
    response = client.messages.create(
        model=MODEL,
        max_tokens=16,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # parse the first integer we find: 0, 1, or -1
    for token in raw.split():
        try:
            val = int(token)
            if val in (-1, 0, 1):
                return val
        except ValueError:
            continue
    log.warning("Could not parse label from response: %r — defaulting to -1", raw)
    return -1


def label_pair(
    client: anthropic.Anthropic,
    task: str,
    idx_a: int,
    img_a: bytes,
    idx_b: int,
    img_b: bytes,
    retry_delay: float = 2.0,
) -> dict:
    """Run both stages for one image pair, with one retry on rate-limit errors."""
    for attempt in range(2):
        try:
            analysis = stage1_analysis(client, task, img_a, img_b)
            label = stage2_label(client, task, analysis)
            return {
                "frame_a": idx_a,
                "frame_b": idx_b,
                "label": label,
                "analysis": analysis,
            }
        except anthropic.RateLimitError:
            if attempt == 0:
                log.warning("Rate limited — waiting %.0fs before retry", retry_delay)
                time.sleep(retry_delay)
            else:
                raise


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RL-VLM-F preference labeling with Claude Haiku")
    p.add_argument("--video", default="data/file-000.mp4", help="Path to input video")
    p.add_argument("--task", required=True, help="Natural language goal description")
    p.add_argument("--pairs", type=int, default=50, help="Number of frame pairs to label")
    p.add_argument("--out", default="data/preferences.jsonl", help="Output JSONL file")
    p.add_argument("--stride", type=int, default=1,
                   help="Sample every Nth frame (reduces API calls for long videos)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--delay", type=float, default=0.5,
                   help="Seconds between API calls (avoids rate limits)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    frames = extract_frames(args.video)
    if args.stride > 1:
        frames = frames[::args.stride]
        log.info("After stride=%d: %d frames", args.stride, len(frames))

    if len(frames) < 2:
        raise RuntimeError("Need at least 2 frames to form pairs.")

    n_pairs = min(args.pairs, len(frames) * (len(frames) - 1) // 2)
    log.info("Labeling %d pairs with task: '%s'", n_pairs, args.task)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    labeled = skipped = 0

    with out_path.open("w") as f:
        for i in range(n_pairs):
            idx_a, idx_b = random.sample(range(len(frames)), 2)
            fi_a, img_a = frames[idx_a]
            fi_b, img_b = frames[idx_b]

            log.info("[%d/%d] frames %d vs %d …", i + 1, n_pairs, fi_a, fi_b)

            result = label_pair(client, args.task, fi_a, img_a, fi_b, img_b)

            if result["label"] == -1:
                skipped += 1
                log.info("  → -1 (no difference, skipping)")
            else:
                labeled += 1
                log.info("  → %d", result["label"])

            f.write(json.dumps(result) + "\n")
            f.flush()

            if i < n_pairs - 1:
                time.sleep(args.delay)

    log.info("Done. %d usable labels, %d skipped (-1). Written to %s", labeled, skipped, out_path)


if __name__ == "__main__":
    main()
