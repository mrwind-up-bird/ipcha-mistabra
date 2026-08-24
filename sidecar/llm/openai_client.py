# ipcha/llm/openai_client.py
import logging
from typing import Any, Dict, Optional

from ipcha.llm.base import LLMClient, LLMError
from ipcha.llm.anthropic_client import _parse_json_object

logger = logging.getLogger("ipcha.llm.openai")


class OpenAIClient(LLMClient):
    provider = "openai"

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
        try:
            from openai import OpenAI  # local import — optional dependency

            opts = {} if self._max_retries is None else {"max_retries": self._max_retries}
            client = OpenAI(api_key=self._api_key, **opts)
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            raw = response.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            raise LLMError(
                str(exc),
                provider=self.provider,
                model=model,
                status_code=getattr(exc, "status_code", None),
            ) from exc

        return _parse_json_object(raw, provider=self.provider, model=model)
