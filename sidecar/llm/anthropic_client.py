# ipcha/llm/anthropic_client.py
import json
import logging
from typing import Any, Dict, Optional

from ipcha.llm.base import LLMClient, LLMError

logger = logging.getLogger("ipcha.llm.anthropic")

# Nudges the model into emitting a bare object; Anthropic has no JSON mode.
_JSON_SUFFIX = "\n\nRespond with a single JSON object and nothing else."


class AnthropicClient(LLMClient):
    provider = "anthropic"

    def __init__(self, api_key: Optional[str] = None, max_retries: Optional[int] = None) -> None:
        self._api_key = api_key
        # None keeps the SDK default. Set to 0 when this client is one of
        # several keys, so a rate-limited key hands over immediately instead of
        # burning the SDK's internal retries first.
        self._max_retries = max_retries

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        model: str,
        max_tokens: int = 16000,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        # `temperature` is deliberately not forwarded: current Claude models
        # removed sampling parameters, and anthropic>=1.0 drops the argument
        # from messages.create() entirely.
        del temperature
        try:
            from anthropic import Anthropic  # local import — optional dependency

            opts = {} if self._max_retries is None else {"max_retries": self._max_retries}
            client = Anthropic(api_key=self._api_key, **opts)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system + _JSON_SUFFIX,
                messages=[{"role": "user", "content": user}],
            )
            raw = "".join(block.text for block in response.content if block.type == "text")
        except Exception as exc:  # noqa: BLE001
            raise LLMError(
                str(exc),
                provider=self.provider,
                model=model,
                status_code=getattr(exc, "status_code", None),
            ) from exc

        return _parse_json_object(raw, provider=self.provider, model=model)


def _parse_json_object(raw: str, *, provider: str, model: str) -> Dict[str, Any]:
    """Parse a JSON object, tolerating fenced code blocks and surrounding prose."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text[3:]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise LLMError(
                f"Model returned no JSON object: {raw[:200]!r}",
                provider=provider,
                model=model,
            ) from None
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(
                f"Model returned malformed JSON: {raw[:200]!r}",
                provider=provider,
                model=model,
            ) from exc

    if not isinstance(data, dict):
        raise LLMError(
            f"Model returned {type(data).__name__}, expected object",
            provider=provider,
            model=model,
        )
    return data
