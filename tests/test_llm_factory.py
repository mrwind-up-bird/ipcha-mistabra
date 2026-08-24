import pytest

from ipcha.llm.base import LLMError
from ipcha.llm.failover import FailoverClient
from ipcha.llm.factory import (
    UnknownModelError,
    build_client,
    keys_for_provider,
    missing_providers,
    provider_for_model,
)


@pytest.mark.parametrize(
    "model,provider",
    [
        ("claude-opus-5", "anthropic"),
        ("claude-sonnet-5", "anthropic"),
        ("gpt-4o", "openai"),
        ("o3", "openai"),
    ],
)
def test_known_families_map_to_providers(model, provider):
    assert provider_for_model(model) == provider


def test_unknown_family_raises():
    with pytest.raises(UnknownModelError):
        provider_for_model("llama-3")


def test_missing_credentials_raise(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMError, match="No credentials"):
        build_client("claude-opus-5", keys={})


def test_supplied_key_beats_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-env")
    client = build_client("claude-opus-5", keys={"anthropic": ["from-body"]})
    assert client._api_key == "from-body"


def test_environment_used_when_no_key_supplied(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    assert build_client("gpt-4o", keys={})._api_key == "from-env"


def test_single_key_accepted_as_bare_string(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert build_client("claude-opus-5", keys={"anthropic": "solo"})._api_key == "solo"


def test_several_keys_produce_a_failover_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = build_client("gpt-4o", keys={"openai": ["k1", "k2", "k3"]})
    assert isinstance(client, FailoverClient)
    assert [c._api_key for c in client._clients] == ["k1", "k2", "k3"]


def test_environment_is_never_appended_to_supplied_keys(monkeypatch):
    # A caller bringing its own key must not silently fall through to the
    # operator's credentials once that key is exhausted.
    monkeypatch.setenv("OPENAI_API_KEY", "operator-key")
    assert keys_for_provider("openai", {"openai": ["caller-key"]}) == ["caller-key"]


def test_blank_keys_are_dropped(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert keys_for_provider("openai", {"openai": ["  ", "", "real"]}) == ["real"]


def test_missing_providers_reports_all_gaps(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    gaps = missing_providers(["claude-opus-5", "gpt-4o"], keys={})
    assert gaps == ["anthropic", "openai"]


def test_missing_providers_empty_when_all_covered(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    keys = {"anthropic": ["a"], "openai": ["b"]}
    assert missing_providers(["claude-opus-5", "gpt-4o"], keys) == []
