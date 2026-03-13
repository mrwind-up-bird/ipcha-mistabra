# Step 1: Prepare
**Provider:** google / gemini-2.5-pro | **Tokens:** 5,250 | **Cost:** $0.0120 | **Duration:** 25.9s

## Prompt
Extract the core thesis, key claims, and implicit assumptions from the following input.

Structure as:
## Core Thesis
## Key Claims (numbered)
## Implicit Assumptions (numbered)

Input:
{{input}}

## Output
## Core Thesis
The existing generic, one-size-fits-all method for evaluating AI personas is ineffective, unauditable, and fails to test for sophisticated vulnerabilities. A superior approach is to implement a structured, persona-specific evaluation framework centered on a detailed `PersonaProfile` artifact, which enables more precise, auditable, and robust testing, including tailored adversarial attacks.

## Key Claims (numbered)
1.  A structured `PersonaProfile` should be the central artifact for defining and evaluating each persona's characteristics, rules, and vulnerabilities. This profile will drive test generation, judging, and scoring.
2.  Replacing the generic judging system with persona-specific rubrics and multi-dimensional scoring (role adherence, rule compliance, marker presence) will produce more accurate and auditable evaluation results, particularly through the inclusion of a "reasoning" field.
3.  Tailored, persona-specific adversarial attacks (e.g., "authority hijack," "domain edge") are a more effective method for testing a persona's resilience and safety than the current generic jailbreak prompts.
4.  Applying different scoring weight profiles based on the test type (e.g., prioritizing `refusalQuality` in jailbreak tests vs. `roleAdherence` in temperature tests) provides a more contextually relevant and meaningful final score.
5.  An automated pipeline using an LLM can reliably derive a structured `PersonaProfile` from a custom persona's system prompt, making the advanced evaluation system scalable to user-created personas.
6.  The new evaluation system can be implemented with non-breaking, additive schema changes, ensuring backward compatibility with existing evaluation data while enabling a clear transition to the new scoring metric.

## Implicit Assumptions (numbered)
1.  A large language model (LLM) is sufficiently capable and consistent to act as a reliable "judge" for scoring another LLM's output against a complex, multi-dimensional rubric.
2.  An LLM can accurately parse a persona's natural language system prompt and deconstruct it into a structured, valid `PersonaProfile` JSON, including creating relevant test cases and attack vectors.
3.  The defined `PersonaProfile` interface is comprehensive enough to capture the most important and testable characteristics of any given persona.
4.  The significant increase in computational cost and time (from a few LLM calls to 16 per evaluation) is a worthwhile trade-off for the improved quality and detail of the evaluation results.
5.  Human-authored profiles for the 12 built-in personas will be qualitatively superior and more effective for testing than auto-derived ones.
6.  The proposed test types (Temperature, Degradation, Adversarial Exploitation) are valid and sufficient proxies for measuring a persona's real-world performance and robustness.
7.  The application will continue to operate in a single-instance environment where an in-memory, per-process cache is a sufficient and acceptable solution for the foreseeable future.
