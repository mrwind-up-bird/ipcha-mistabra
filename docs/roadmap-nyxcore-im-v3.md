# nyxCore Roadmap: Ipcha Mistabra v3.0 — From Theatrical Dissent to Genuine Epistemic Correction

**Date:** 2026-03-13
**Status:** Draft — pending Oliver Baer review
**Basis:** Verified 2025-2026 literature (see `backcheck/compass-verification.md` for source validation)

---

## Problem Statement

The 2025-2026 literature establishes that the IM Protocol v2.0 operates in a regime where:
1. **Sycophancy is architectural** (CAUSM, Li et al. ICLR 2025) — prompt-level role assignment ("assume FALSE") cannot override weight-level conditioning
2. **MAD stagnates** (Liu et al. 2026) — vanilla multi-agent debate has martingale properties; expected truth convergence is zero
3. **Cosine similarity is blind to logic** (arXiv:2509.09714) — embedding-based metrics fail at opposition detection (model-dependent, worst case in code domain)
4. **RAG is an attack surface** (AgentSentry, Zhang et al. 2026) — cryptographic integrity doesn't protect against semantic injection

The protocol's modular architecture was designed for exactly this scenario: swap components without changing the surrounding structure. The roadmap below specifies **what to swap, in what order, and what's blocked by open research.**

---

## Phase 0: Immediate Fixes (Week 1)

### 0.1 Reference Integrity Audit ✅ DONE
- Fixed 6/7 fabricated author names in `references.bib`
- Fixed swapped ColMAD/ConfMAD bib entries
- Fixed SDRL year (2025→2026)
- Full verification report: `backcheck/compass-verification.md`

### 0.2 Paper Prose Corrections (Week 1)
Compass document analysis revealed that several claims we cite in v2.0.0 main.tex are more nuanced than stated:

| Section | Issue | Fix |
|---------|-------|-----|
| 2.3 | "48% of the time" cited from ELEPHANT — verify this is from abstract | OK (verified: abstract says "48%") |
| 2.5 | Wynn claims about debate degradation | Our prose already hedged ("can degrade") — OK |
| 4 | IS false-positive discussion doesn't cite specific numbers | OK — we discuss the mechanism, not specific rates |

**Assessment: v2.0.0 prose is defensible.** The references were wrong, but the analytical claims in our paper are hedged correctly and don't depend on the specific fabricated numbers from the compass document.

---

## Phase 1: Ipcha Score Reform (Weeks 2-4)

### Problem
Cosine similarity fails at opposition detection. The arXiv:2509.09714 study shows embedding methods assign 0.82-0.99 similarity to semantically opposite content. While this study is code-domain-specific and model-dependent (CodeBERT worst, LLM-based approaches better), the fundamental limitation applies: embeddings encode distributional co-occurrence, not logical relations.

### 1.1 Replace IS with IS_w as Primary Metric
- **Action:** Implement `IS_w` (finding-weighted score) as the default operational metric
- **Rationale:** IS_w operates on structured finding data (severity, status changes), not embedding distance
- **Keep IS as:** Optional screening signal for cross-system comparisons where structured outputs are unavailable
- **Implementation:** `ipcha/score.py` — IS_w is already defined in the paper; implement and test

### 1.2 Evaluate Alternative Distance Metrics for IS
- **Action:** Benchmark IS computation with multiple distance functions:
  - Cosine similarity (current baseline)
  - Euclidean distance (24-66% improvement over cosine for CodeBERT — verify transfer to NL embeddings)
  - NLI-based contradiction detection (e.g., via `cross-encoder/nli-deberta-v3-large`)
- **Implementation:** `ipcha/score.py` — make distance metric configurable, default to NLI-based
- **Test:** Construct adversarial pairs (boolean inversions, verbosity-only changes, paraphrases) and measure discrimination

### 1.3 Research Track: Formal Verification Metrics (Long-term)
- **Goal:** Translate subset of extractable claims into LTL templates for deterministic verification
- **Dependency:** Requires domain-specific claim-to-logic translation (no off-the-shelf tool exists)
- **Status:** Future work — acknowledged in paper Section 4

---

## Phase 2: Anti-Sycophancy Architecture (Weeks 4-8)

### Problem
The Ipcha Agent operates via system prompt ("assume FALSE"). CAUSM (Li et al., ICLR 2025) demonstrates that sycophancy originates from spurious correlations in intermediate transformer layers, requiring weight-level intervention. ELEPHANT (Cheng et al., ICLR 2026) measures the scale: LLMs preserve user face ~45pp more than human experts.

### 2.1 Model Selection Strategy
- **Action:** Implement model diversity requirements in `ipcha/protocol.py`
  - Proponent and Ipcha Agent MUST use different model families (e.g., Claude + GPT-4 + Gemini)
  - Wu et al. (2025) confirm: "group diversity" is the only significant structural predictor of debate success
- **Implementation:** `ipcha/protocol.py` — model configuration per role, validation that roles use distinct providers

