# ipcha/roles/_prompt.py
"""Prompt template loading, cached per process."""

import json
import os
from functools import lru_cache
from typing import Any

_PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """Read prompts/<name>.txt. Cached — templates are static per deployment."""
    path = os.path.join(_PROMPT_DIR, f"{name}.txt")
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip()


def as_block(label: str, value: Any) -> str:
    """Render a labelled section for a user message."""
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    return f"## {label}\n{value}"
