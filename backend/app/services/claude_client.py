from __future__ import annotations

import json
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from .. import config
from ..models.schemas import ChatMessage, Interaction, Medicine, Patient


_SYSTEM_TEMPLATE = """You are Dispensr's medication-information assistant for a pharmacist working at a small Hong Kong clinic.

You answer questions about ONE medicine: the one named below. Ground every answer in the structured record and interaction list provided. If a question cannot be answered from that data, say so plainly and recommend the pharmacist consult a clinician.

Safety rules:
- Never give individualised clinical advice or change a dose.
- Flag interactions that match the patient's other medications or allergies.
- If asked something outside this medicine's scope, redirect to the pharmacist.
- Match the user's language. Reply in 繁體中文 if the user writes in Chinese; otherwise English.
- Keep answers under 6 sentences unless the user asks for more detail.

=== Active medicine record ===
{medicine_json}

=== Known interactions (from catalog) ===
{interactions_json}

=== Patient context ===
{patient_json}
"""


def _build_system_block(
    medicine: Medicine, interactions: list[Interaction], patient: Patient | None
) -> str:
    return _SYSTEM_TEMPLATE.format(
        medicine_json=json.dumps(medicine.model_dump(), indent=2, ensure_ascii=False),
        interactions_json=json.dumps(
            [i.model_dump() for i in interactions], indent=2, ensure_ascii=False
        ),
        patient_json=(
            json.dumps(patient.model_dump(), indent=2, ensure_ascii=False)
            if patient
            else "null"
        ),
    )


class ClaudeClient:
    def __init__(self) -> None:
        self._client: AsyncAnthropic | None = None

    def _client_or_raise(self) -> AsyncAnthropic:
        if self._client is None:
            if not config.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set; chat endpoint cannot run."
                )
            self._client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        return self._client

    async def stream_reply(
        self,
        *,
        medicine: Medicine,
        interactions: list[Interaction],
        patient: Patient | None,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:
        system_text = _build_system_block(medicine, interactions, patient)
        api_messages = [
            {"role": m.role, "content": m.content} for m in messages if m.content.strip()
        ]
        if not api_messages:
            return

        client = self._client_or_raise()
        async with client.messages.stream(
            model=config.ANTHROPIC_MODEL,
            max_tokens=600,
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


_client = ClaudeClient()


def get_claude_client() -> ClaudeClient:
    return _client
