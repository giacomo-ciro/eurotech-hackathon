from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from ..models.schemas import Session
from .claude_client import get_claude_client
from .data_store import get_store


log = logging.getLogger("vla.caption_engine")


_PHASE_PROMPTS = [
    "Describe what the operator is doing right now in 1 sentence. Be precise about objects, geometry, and intent.",
    "Describe the next sub-motion in 1 sentence. Mention any visible constraints (clearance, contact, orientation).",
    "Describe the moment of contact or release in 1 sentence. Include force/grip hints if relevant.",
    "Summarise the trajectory of the last few seconds in 1 sentence. Include task progress.",
    "Suggest 2 alternative phrasings of the task name that a buyer fine-tuning a model might also want as labels.",
]


class CaptionEngine:
    async def stream(self, session: Session) -> AsyncIterator[dict[str, object]]:
        """Yield rolling Claude captions for the active session.

        For the demo this is a simple loop: every ~6 seconds we ask Claude to
        generate the next caption for the trajectory phase implied by the
        rotating prompt list. When a real frame buffer is available, each
        prompt should be paired with the most recent camera frame.
        """
        store = get_store()
        client = get_claude_client()
        dataset = store.dataset(session.dataset_id)

        t = 0.0
        idx = 0
        while True:
            prompt = _PHASE_PROMPTS[idx % len(_PHASE_PROMPTS)]
            try:
                text = await client.one_shot(
                    session=session,
                    dataset=dataset,
                    episode=None,
                    user_prompt=prompt,
                )
            except RuntimeError as exc:
                yield {"t": t, "text": f"[caption engine offline] {exc}"}
                return
            except Exception as exc:  # noqa: BLE001
                log.exception("caption stream failed")
                yield {"t": t, "text": f"[error] {type(exc).__name__}: {exc}"}
                return

            yield {"t": round(t, 2), "text": text.strip()}
            await asyncio.sleep(6.0)
            t += 6.0
            idx += 1


_engine = CaptionEngine()


def get_caption_engine() -> CaptionEngine:
    return _engine
