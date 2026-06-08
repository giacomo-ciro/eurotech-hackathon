from __future__ import annotations

import json
from typing import AsyncIterator, Optional

from anthropic import AsyncAnthropic

from .. import config
from ..models.schemas import ChatMessage, Dataset, Episode, Session


_SYSTEM_TEMPLATE = """You are the assistant for VLA-DataEngine, a synthetic-data engine that turns raw robot trajectories into dense, deployment-ready LeRobot datasets.

Your role on this page: act as an automated data engineer for the operator. Help them think about the task, the trajectory they just recorded, and how the dataset will adapt downstream models (e.g. SmolVLA). Be specific and technical when relevant; concise when not.

Style:
- Plain language unless the operator asks for a structured output.
- 4 sentences max unless they ask for more.
- Never invent data. If a fact isn't in the context blocks below, say so and ask what they want.

Context (only what is provided is in scope):
=== Active session ===
{session_json}

=== Active dataset ===
{dataset_json}

=== Active episode ===
{episode_json}
"""


def _block(obj) -> str:
    if obj is None:
        return "null"
    return json.dumps(obj.model_dump(), indent=2, ensure_ascii=False, default=list)


def _build_system_block(
    session: Optional[Session],
    dataset: Optional[Dataset],
    episode: Optional[Episode],
) -> str:
    return _SYSTEM_TEMPLATE.format(
        session_json=_block(session),
        dataset_json=_block(dataset),
        episode_json=_block(episode),
    )


class ClaudeClient:
    def __init__(self) -> None:
        self._client: AsyncAnthropic | None = None

    def _client_or_raise(self) -> AsyncAnthropic:
        if self._client is None:
            if not config.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set; Claude endpoints cannot run."
                )
            self._client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        return self._client

    async def stream_chat(
        self,
        *,
        session: Optional[Session],
        dataset: Optional[Dataset],
        episode: Optional[Episode],
        messages: list[ChatMessage],
        max_tokens: int = 600,
    ) -> AsyncIterator[str]:
        system_text = _build_system_block(session, dataset, episode)
        api_messages = [
            {"role": m.role, "content": m.content} for m in messages if m.content.strip()
        ]
        if not api_messages:
            return

        client = self._client_or_raise()
        async with client.messages.stream(
            model=config.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_text,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=api_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def one_shot(
        self,
        *,
        session: Optional[Session],
        dataset: Optional[Dataset],
        episode: Optional[Episode],
        user_prompt: str,
        max_tokens: int = 220,
    ) -> str:
        chunks: list[str] = []
        async for chunk in self.stream_chat(
            session=session,
            dataset=dataset,
            episode=episode,
            messages=[ChatMessage(role="user", content=user_prompt)],
            max_tokens=max_tokens,
        ):
            chunks.append(chunk)
        return "".join(chunks)


_client = ClaudeClient()


def get_claude_client() -> ClaudeClient:
    return _client
