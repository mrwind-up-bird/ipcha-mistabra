from ipcha.redact import REDACTED, redact_mapping, redact_secrets


def test_openai_style_error_is_redacted():
    text = "Incorrect API key provided: sk-proj-AbC123xyz. Find your key at ..."
    out = redact_secrets(text)
    assert "sk-proj-AbC123xyz" not in out
    assert REDACTED in out


def test_partially_masked_key_is_still_redacted():
    # Providers mask the middle themselves; prefix and suffix still leak.
    assert "sk-dummy" not in redact_secrets("provided: sk-dummy***********-key.")


def test_anthropic_key_is_redacted():
    assert "sk-ant-api03" not in redact_secrets("invalid x-api-key sk-ant-api03-AbCdEf")


def test_innocent_text_is_untouched():
    text = "Connection timed out after 5s"
    assert redact_secrets(text) == text


def test_empty_input_survives():
    assert redact_secrets("") == ""


def test_mapping_redacts_strings_and_leaves_other_types():
    out = redact_mapping({"error": "key sk-abc123def", "status": 401, "ok": False})
    assert REDACTED in out["error"]
    assert out["status"] == 401 and out["ok"] is False
