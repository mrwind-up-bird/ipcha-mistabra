# ipcha/llm/base.py
"""Provider-agnostic LLM interface.

All protocol roles talk to this ABC, never to a vendor SDK directly, so the
whole trialectic can be exercised in tests with a mock client and no network.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMError(RuntimeError):
    """Raised when a provider call fails or returns unusable output.

    `status_code` carries the provider's HTTP status when there was one, so
    callers can tell a key problem (401/403) or a rate limit (429) apart from a
    genuine failure. It is None for parse errors and transport failures.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        model: str,
        status_code: int | None = None,
    ):
        self.provider = provider
        self.model = model
        self.status_code = status_code
        super().__init__(message)


class LLMClient(ABC):
    """A single-turn, JSON-returning completion interface."""

    #: Vendor label used in errors and result metadata.
    provider: str = "unknown"

    @abstractmethod
    def complete_json(
        self,
        *,
        system: str,
        user: str,
        model: str,
        max_tokens: int = 16000,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Run one completion and return the parsed JSON object.

        Implementations must raise LLMError rather than a vendor-specific
        exception, and must not return a non-dict payload.

        `temperature` is honoured only where the provider still accepts it.
        Current Claude models removed sampling parameters outright and reject
        them with a 400, so the Anthropic client ignores this argument.
        """