### 2.2 CAUSM Integration Path (Medium-term)
- **Dependency:** CAUSM requires access to model weights (open-weight models only)
- **Action for open-weight deployments:**
  1. Apply CAUSM causal head reweighting to the Ipcha Agent model
  2. Measure sycophancy reduction via ELEPHANT-style evaluation
  3. Compare prompt-only vs. CAUSM-calibrated contradiction quality
- **Action for API-only deployments:**
  - Document that prompt-level role assignment is a "first-order approximation" (already in v2.0.0 prose)
  - Implement behavioral sycophancy detection as a meta-metric (see 2.3)

### 2.3 Sycophancy Detection Meta-Metrics
- **Action:** Add protocol-level sycophancy indicators to `ipcha/audit.py`:
  - **Agreement rate:** % of Proponent claims the Ipcha Agent accepts without challenge
  - **Contradiction depth:** Average evidence count per challenged claim
  - **Capitulation rate:** How often the Ipcha Agent reverses position when the Proponent provides counter-evidence
- **Alert threshold:** If agreement rate > 70%, flag as potential sycophantic collapse
- **Implementation:** New module `ipcha/sycophancy_monitor.py`

---

## Phase 3: Auditor Reform (Weeks 6-10)

### Problem
The Auditor Warning Paradox (documented in v2.0.0, Section 7.4): RLHF-trained Auditors structurally down-weight extreme but correct Ipcha findings because such findings are statistical outliers in training distributions.

### 3.1 Confidence-Weighted Arbitration (ConfMAD Integration)
- **Action:** Replace narrative-based Auditor synthesis with structured confidence aggregation
  - Ipcha Agent outputs: `Finding` + `confidence: float [0,1]` + `evidence_strength: float [0,1]`
  - Proponent outputs: `CounterArgument` + `confidence: float [0,1]`
  - Auditor aggregates via confidence tensors, not persuasive text
- **Implementation:** Extend `ipcha/models.py` with confidence fields; new `ipcha/arbitration.py` module
- **Reference:** Lin & Hooi, ConfMAD (EMNLP Findings 2025)

### 3.2 Rejection Logging and Audit Trail
- **Action:** Require explicit written justification for each rejected Ipcha finding
  - Log rejection ratios as protocol-level meta-metric
  - High rejection rate (>80%) triggers human review alert
- **Implementation:** `ipcha/audit.py` — structured rejection reasons in Finding model

### 3.3 Cooperative Protocol Evaluation (ColMAD, Long-term)
- **Action:** Evaluate reframing the trialectic as cooperative (non-zero-sum) rather than adversarial
  - ColMAD (Chen et al., arXiv:2510.20963) provides the framework
  - Test whether cooperative framing reduces both conformity AND rhetoric-over-truth
- **Dependency:** Requires controlled evaluation (Phase 5)

---

## Phase 4: Security Hardening (Weeks 8-12)

### 4.1 Input Sanitization / IPI Defense
- **Action:** Implement pre-processing pipeline for input artifacts:
  1. Strip zero-width characters, hidden Unicode, metadata injection vectors
  2. Detect instruction-like content embedded in authority documents
  3. Log all detected anomalies
- **Reference:** AgentSentry (Zhang et al., arXiv:2602.22724)
- **Implementation:** New module `ipcha/sanitize.py`

### 4.2 Cross-Chunk Coherence Validation
- **Action:** Before passing retrieved authority chunks to agents, validate:
  - No instruction-like content appears in assembled context that's absent from individual chunks
  - No contradictory directives across chunks
  - Semantic consistency check of assembled context
- **Implementation:** `ipcha/authority/validator.py`

### 4.3 Denial-of-Wallet Defense
- **Action:** Implement claim budget and cost controls (already documented in v2.0.0, Section 7.3):
  - `|C|_max` configurable claim budget (default: 100)
  - Per-invocation cost ceiling with automatic abort + partial report
  - Priority queue: process claims in descending estimated severity
- **Implementation:** `ipcha/extract.py` — claim count gate; `ipcha/protocol.py` — cost tracking

---

## Phase 5: Evaluation Infrastructure (Weeks 10-16)

### 5.1 Controlled Evaluation Suite
- **Action:** Build evaluation harness for IM Protocol variants:
  - **Benchmark:** Knight-Knave-Spy puzzles (Wu et al., 2025) for isolating debate quality from domain knowledge
  - **Metrics:** Finding accuracy, gate decision correctness, false positive/negative rates
  - **Baselines:** Single-agent review, unstructured MAD, ConfMAD, IM Protocol
- **Implementation:** `tests/evaluation/` directory with configurable experiment runner

### 5.2 Sycophancy Evaluation (ELEPHANT-style)
- **Action:** Adapt ELEPHANT benchmark dimensions to the IM context:
  - Present Ipcha Agent with claims that are clearly false but well-argued
  - Measure challenge rate, evidence quality, capitulation under counter-pressure
  - Compare prompt-only vs. CAUSM-calibrated (where available)

