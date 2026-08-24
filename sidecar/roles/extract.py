# ipcha/roles/extract.py
"""ExtractClaims (Algorithm 2)."""

from typing import Any, Dict, List

from ipcha.llm.base import LLMClient
from ipcha.roles._prompt import as_block, load_prompt


def extract_claims(client: LLMClient, model: str, text: str) -> List[Dict[str, Any]]:
    """Return the atomic claims found in `text`, each with its assumptions."""
    result = client.complete_json(
        system=load_prompt("extract"),
        user=as_block("Text artifact", text),
        model=model,
    )
    claims = result.get("claims", [])
    return claims if isinstance(claims, list) else []
