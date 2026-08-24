# ipcha/llm/failover.py
"""Try a provider's keys in order until one works.

Deliberately ordered, not random. Randomised rotation would defeat provider-side
prompt caching (which is key-scoped, and the protocol replays the same four
system prompts on every run), scatter billing across accounts arbitrarily, and
make a run irreproducible — which matters for a verification protocol whose
output is meant to be auditable. Rotation buys no security either: every key
arrives in the same request over the same channel.
"""

import logging
from typing import Any, Dict, List

from ipcha.llm.base import LLMClient, LLMError

logger = logging.getLogger("ipcha.llm.failover")

#: Provider statuses that mean "this key is unusable, try the next one".
ROTATE_ON_STATUS = frozenset({401, 403, 429})


class FailoverClient(LLMClient):
    """Wraps one client per key and advances only when a key is rejected."""

    def __init__(self, clients: List[LLMClient], provider: str):
        if not clients:
            raise ValueError("FailoverClient needs at least one client")
        self._clients = clients
        self.provider = provider
        # Keys already rejected in this run; skipped on later calls so a dead
        # key is not retried once per role.
        self._exhausted: set[int] = set()

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        model: str,
        max_tokens: int = 16000,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        last_error: LLMError | None = None

        for index, client in enumerate(self._clients):
            if index in self._exhausted:
                continue
            try:
                return client.complete_json(
                    system=system,
                    user=user,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except LLMError as exc:
                if exc.status_code not in ROTATE_ON_STATUS:
                    raise  # a real failure, not a key problem
                self._exhausted.add(index)
                last_error = exc
                logger.warning(
                    "Key %d/%d for provider '%s' rejected (status %s); trying next",
                    index + 1,
                    len(self._clients),
                    self.provider,
                    exc.status_code,
                )

        raise last_error or LLMError(
            f"All {len(self._clients)} key(s) for provider '{self.provider}' were rejected",
            provider=self.provider,
            model=model,
        )
