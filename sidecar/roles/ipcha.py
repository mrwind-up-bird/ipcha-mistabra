# ipcha/roles/ipcha.py
"""The Ipcha Agent — antithesis (Algorithm 3)."""

from typing import Any, Dict, List

from ipcha.llm.base import LLMClient
from ipcha.roles._prompt import as_block, load_prompt


def ipcha_contradict(
    client: LLMClient,
    model: str,
    text: str,
    claims: List[Dict[str, Any]],
    proponent: Dict[str, Any],
    authority: List[str] | None = None,
) -> Dict[str, Any]:
    """Return the strongest grounded case against the artifact."""
    sections = [
        as_block("Text artifact", text),
        as_block("Extracted claims", claims),
        as_block("Proponent review", proponent.get("review", "")),
        as_block("Proponent findings", proponent.get("findings", [])),
    ]
    if authority:
        sections.append(as_block("Authority documents", "\n---\n".join(authority)))

    return client.complete_json(
        system=load_prompt("contradict"),
        user="\n\n".join(sections),
        model=model,
    )
