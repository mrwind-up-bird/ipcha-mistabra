# ipcha/redact.py
"""Strip provider credentials out of text before it leaves the process.

Provider SDKs echo the offending key into their error messages — OpenAI, for
example, answers a bad key with "Incorrect API key provided: sk-abc***xyz".
That text must never reach an HTTP response, a log line, or the job store.
"""

import re
from typing import Any, Dict

# Matches live keys (sk-…, sk-ant-…) and the partially-masked forms providers
# put in their own error strings (sk-dummy***********-key).
_SECRET_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_*\-]{4,}", re.IGNORECASE)

REDACTED = "[redacted]"


def redact_secrets(text: str) -> str:
    """Replace anything that looks like an API key with a placeholder."""
    if not text:
        return text
    return _SECRET_PATTERN.sub(REDACTED, text)


def redact_mapping(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact every string value in a flat mapping."""
    return {
        k: redact_secrets(v) if isinstance(v, str) else v
        for k, v in data.items()
    }
