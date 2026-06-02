"""AI executive summary via Anthropic Claude."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Kamu adalah pentester senior dengan pengalaman audit keamanan aplikasi web, "
    "infrastruktur, dan OSINT. Analisis temuan secara objektif, prioritaskan risiko "
    "bisnis, dan gunakan bahasa Indonesia yang jelas dan profesional."
)

USER_PROMPT_TEMPLATE = """Berikut hasil reconnaissance lengkap (JSON):

{results_json}

Berikan laporan dengan struktur:
1. **Executive Summary** — ringkasan 2–3 paragraf untuk stakeholder non-teknis
2. **Risk Rating** — skor/kategori (Critical/High/Medium/Low) dengan justifikasi singkat
3. **Attack Surface** — aset, port, subdomain, dan vektor yang teridentifikasi
4. **Rekomendasi** — langkah mitigasi terprioritas (bullet points, actionable)
"""


def execute_ai_summary(all_results: dict[str, Any]) -> str:
    """
    Call Anthropic API and return Claude text response.

    Raises:
        ValueError: if API key is missing
        anthropic.APIError: on API failures
    """
    if not settings.CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY is not configured")

    from anthropic import Anthropic

    results_json = json.dumps(all_results, indent=2, default=str)
    if len(results_json) > 100_000:
        results_json = results_json[:100_000] + "\n... (truncated)"

    user_prompt = USER_PROMPT_TEMPLATE.format(results_json=results_json)

    client = Anthropic(api_key=settings.CLAUDE_API_KEY)
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_parts: list[str] = []
    for block in message.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))

    return "\n".join(text_parts).strip()
