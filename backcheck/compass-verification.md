# Compass Literature Review — Critical Verification Report

**Date:** 2026-03-13
**Verified by:** 3 parallel deep-research agents (web search, OpenReview API, ACL Anthology, arXiv, Semantic Scholar)
**Subject:** `compass_artifact_wf-78f2300a-8872-491a-b4c9-8b2c25d71dee_text_markdown.md`

---

## Executive Summary

The compass document presents a compelling narrative but contains **systematic factual errors** that undermine its reliability as a scientific source. Of 15 papers cited, **6 have fabricated or wrong author names**, **2 have swapped identities**, **1 was withdrawn from its claimed venue**, and multiple quantitative claims are exaggerated or misattributed. The document reads as LLM-generated with high confidence but insufficient verification — ironically exemplifying the very sycophancy and hallucination risks it describes.

**Verdict: The document's ANALYTICAL FRAMEWORK is largely sound, but its EVIDENTIAL FOUNDATION is unreliable. Every specific number and attribution must be independently verified before citation.**

---

## Section-by-Section Verification

### Section 1: Social Sycophancy (ELEPHANT, CAUSM)

#### ELEPHANT (Cheng et al., ICLR 2026)
- **Paper exists:** YES (OpenReview: igbRHKEiAs, ICLR 2026 Poster)
- **Authors:** Myra Cheng, Sunny Yu, Cinoo Lee, Pranav Khadpe, Lujain Ibrahim, Dan Jurafsky
- **"Tests 11 LLMs":** VERIFIED (abstract confirms)
- **"4 dimensions based on face-preservation theory":** NOT IN ABSTRACT — abstract mentions "social sycophancy" broadly
- **"Validation sycophancy 50pp (72% vs 22%)":** CONTRADICTED — abstract says **45pp**, not 50pp
- **"Indirectness sycophancy 63pp (84% vs 21%)":** UNVERIFIABLE from public metadata
- **"Framing sycophancy 28pp (88% vs 60%)":** UNVERIFIABLE from public metadata
- **"86% failure to challenge unfounded premises":** UNVERIFIABLE from public metadata
- **"48% validate both parties in conflict":** VERIFIED (abstract: "affirm whichever side the user adopts in 48% of cases")

**Severity: MEDIUM.** The paper exists and the broad claims are directionally correct, but specific percentages beyond 45pp and 48% cannot be verified and the 50pp figure directly contradicts the abstract.

#### CAUSM (ICLR 2025)
- **Paper exists:** YES (OpenReview: yRKelogz5i, ICLR 2025 Poster)
- **CRITICAL: Author is WRONG.** Compass says "Xu et al." — actual first author is **Haoxi Li** (co-authors: Xueyang Tang, Jie Zhang, Song Guo, Sikai Bai, Peiran Dong, Yue Yu)
- **"Structured Causal Models":** VERIFIED
- **"Spurious correlations in intermediate attention layers":** PARTIALLY — abstract says "intermediate layers", not specifically "attention layers"
- **"Sycophancy heads":** NOT IN ABSTRACT — abstract says "causally motivated head reweighting" (the term "sycophancy heads" may be coined by the compass author)
- **"Knowledge calibration along causal representation direction":** VERIFIED but omits qualifier "intra-head"

**Severity: HIGH.** Wrong author attribution is a citation integrity violation.

#### CONSENSAGENT (ACL Findings 2025)
- **Paper exists:** YES (aclanthology.org/2025.findings-acl.1141)
- **Authors:** Priya Pitre, Naren Ramakrishnan, Xuan Wang — CORRECT
- **"Reactive trigger-based prompt optimization":** INACCURATE — paper says "dynamically refines prompts based on agent interactions"

**Severity: LOW.** Minor characterization issue.

#### "Ask Don't Tell" (arXiv:2602.23971)
- **Paper exists:** YES. Authors: Magda Dubois, Cozmin Ududec, Christopher Summerfield, Lennart Luettgau

**Severity: NONE.** Correctly cited.

#### "Peacemaker or Troublemaker" (OpenReview: hkBM5QkFVg)
- **Paper exists:** YES, BUT **WITHDRAWN from ICLR 2026**
- Cannot be cited as an ICLR 2026 publication

**Severity: MEDIUM.** Must be cited as withdrawn/preprint only.

---

### Section 2: Multi-Agent Debate Failures

#### Wynn & Satija 2025 "Talk Isn't Always Cheap" (arXiv:2509.05396)
- **Paper exists:** YES. Published at **ICML 2025** (PMLR 267)
- **CRITICAL: Author name WRONG.** First author is **Andrea Wynn**, not "Ori Wynn". Third author **Gillian Hadfield** entirely omitted.
- **"Actively worsens collective reasoning":** EXAGGERATED — paper says debate "can sometimes be harmful rather than helpful"
- **"Tyranny of the majority":** VERIFIED — paper uses this exact phrase
- **"Massively disrupts":** NOT FOUND in paper
- **"Rhetoric over truth" / "bluster":** LIKELY FABRICATED terminology — not found in searchable content
- **"LLM arbitrators systematically deceived":** MISFRAMED — paper focuses on agents within debate conforming, not on external arbitrators being deceived