### 5.3 Adversarial Red-Teaming
- **Action:** Construct adversarial test cases:
  - **Boolean inversion:** Compliance claims with single-word negation
  - **Verbosity churn:** Cosmetically different but semantically identical outputs
  - **Claim inflation:** Thousands of trivial claims (DoW test)
  - **IPI injection:** Authority documents with embedded instructions
  - **Cross-chunk coherence:** Fragmented malicious payloads across chunks

---

## Phase 6: SDRL Research Track (Long-term, Weeks 16+)

### Problem
Liu et al. (arXiv:2601.22297) prove that vanilla MAD induces a martingale over agent beliefs. SDRL breaks this via RLVR (Reinforcement Learning with Verifiable Rewards), but only for domains with verifiable answers.

### 6.1 Feasibility Assessment
- **Question:** Can RLVR be applied to security/compliance review?
  - Some claims ARE verifiable (e.g., "system uses AES-256" — checkable against config)
  - Most compliance claims require interpretation (not directly verifiable)
- **Action:** Classify IM claim types into verifiable vs. interpretive; estimate RLVR coverage

### 6.2 SDRL-Trained Ipcha Agent (If Feasible)
- **Dependency:** Requires open-weight model + verifiable reward signal
- **Action:** Fine-tune adversarial agent via SDRL on verifiable security claims
- **Expected outcome:** Agent develops "private critique capabilities" that resist social conformity

### 6.3 Hybrid Architecture
- **Action:** Design hybrid where:
  - SDRL-trained agent handles verifiable claims
  - Prompt-based agent (with CAUSM calibration) handles interpretive claims
  - Protocol routes claims to appropriate agent based on verifiability classification
- **Implementation:** `ipcha/routing.py`

---

## Dependency Graph

```
Phase 0 (Immediate) ──→ Phase 1 (IS Reform)
                    ──→ Phase 2 (Anti-Sycophancy) ──→ Phase 3 (Auditor Reform)
                    ──→ Phase 4 (Security) ──────────→ Phase 5 (Evaluation)
                                                  ──→ Phase 6 (SDRL Research)
```

Phases 1, 2, and 4 can run in parallel after Phase 0.
Phase 3 depends on Phase 2 (model diversity must be in place before Auditor reform).
Phase 5 depends on Phases 1-4 (need implementations to evaluate).
Phase 6 is independent research track.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CAUSM requires model weights → blocks API-only deployments | HIGH | MEDIUM | Sycophancy meta-metrics (2.3) provide API-compatible fallback |
| SDRL doesn't transfer to non-verifiable domains | HIGH | MEDIUM | Hybrid architecture (6.3) limits blast radius |
| ConfMAD confidence values are uncalibrated / gameable | MEDIUM | HIGH | Cross-validate confidence against evidence strength |
| Evaluation requires significant compute budget | HIGH | LOW | Start with Knight-Knave-Spy (cheap, verifiable) |
| NLI-based IS replacement introduces new failure modes | MEDIUM | MEDIUM | Keep cosine-IS as secondary metric for regression detection |

---

## What the Literature Does NOT Demand (Scope Control)

The compass document overstates several requirements. Based on verified evidence:

1. **"99.9% false-positive rate" does NOT apply generically** — it's CodeBERT-specific in a code-similarity domain. Text-embedding-3-large (our model) was not tested. IS reform is warranted but not because of this specific number.

2. **"Cosine similarity is structurally unsuitable"** is too strong — the 2509.09714 study shows LLM-based approaches correctly produce low scores (0.00-0.29) for semantic differences. The issue is model-dependent, not metric-dependent.

3. **The "martingale proof" is a theoretical model**, not a formal impossibility result — it shows vanilla MAD doesn't IMPROVE in expectation, not that it always fails. The protocol's structured finding objects and evidence binding already deviate from "vanilla MAD."

4. **Claimify's "5 failure modes"** — the specific taxonomy (over-splitting, under-splitting, etc.) could not be verified in any published paper. Claim extraction challenges are real but the cited taxonomy may be fabricated.

5. **"Peacemaker or Troublemaker"** was withdrawn from ICLR 2026 — do not cite as evidence.

---

## Implementation Priority (nyxCore Engineering)

| Priority | Item | Effort | Value |
|----------|------|--------|-------|
| P0 | Reference fixes (done) | 1h | CRITICAL |
| P1 | IS_w as primary metric | 2d | HIGH — removes dependence on cosine |
| P1 | Model diversity requirement | 1d | HIGH — only verified structural predictor |
| P1 | Input sanitization | 3d | HIGH — production security |
| P2 | Confidence-weighted arbitration | 5d | HIGH — addresses warning paradox |
| P2 | Sycophancy meta-metrics | 3d | MEDIUM — monitoring capability |
| P2 | DoW defense (claim budget) | 2d | MEDIUM — operational safety |
| P3 | NLI-based IS variant | 5d | MEDIUM — better opposition detection |
| P3 | Cross-chunk coherence validator | 5d | MEDIUM — RAG security |
| P3 | Evaluation suite | 10d | MEDIUM — scientific credibility |
| P4 | CAUSM integration | 10d+ | HIGH but blocked by model access |
| P4 | SDRL research track | Months | HIGH but speculative |
