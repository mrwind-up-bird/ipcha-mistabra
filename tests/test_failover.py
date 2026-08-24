"""Failover across several keys of one provider — ordered, never random."""

import pytest

from ipcha.llm.base import LLMClient, LLMError
from ipcha.llm.failover import FailoverClient


class StubClient(LLMClient):
    """Fails with a given status until `succeed_after` calls have been made."""

    provider = "stub"

    def __init__(self, name, status=None):
        self.name = name
        self.status = status
        self.calls = 0

    def complete_json(self, *, system, user, model, max_tokens=16000, temperature=0.0):
        self.calls += 1
        if self.status is not None:
            raise LLMError(f"{self.name} rejected", provider="stub",
                           model=model, status_code=self.status)
        return {"served_by": self.name}


def run(clients):
    return FailoverClient(clients, provider="stub").complete_json(
        system="s", user="u", model="m"
    )


def test_first_working_key_is_used():
    a, b = StubClient("a"), StubClient("b")
    assert run([a, b])["served_by"] == "a"
    assert b.calls == 0  # no pointless second call


@pytest.mark.parametrize("status", [401, 403, 429])
def test_rejected_key_advances_to_the_next(status):
    a, b = StubClient("a", status=status), StubClient("b")
    assert run([a, b])["served_by"] == "b"
    assert a.calls == 1


def test_non_key_errors_do_not_rotate():
    # A 500 is the provider failing, not the key being bad — burning the
    # remaining keys on it would be wrong.
    a, b = StubClient("a", status=500), StubClient("b")
    with pytest.raises(LLMError) as exc:
        run([a, b])
    assert exc.value.status_code == 500
    assert b.calls == 0


def test_parse_errors_do_not_rotate():
    a, b = StubClient("a", status=None), StubClient("b")
    a.status = None
    # status_code None means "not an HTTP failure" — e.g. malformed JSON.
    broken = StubClient("broken")
    broken.complete_json = lambda **kw: (_ for _ in ()).throw(
        LLMError("bad json", provider="stub", model="m")
    )
    with pytest.raises(LLMError):
        run([broken, b])
    assert b.calls == 0


def test_all_keys_rejected_raises_the_last_error():
    clients = [StubClient(n, status=429) for n in ("a", "b", "c")]
    with pytest.raises(LLMError) as exc:
        run(clients)
    assert exc.value.status_code == 429
    assert all(c.calls == 1 for c in clients)


def test_dead_key_is_not_retried_on_later_calls():
    a, b = StubClient("a", status=401), StubClient("b")
    client = FailoverClient([a, b], provider="stub")
    for _ in range(3):
        assert client.complete_json(system="s", user="u", model="m")["served_by"] == "b"
    assert a.calls == 1  # tried once, then skipped


def test_empty_client_list_is_rejected():
    with pytest.raises(ValueError):
        FailoverClient([], provider="stub")
