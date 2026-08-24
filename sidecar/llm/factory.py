# ipcha/llm/factory.py
"""Maps a model name to the provider client that can serve it."""

import os
from typing import Dict, Iterable, List, Optional, Union

from ipcha.llm.base import LLMClient, LLMError
from ipcha.llm.anthropic_client import AnthropicClient
from ipcha.llm.failover import FailoverClient
from ipcha.llm.openai_client import OpenAIClient
from ipcha.utils.models import get_model_family

#: A caller may supply one key or several per provider.
KeySpec = Dict[str, Union[str, Iterable[str]]]

# Model family (as produced by get_model_family) -> provider label.
FAMILY_TO_PROVIDER: Dict[str, str] = {
    "claude": "anthropic",
    "gpt": "openai",
    "o": "openai",
    "chatgpt": "openai",
}

#: Environment variable holding each provider's key.
PROVIDER_ENV_VAR: Dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


class UnknownModelError(LLMError):
    """Raised when a model name maps to no known provider. A client error."""


class MissingCredentialsError(LLMError):
    """Raised when no key is available for a provider. A configuration error."""


def provider_for_model(model: str) -> str:
    family = get_model_family(model)
    provider = FAMILY_TO_PROVIDER.get(family)
    if not provider:
        raise UnknownModelError(
            f"No provider registered for model family '{family}' (model '{model}'). "
            f"Known families: {sorted(FAMILY_TO_PROVIDER)}",
            provider="unknown",
            model=model,
        )
    return provider


def _as_list(value: Union[str, Iterable[str], None]) -> List[str]:
    """Accept a single key or a sequence; drop blanks."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [k.strip() for k in value if isinstance(k, str) and k.strip()]


def keys_for_provider(provider: str, keys: Optional[KeySpec] = None) -> List[str]:
    """Resolve a provider's key list.

    Precedence, first non-empty wins: caller-supplied keys, then the provider's
    environment variable. The environment is a single-key fallback for
    deployments that run on operator credentials; it is never appended to a
    caller-supplied list, so a request that brings its own keys never silently
    spends the operator's.
    """
    supplied = _as_list((keys or {}).get(provider))
    if supplied:
        return supplied
    return _as_list(os.getenv(PROVIDER_ENV_VAR[provider]))


def missing_providers(models: Iterable[str], keys: Optional[KeySpec] = None) -> List[str]:
    """Providers required by `models` for which no key is available."""
    required = {provider_for_model(m) for m in models}
    return sorted(p for p in required if not keys_for_provider(p, keys))


def build_client(model: str, keys: Optional[KeySpec] = None) -> LLMClient:
    """Return a client for `model`, backed by every key available for its provider.

    With more than one key the client fails over in order (see FailoverClient);
    it does not rotate randomly.
    """
    provider = provider_for_model(model)
    api_keys = keys_for_provider(provider, keys)

    if not api_keys:
        raise MissingCredentialsError(
            f"No credentials for provider '{provider}' "
            f"(send keys.{provider} in the body, the matching header, "
            f"or set {PROVIDER_ENV_VAR[provider]})",
            provider=provider,
            model=model,
        )

    cls = AnthropicClient if provider == "anthropic" else OpenAIClient

    if len(api_keys) == 1:
        # Sole key: let the SDK do its own retrying, there is nowhere to fail over to.
        return cls(api_key=api_keys[0])

    # With spares available, don't let the SDK burn retries on a rate-limited
    # key — hand over to the next one immediately.
    clients = [cls(api_key=k, max_retries=0) for k in api_keys]
    return FailoverClient(clients, provider=provider)