**Severity: HIGH.** Wrong author name + multiple exaggerations.

#### Wu et al. 2025 "Can LLM Agents Really Debate?" (arXiv:2511.07784)
- **Paper exists:** YES
- **CRITICAL: ENTIRE AUTHOR LIST FABRICATED.** Compass/bib says "Wu, Jingyi; Chen, Zhijing; Zhang, Zhiheng; Bareinboim, Elias". Actual authors: **Haolun Wu, Zhenkun Li, Lingyao Li** (McGill/Mila, U. South Florida). Elias Bareinboim (Columbia) is a real researcher entirely unaffiliated with this paper.
- **"Knight-Knave-Spy benchmark":** VERIFIED
- **Regression coefficients (−0.010, 0.033, −0.158):** UNVERIFIABLE without full paper access — suspiciously precise
- **"Intrinsic model strength and group architectural diversity":** PARTIALLY — paper says "group diversity", not "architectural diversity"

**Severity: CRITICAL.** Fabricated author list is academic misconduct if published.

#### Zhang et al. 2026 SDRL (arXiv:2601.22297)
- **Paper exists:** YES
- **CRITICAL: Author name WRONG.** First author is **Chenxi Liu** (co-authors: Yanshuo Chen, Ruibo Chen, Tianyi Xiong, Tong Zheng, Heng Huang). No "Qi Zhang" exists among authors.
- **Year:** Paper is from January 2026, not 2025 as listed in bib
- **"Formally prove MAD is a martingale":** PARTIALLY — paper "recovers the key implication" via theoretical modeling, not a formal mathematical proof
- **"Error propagation exactly cancels error correction":** EDITORIALIZED gloss on martingale property
- **SDRL via RLVR:** VERIFIED
- **"Domain-constrained to verifiable tasks":** REASONABLE INFERENCE (inherent RLVR limitation) but not in those words

**Severity: CRITICAL.** Wrong author + wrong year.

#### ConfMAD (Lin & Hooi, EMNLP Findings 2025)
- **Paper exists:** YES (aclanthology.org/2025.findings-emnlp.343)
- **Authors:** Zijie Lin, Bryan Hooi — CORRECT
- **Title:** "Enhancing Multi-Agent Debate System Performance via Confidence Expression"
- **BUT:** In references.bib, the `colmad2025` key contains ConfMAD's title with wrong author "Li, Wei". The `confmad2025` key points to a DIFFERENT paper (arXiv:2601.19921).

**Severity: CRITICAL.** BibTeX keys are swapped; both entries have wrong authors.

#### ColMAD (OpenReview: W6qSjvTQMW)
- **Paper exists:** YES (also arXiv:2510.20963)
- **Title:** "Towards Scalable Oversight with Collaborative Multi-Agent Debate in Error Detection"
- **Authors:** Yongqiang Chen, Gang Niu, James Cheng, Bo Han, Masashi Sugiyama
- **Venue:** Submitted to ICLR 2026 (acceptance status unclear)
- **Not correctly represented in references.bib at all**

**Severity: HIGH.** No correct bib entry exists.

---

### Section 4: Cosine Similarity Critique

#### "How Small Transformations..." (arXiv:2509.09714)
- **Paper exists:** YES
- **"99.9% false-positive rate for cosine similarity":** MISLEADING — this applies specifically to **CodeBERT** in opposition detection, not to cosine similarity as a generic metric. Paper tests 18 different similarity measures.
- **"0.82-0.99 similarity for opposites":** PARTIALLY — applies to embedding methods as a class; LLM-based approaches correctly scored 0.00-0.29
- **CRITICAL CONTEXT OMISSION:** Paper is about **code similarity** (software engineering, 5,068 pairs), not natural language text review. Extrapolation to NL requires explicit qualification.

**Severity: HIGH.** The most rhetorically powerful claim in the compass document is built on a decontextualized, model-specific finding from a code-domain paper.

#### "Rethinking Metrics..." (arXiv:2602.15716)
- **Paper exists:** YES (Goworek & Dubossarsky, Feb 2026)
- **"Euclidean outperforms cosine by 24-66%":** MISATTRIBUTED — this number is from arXiv:2509.09714 (CodeBERT paper), not this paper. This paper is about diachronic lexical semantic change, an entirely different task.

**Severity: HIGH.** Cross-paper number attribution — either confusion or deliberate misattribution.

---

### Section 5: Authority Documents / RAG Security

