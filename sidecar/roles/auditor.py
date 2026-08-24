# ipcha/roles/auditor.py
"""The Auditor — synthesis."""

from typing import Any, Dict

from ipcha.llm.base import LLMClient
from ipcha.roles._prompt import as_block, load_prompt


def audit_and_resolve(
    client: LLMClient,
    model: str,
    text: str,
    proponent: Dict[str, Any],
    ipcha: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge thesis and antithesis into final findings."""
    return client.complete_json(
        system=load_prompt("auditor"),
        user="\n\n".join(
            [
                as_block("Text artifact", text),
                as_block("Proponent review", proponent.get("review", "")),
                as_block("Proponent findings", proponent.get("findings", [])),
                as_block("Ipcha contradiction", ipcha.get("contradiction", "")),
                as_block("Ipcha findings", ipcha.get("findings", [])),
            ]
        ),
        model=model,
    )
