# ipcha/agents/implementations.py

import json
import logging
import os
from typing import List, Optional

from ipcha.agents.base import VerificationAgent
from ipcha.models import Claim, VerificationResult
import ipcha.nli_client as nli_client

logger = logging.getLogger("ipcha.agents")


class SDRLAgent(VerificationAgent):
    """
    Verifies factual (VERIFIABLE) claims against authority documents using NLI.

    For each authority chunk, calls the NLI service to score entailment and
    contradiction against the claim. The highest scores across all chunks
    determine the final verdict:
      - contradiction > 0.7  → rejected with contradiction confidence
      - entailment   > 0.7  → accepted with entailment confidence
      - otherwise           → conservative rejection with max of both scores
    """

    def __init__(self, authority_chunks: Optional[List[str]] = None) -> None:
        self._authority_chunks: List[str] = authority_chunks or []

    def verify(self, claim: Claim) -> VerificationResult:
        if not self._authority_chunks:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                reason="No authority documents available for verification.",
                agent_name=self.__class__.__name__,
            )

        max_entailment = 0.0
        max_contradiction = 0.0

        for chunk in self._authority_chunks:
            try:
                result = nli_client.classify(premise=chunk, hypothesis=claim.text)
                entailment = float(result.get("entailment", 0.0))
                contradiction = float(result.get("contradiction", 0.0))
                if entailment > max_entailment:
                    max_entailment = entailment
                if contradiction > max_contradiction:
                    max_contradiction = contradiction
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "NLI classification failed for chunk (claim_id=%s): %s",
                    claim.id,
                    exc,
                )
                continue

        if max_contradiction > 0.7:
            return VerificationResult(
                is_verified=False,
                confidence=max_contradiction,
                reason=(
                    f"Claim contradicted by authority documents "
                    f"(contradiction score: {max_contradiction:.3f})."
                ),
                agent_name=self.__class__.__name__,
            )

        if max_entailment > 0.7:
            return VerificationResult(
                is_verified=True,
                confidence=max_entailment,
                reason=(
                    f"Claim supported by authority documents "
                    f"(entailment score: {max_entailment:.3f})."
                ),
                agent_name=self.__class__.__name__,
            )

        # Neither threshold met — conservative rejection
        confidence = max(max_entailment, max_contradiction)
        return VerificationResult(
            is_verified=False,
            confidence=confidence,
            reason=(
                "Insufficient evidence in authority documents to verify claim "
                f"(max entailment: {max_entailment:.3f}, "
                f"max contradiction: {max_contradiction:.3f})."
            ),
            agent_name=self.__class__.__name__,
        )


class PromptBasedAgent(VerificationAgent):
    """
    Analyzes interpretive (INTERPRETIVE) claims via an LLM.

    Sends the claim to gpt-4o-mini and asks it to assess whether the claim
    is supported, contested, or unfounded. Returns a structured verdict.
    """

    _SYSTEM_PROMPT = (
        "You are an objective claim verification assistant. "
        "Analyze the given interpretive claim and return a JSON object with exactly "
        "three fields:\n"
        '  "assessment": one of "supported", "contested", or "unfounded"\n'
        '  "reasoning": a brief explanation (one or two sentences)\n'
        '  "confidence": a float between 0.0 and 1.0\n'
        "Be concise and factual. Do not include any text outside the JSON object."
    )

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")

    def verify(self, claim: Claim) -> VerificationResult:
        try:
            from openai import OpenAI  # local import — optional dependency

            client = OpenAI(api_key=self._api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=200,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": claim.text},
                ],
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            assessment: str = data.get("assessment", "unfounded").lower()
            reasoning: str = data.get("reasoning", "No reasoning provided.")
            confidence: float = float(data.get("confidence", 0.0))

            is_verified = assessment == "supported"

            return VerificationResult(
                is_verified=is_verified,
                confidence=confidence,
                reason=reasoning,
                agent_name=self.__class__.__name__,
            )

        except Exception as exc:  # noqa: BLE001
            logger.warning("PromptBasedAgent LLM call failed (claim_id=%s): %s", claim.id, exc)
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                reason=f"LLM verification failed: {exc}",
                agent_name=self.__class__.__name__,
            )


class DefaultAgent(VerificationAgent):
    """
    Conservative fallback agent for claims that cannot be classified.

    This is not a stub — deliberate fail-closed design. Unclassifiable claims
    must not pass through verification silently; conservative rejection protects
    against ambiguous or adversarial inputs.
    """

    def verify(self, claim: Claim) -> VerificationResult:
        logger.info(
            "DefaultAgent: unclassifiable claim rejected (claim_id=%s, text=%r)",
            claim.id,
            claim.text,
        )
        return VerificationResult(
            is_verified=False,
            confidence=0.0,
            reason="Claim could not be classified; conservative rejection applied.",
            agent_name=self.__class__.__name__,
        )