#### AgentSentry (arXiv:2602.22724)
- **Paper exists:** YES
- **"Temporal causal takeover":** VERIFIED
- **Author:** Tian Zhang et al. — correct

**Severity: NONE.** Correctly represented.

---

### Section 7: Claim Extraction

#### Claimify (claimed: Wanner, Ebner, Jiang & Roth, ACL 2025)
- **CRITICAL: Attribution is WRONG.** The actual Claimify paper at ACL 2025 is by **Dasha Metropolitansky and Jonathan Larson** (Microsoft Research). The Wanner/Ebner team wrote a DIFFERENT paper ("A Closer Look at Claim Decomposition") at ***SEM 2024**, and no "Roth" was among their authors.
- **"5 failure modes" (over-splitting, etc.):** UNVERIFIABLE — this specific taxonomy could not be confirmed in either paper

**Severity: HIGH.** Complete author misattribution + possibly fabricated taxonomy.

---

### Section 8: Fagan Parallel / Other

#### "Multi-Agent LLM Debate Unveils the Premise Left Unsaid" (ACL ArgMining 2025)
- **Paper exists:** YES (aclanthology.org/2025.argmining-1.6)

**Severity: NONE.**

#### GeoSteer (arXiv:2601.10229)
- **Paper exists:** YES
- **"Logical shifts as latent gradient changes":** OVERSIMPLIFIED — paper is about steering toward better reasoning, not measuring logical shifts

**Severity: LOW.**

#### Identity Skews Debate (arXiv:2510.07517)
- **Paper exists:** YES (title revised between v1 and v2)

**Severity: NONE.**

---

## Aggregated Error Table

| Category | Count | Papers Affected |
|----------|-------|-----------------|
| Fabricated/wrong author names | 6 | CAUSM, Wynn, Wu, SDRL, ColMAD, ConfMAD bib entries |
| Swapped bib keys | 2 | colmad2025 ↔ confmad2025 |
| Withdrawn paper cited as published | 1 | "Peacemaker or Troublemaker" |
| Exaggerated/misleading numbers | 4 | ELEPHANT 50pp (actual 45pp), "99.9%" decontextualized, "24-66%" misattributed, regression coefficients unverifiable |
| Misattributed paper content | 2 | Claimify authors, Euclidean/cosine attribution |
| Fabricated terminology | 3+ | "sycophancy heads", "rhetoric over truth"/"bluster", "5 failure modes" |
| Wrong year | 1 | SDRL (2025→2026) |

---

## Impact on Ipcha Mistabra v2.0.0

Our v2.0.0 commit already contains 7 references from the compass document's earlier version (critics.md). These share the same hallucinated author problem:

| Bib Key | Listed Author | Actual Author | Status |
|---------|--------------|---------------|--------|
| causm2025 | Xu, Haoran | **Li, Haoxi** | WRONG |
| wynn2025 | Wynn, Ori | **Wynn, Andrea** + missing Hadfield | WRONG |
| wu2025_debate | Wu, Jingyi; Chen, Zhijing; Zhang, Zhiheng; Bareinboim, Elias | **Wu, Haolun; Li, Zhenkun; Li, Lingyao** | ENTIRELY FABRICATED |
| sdrl2025 | Zhang, Qi | **Liu, Chenxi** et al. | WRONG + wrong year (2025→2026) |
| colmad2025 | Li, Wei | Contains WRONG title (ConfMAD's) + wrong author | SWAPPED + WRONG |
| confmad2025 | Wang, Zhe | Points to wrong paper | SWAPPED + WRONG |
| cheng2026 | Cheng, Myra and others | Cheng, Myra et al. | OK (shorthand acceptable) |

**6 of 7 new references need immediate correction.**

---

## Assessment of Analytical Claims (Separate from Evidential Errors)

Despite the citation errors, the compass document's core analytical claims are **directionally supported** by the verified literature:

| Analytical Claim | Verdict | Confidence |
|-----------------|---------|------------|
| Sycophancy is architectural, not just behavioral | SUPPORTED (CAUSM, ELEPHANT) | HIGH |
| MAD can degrade rather than improve accuracy | SUPPORTED (Wynn, Wu) | HIGH |
| Structural debate parameters have marginal effect | SUPPORTED (Wu) | MEDIUM-HIGH |
| Vanilla MAD has martingale-like stagnation properties | SUPPORTED (SDRL paper) | MEDIUM |
| Cosine similarity fails at opposition detection | SUPPORTED but OVERSTATED (code-domain specific, model-dependent) | MEDIUM |
| RAG systems vulnerable to prompt injection cascades | SUPPORTED (AgentSentry) | HIGH |
| Claim extraction destroys relational structure | PLAUSIBLE but poorly sourced | LOW-MEDIUM |
| CAUSM/SDRL/ConfMAD as layered defense | WELL-ARGUED synthesis | HIGH (analytical) |
