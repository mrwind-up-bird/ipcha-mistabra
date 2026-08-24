# ipcha/roles/proponent.py
"""The Proponent role — thesis."""

from typing import Any, Dict, List

from ipcha.llm.base import LLMClient
from ipcha.roles._prompt import as_block, load_prompt


def proponent_review(
    client: LLMClient,
    model: str,
    text: str,
    claims: List[Dict[str, Any]],
    authority: List[str] | None = None,
) -> Dict[str, Any]:
    """Return the Proponent's assessment of the artifact."""
    sections = [as_block("Text artifact", text), as_block("Extracted claims", claims)]
    if authority:
        sections.append(as_block("Authority documents", "\n---\n".join(authority)))

    return client.complete_json(
        system=load_prompt("proponent"),
        user="\n\n".join(sections),
        model=model,
    )
