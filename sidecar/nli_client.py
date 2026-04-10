# ipcha/nli_client.py

import os
import logging
from typing import Optional
import httpx

logger = logging.getLogger("ipcha.nli_client")
NLI_BASE_URL = os.getenv("NLI_SERVICE_URL", "http://deberta-nli:8200")
NLI_TIMEOUT_SECONDS = 5.0


def classify(premise: str, hypothesis: str, base_url: Optional[str] = None) -> dict:
    url = (base_url or NLI_BASE_URL) + "/classify"
    resp = httpx.post(url, json={"premise": premise, "hypothesis": hypothesis}, timeout=NLI_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.json()


def classify_batch(pairs: list[dict], base_url: Optional[str] = None) -> list[dict]:
    if not pairs:
        return []
    url = (base_url or NLI_BASE_URL) + "/batch"
    resp = httpx.post(url, json={"pairs": pairs}, timeout=NLI_TIMEOUT_SECONDS * 2)
    resp.raise_for_status()
    return resp.json()["results"]
