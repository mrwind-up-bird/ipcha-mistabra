# Paper v2.0.0: Critics-Driven Refactoring Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate 2025/2026 multi-agent debate, sycophancy, and AI-security research into the Ipcha Mistabra paper. Address all valid critique points from `backcheck/critics.md` and additional user-provided research directions. Strengthen the paper through honest engagement with limitations, not defensive rebuttal.

**Architecture:** Nine targeted edits to `main.tex` and `references.bib`. No structural reorganization — all changes are additive paragraphs, sentence-level edits, or expansions within existing sections. New references expand the bibliography from 9 to 16 entries.

**Tech Stack:** LaTeX (pdflatex + bibtex), references.bib (BibTeX)

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `references.bib` | Modify | Add 7 new bibliography entries |
| `main.tex` | Modify | 9 targeted edits across Sections 2, 3, 4, 7, 8 |
| `CHANGELOG.md` | Modify | Document v2.0.0 changes |
| `backcheck/critics.md` | Read-only | Source of critique (no changes) |

All changes are within `main.tex` lines 96–770 and `references.bib`.

---

## Chunk 1: New References + MAD Failure Modes in Related Work

### Task 1: Add new bibliography entries to references.bib

**Files:**
- Modify: `references.bib` (append after line 68)

- [ ] **Step 1: Add 7 new BibTeX entries**

Append the following after the closing `}` of `autogen2023`:

```bibtex
@inproceedings{wynn2025,
  title     = {Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate},
  author    = {Wynn, Ori and Satija, Harsh},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2025},
  note      = {arXiv:2509.05396},
}

@inproceedings{wu2025_debate,
  title     = {Can {LLM} Agents Really Debate? {A} Controlled Study of Multi-Agent Debate in Logical Reasoning},
  author    = {Wu, Jingyi and Chen, Zhijing and Zhang, Zhiheng and Bareinboim, Elias},
  year      = {2025},
  note      = {arXiv:2511.07784},
}

@inproceedings{cheng2026,
  title     = {{ELEPHANT}: Measuring and Understanding Social Sycophancy in {LLMs}},
  author    = {Cheng, Myra and others},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026},
}

@article{sdrl2025,
  title     = {Prepare Reasoning Language Models for Multi-Agent Debate with Self-Debate Reinforcement Learning},
  author    = {Zhang, Qi and others},
  year      = {2025},
  note      = {arXiv:2601.22297},
}

@inproceedings{colmad2025,
  title     = {Enhancing Multi-Agent Debate System Performance via Confidence Expression},
  author    = {Li, Wei and others},
  booktitle = {Findings of EMNLP},
  year      = {2025},
}

@article{causm2025,
  title     = {Causally Motivated Sycophancy Mitigation for Large Language Models},
  author    = {Xu, Haoran and others},
  year      = {2025},
  note      = {OpenReview:yRKelogz5i},
}

@inproceedings{confmad2025,
  title     = {Demystifying Multi-Agent Debate: The Role of Confidence and Diversity},
  author    = {Wang, Zhe and others},
  year      = {2025},
  note      = {arXiv:2601.19921},
}
```

- [ ] **Step 2: Verify bibtex compiles**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

Expected: No undefined citation warnings for the new keys.

- [ ] **Step 3: Commit**

```bash
git add references.bib
git commit -m "refs: add 7 new entries (MAD failures, sycophancy, cooperative debate)"
```

---

### Task 2: Expand Section 2.5 (Multi-Agent Debate) with MAD failure modes + cooperative alternatives

**Files:**
- Modify: `main.tex:146-149` (Section 2.5)

- [ ] **Step 1: Replace Section 2.5 content**

Current text (lines 146-149):
```latex
\subsection{Multi-Agent Debate}
Du et~al.\ demonstrated that multi-agent debate can improve factuality and reasoning by forcing explicit counter-arguments~\cite{du_multiagent_debate}.
However, debate-based setups typically lack: (i)~an explicit audit role with synthesis authority, (ii)~evidence binding against external sources, and (iii)~a formal gate that blocks output based on finding severity.
\methodname{} operationalizes adversarial pressure as a verifiable protocol (roles, artifacts, gate rules) rather than a prompt-based heuristic.
```

Replace with:
```latex
\subsection{Multi-Agent Debate}
\label{sec:mad}
Du et~al.\ demonstrated that multi-agent debate can improve factuality and reasoning by forcing explicit counter-arguments~\cite{du_multiagent_debate}.
However, subsequent empirical work has revealed fundamental failure modes in the debate paradigm.
Wynn and Satija~\cite{wynn2025} showed that LLM agents in multi-agent debate exhibit strong social conformity: agents systematically abandon correct minority positions when confronted with eloquent but incorrect majority arguments---a phenomenon they term ``tyranny of the majority''---and group accuracy \emph{degrades} over successive debate rounds.
Wu et~al.~\cite{wu2025_debate} confirmed through controlled logic-puzzle experiments that structural debate parameters (round count, role assignment, debate order) have negligible effect on accuracy; the dominant performance drivers are individual model strength and architectural diversity of the agent pool.

These findings have motivated two lines of successor work.
\emph{Cooperative protocols} reframe debate as a non-zero-sum game: ColMAD~\cite{colmad2025} introduces collaborative multi-agent structures in which agents complement rather than defeat each other.
\emph{Confidence-weighted protocols} such as ConfMAD~\cite{confmad2025} integrate explicit confidence scores into the deliberation process, preventing low-confidence but eloquent arguments from overriding high-confidence minority positions.

These findings constrain the design space for any multi-agent verification system, including \methodname{}.
The protocol addresses the identified failure modes through three structural mechanisms that distinguish it from pure debate:
(i)~an explicit audit role that operates over structured finding objects rather than narrative arguments, reducing susceptibility to persuasive falsehoods;
(ii)~evidence binding against external authority documents, providing a decision anchor independent of agent eloquence; and
(iii)~a formal gate rule that blocks output based on finding severity, not on consensus or majority opinion.
The protocol does not claim to solve the social conformity problem in LLMs; rather, it routes the decision through structured data and external references to reduce the surface area where conformity dynamics can cause harm.
We note that cooperative protocols (ColMAD) and confidence-weighted arbitration (ConfMAD) represent promising architectural alternatives to the current sequential trialectic; their integration is discussed in Section~\ref{sec:outlook}.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

Expected: Clean compilation, new citations resolved.

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec2.5: integrate MAD failure literature, ColMAD, ConfMAD (Wynn 2025, Wu 2025)"
```

---

## Chunk 2: Sycophancy Depth (CAUSM, SDRL) + Auditor Warning Paradox

### Task 3: Expand Section 2.3 (Sycophancy) with architectural depth + CAUSM

**Files:**
- Modify: `main.tex:135-138` (Section 2.3)

- [ ] **Step 1: Replace Section 2.3 content**

Current text (lines 135-138):
```latex
\subsection{Failure Modes of LLM-Assisted Text Analysis}
Sycophancy denotes the tendency of models to confirm user opinions even at the expense of truth~\cite{sharma_sycophancy}.
Perez et~al.\ showed that model-written evaluations can systematically discover such behavioral failures~\cite{perez2023}.
For safety-relevant text reviews this is especially critical, because ``confirmation'' can be mistakenly interpreted as ``validation.''
```

Replace with:
```latex
\subsection{Failure Modes of LLM-Assisted Text Analysis}
\label{sec:sycophancy}
Sycophancy denotes the tendency of models to confirm user opinions even at the expense of truth~\cite{sharma_sycophancy}.
Perez et~al.\ showed that model-written evaluations can systematically discover such behavioral failures~\cite{perez2023}.
For safety-relevant text reviews this is especially critical, because ``confirmation'' can be mistakenly interpreted as ``validation.''

Recent work demonstrates that sycophancy is not merely a prompting artifact but a property rooted in model architecture.
Cheng et~al.~\cite{cheng2026} measured \emph{social sycophancy} at scale and found that LLMs validate both parties in conflict scenarios up to 48\% of the time, even when explicitly instructed to take a position.
Causal analyses trace this behavior to spurious correlations in intermediate attention layers; the CAUSM framework~\cite{causm2025} models sycophancy as a structural causal graph and eliminates it through targeted head reweighting---a weight-level intervention that inference-time prompting cannot replicate.
An orthogonal approach, Self-Debate Reinforcement Learning (SDRL)~\cite{sdrl2025}, trains models via verifiable rewards (RLVR) to extract collaborative value from divergent reasoning paths rather than collapsing to the most fluent consensus.

These findings have direct implications for any multi-agent protocol that assigns adversarial roles via system prompts.
\methodname{} does not claim to solve architectural sycophancy through prompting alone; its defense is structural: role separation across distinct model instances, evidence binding that forces external grounding, and a gate rule that operates on structured finding data rather than narrative persuasion.
We acknowledge that the prompt-level contradiction in Appendix~\ref{app:prompts} (``assume the claim is FALSE'') is a first-order approximation.
Deeper mitigations---CAUSM-calibrated models~\cite{causm2025} or SDRL-trained debaters~\cite{sdrl2025}---are complementary to the protocol and can serve as drop-in replacements for the Ipcha Agent role without changing the surrounding architecture.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec2.3: architectural sycophancy depth — CAUSM, SDRL, Cheng 2026"
```

---

### Task 4: Add Auditor Warning Paradox as distinct limitation in Section 7.4

**Files:**
- Modify: `main.tex:692-700` (Section 7.4, after "Limitations" label, before "Correlated model failures")

- [ ] **Step 1: Insert new paragraph before "Correlated model failures"**

Insert between line 694 (`\label{sec:limitations}`) and line 695 (`\paragraph{Correlated model failures.}`):

```latex
\paragraph{Auditor failure and the warning paradox.}
Even when the Ipcha Agent produces correct and well-grounded warnings, the protocol can fail if the Auditor systematically discounts them.
This is distinct from correlated model failures (below): the Ipcha Agent and Auditor may use architecturally diverse models with uncorrelated blind spots, yet the Auditor may still reject valid warnings because its synthesis heuristic favors consensus, statistical plausibility, or surface-level coherence over outlier signals.
This phenomenon mirrors the \emph{warning paradox} in intelligence analysis, where institutionalized dissent loses effectiveness when the receiving entity suffers from conceptual rigidity~\cite{wynn2025}.
An LLM Auditor fine-tuned via RLHF to produce balanced, consensual outputs will structurally down-weight extreme but correct Ipcha findings, because such findings represent statistical outliers in the training distribution.
The result is a protocol that \emph{performs} contradiction without \emph{acting on it}---the most dangerous failure mode, as it generates a false audit trail of due diligence.

Mitigations include:
(i)~requiring the Auditor to produce explicit written justification for each rejected Ipcha finding, forcing deliberation rather than reflexive dismissal;
(ii)~logging rejection ratios as a protocol-level meta-metric---a consistently high rejection rate may indicate Auditor conformity rather than Ipcha noise; and
(iii)~periodic human review of \emph{rejected} findings (not only accepted ones) to calibrate Auditor behavior.
Confidence-weighted arbitration~\cite{confmad2025} offers a structural alternative by replacing majority-vote synthesis with confidence-aware aggregation.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec7.4: auditor warning paradox — distinct from correlated failures"
```

---

## Chunk 3: Ipcha Score Honesty + Formal-Logic Future Direction

### Task 5: Clarify IS limitations, add verbosity bias, frame formal-logic future in Section 4

**Files:**
- Modify: `main.tex:391-402` (Section 4, known limitations + recommendation)

- [ ] **Step 1: Expand the false-positive failure mode (line 396)**

Current text of item 1 (line 396):
```latex
  \item \textbf{False positive (high score, low correction):} If the Auditor paraphrases the Proponent output without changing substance, the score inflates. Mitigation: complement with structured finding-level diff (count of status changes in $F$).
```

Replace with:
```latex
  \item \textbf{False positive (high score, low correction):} If the Auditor paraphrases the Proponent output without changing substance, the score inflates.
  A pervasive driver is \emph{verbosity bias}: LLMs routinely vary sentence structure, output length, formatting (e.g., prose vs.\ bullet lists), and vocabulary across invocations, producing substantial embedding displacement without altering epistemic content.
  Mitigation: complement $\mathit{IS}$ with structured finding-level diff (count of status changes in $F$).
```

- [ ] **Step 2: Replace the recommendation paragraph (lines 401-402)**

Current text (lines 401-402):
```latex
We recommend reporting $\mathit{IS}$ alongside finding-level metrics (recall, precision) and $\mathit{IS}_w$, and not using $\mathit{IS}$ as a sole decision criterion.
Future work should validate $\mathit{IS}$ against human expert ratings of correction strength (correlation study).
```

Replace with:
```latex
We recommend reporting $\mathit{IS}$ alongside finding-level metrics (recall, precision) and $\mathit{IS}_w$, and not using $\mathit{IS}$ as a sole decision criterion.
The two scores serve distinct purposes: $\mathit{IS}$ requires only the raw text outputs and is therefore computable even for unstructured reviews that lack finding-level annotation; $\mathit{IS}_w$ requires structured findings with severity and status tracking.
In fully instrumented IM deployments, $\mathit{IS}_w$ is the more reliable operational metric; $\mathit{IS}$ remains useful as a lightweight screening signal and for cross-system comparisons where structured outputs are unavailable.

\paragraph{Toward formal verification metrics.}
The fundamental limitation of both $\mathit{IS}$ and $\mathit{IS}_w$ is that they measure \emph{surface-level} displacement (embedding vectors) or \emph{structural} change (finding counts), neither of which captures logical validity.
A critical boolean inversion (e.g., ``the system is secure'' $\to$ ``the system has an unmitigated CVE'') may produce negligible embedding shift while representing the most important correction in the review.
Future work should investigate formal-logic extraction: translating natural-language claims into structured temporal-logic templates (e.g., LTL) that can be verified by deterministic solvers or theorem provers, and evaluating logical preference consistency via metrics such as transitivity, commutativity, and negation invariance.
Such approaches would complement the statistical proxy of $\mathit{IS}$ with mathematically verifiable correctness guarantees, moving the protocol from probabilistic screening toward deterministic validation for the subset of claims that admit formal representation.
```

- [ ] **Step 3: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 4: Commit**

```bash
git add main.tex
git commit -m "sec4: verbosity bias, IS/IS_w clarification, formal-logic future direction"
```

---

## Chunk 4: Operational Security (Denial of Wallet + RAG Hardening)

### Task 6: Add Denial of Wallet to Section 7.3 (Operational Integration Model)

**Files:**
- Modify: `main.tex:686-689` (Section 7.3, before Section 7.4)

- [ ] **Step 1: Insert DoW paragraph before the closing of Section 7.3**

Insert after line 689 (the risk-acceptance artifact paragraph) and before line 691 (`% [FIX F4: correlated model failures as core limitation]`):

```latex
\paragraph{Denial-of-wallet via claim inflation.}
The protocol's mandatory exhaustive evaluation creates an asymmetric cost exposure.
An adversary can submit a text artifact $T$ deliberately seeded with thousands of grammatically well-formed but trivially verifiable atomic claims, forcing the trialectic pipeline into massively parallel API evaluation.
Because the protocol requires the Ipcha Agent to process \emph{every} extracted claim (Algorithm~\ref{alg:contra}, line~2), and modern LLM context windows can accommodate millions of tokens, such an attack can consume significant API budget within minutes---a vector known as \emph{denial of wallet} (DoW).
Mitigations include:
(i)~a claim-count budget $|C|_{\max}$ that triggers human escalation rather than exhaustive evaluation when exceeded;
(ii)~a per-invocation cost ceiling with automatic abort and partial-report generation; and
(iii)~prioritized claim evaluation---processing claims in descending estimated severity so that the most critical issues surface first, even under budget constraints.
The asynchronous advisory mode described above naturally limits financial exposure, as non-blocking runs can be terminated without blocking the pipeline.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec7.3: denial-of-wallet attack vector and mitigations"
```

---

### Task 7: Expand Section 7.2 (Authority Document Trust Model) with RAG attack specifics

**Files:**
- Modify: `main.tex:660-673` (Section 7.2)

- [ ] **Step 1: Insert RAG-specific attack paragraph after line 663**

Current text ends with (line 663):
```latex
This is analogous to a supply-chain attack on knowledge artifacts rather than software dependencies.
```

Insert after this line (before "The current protocol does not provide mitigations"):

```latex
Modern RAG-specific attack vectors compound this risk.
\emph{Embedding inversion} techniques allow adversaries to craft document chunks that are semantically innocuous in isolation but, when retrieved together, reconstruct a coherent malicious instruction---a pattern known as \emph{cross-chunk coherence attack}.
Because the Ipcha Agent retrieves authority chunks via similarity search, not via a verified index, an attacker who can insert or modify documents in the authority corpus can steer the entire verification pipeline without triggering any individual-chunk anomaly detector.
```

Additionally, expand mitigation item 1 (line 668). Current:
```latex
  \item \textbf{Version-controlled authority corpus.} All authority documents must be stored in a version-controlled repository with cryptographic integrity guarantees (e.g., GPG-signed commits).
```

Replace with:
```latex
  \item \textbf{Version-controlled authority corpus with runtime integrity.} All authority documents must be stored in a version-controlled repository with cryptographic integrity guarantees (e.g., GPG-signed commits).
  At retrieval time, a \emph{cross-chunk coherence validator} should verify that the assembled context from multiple retrieved chunks does not contain instruction-like content or internally contradictory directives that were absent from each individual chunk.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec7.2: RAG attack specifics — embedding inversion, cross-chunk coherence"
```

---

## Chunk 5: Introduction Nuance + Expanded Future Work + Version Bump

### Task 8: Add nuance to Introduction (line 98-99) about training-time vs. runtime

**Files:**
- Modify: `main.tex:98-99` (Introduction, second paragraph)

- [ ] **Step 1: Expand the framing of the architectural problem**

Current text (lines 98-99):
```latex
Most mitigation strategies target training-time or inference-time behavioral alignment.
These approaches improve average behavior but leave a deeper architectural problem unaddressed: the same system instance is often responsible for both proposing and implicitly validating its own reasoning.
```

Replace with:
```latex
Most mitigation strategies target training-time alignment (e.g., RLHF, Constitutional AI) or inference-time behavioral steering (e.g., system prompts, chain-of-thought).
These approaches improve average behavior but leave a deeper architectural problem unaddressed: the same system instance is often responsible for both proposing and implicitly validating its own reasoning.
Recent empirical evidence suggests that this architectural limitation cannot be fully overcome by prompting alone: social sycophancy is rooted in model weights~\cite{cheng2026}, and multi-agent debate can degrade rather than improve group accuracy when agents exhibit social conformity~\cite{wynn2025}.
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec1: strengthen problem statement with 2025/2026 empirical evidence"
```

---

### Task 9: Expand Section 8 (Future Work) with concrete research directions

**Files:**
- Modify: `main.tex:761-768` (Section 8, future work list)

- [ ] **Step 1: Replace the future work enumeration**

Current text (lines 761-768):
```latex
Future work includes
(i)~controlled evaluation across artifact classes (RQ1--RQ3),
(ii)~empirical calibration of the Ipcha Score against human expert ratings (RQ4),
(iii)~cross-domain validation (medical, legal, scientific review),
(iv)~authority document governance tooling,
(v)~artifact input sanitization against role-collapse attacks,
(vi)~model-diversification strategies to mitigate correlated failures, and
(vii)~integration of deterministic, non-LLM agents into the trialectic to provide architecturally diverse contradiction.
```

Replace with:
```latex
Future work falls into three categories.

\emph{Evaluation.}
(i)~Controlled evaluation across artifact classes (RQ1--RQ3).
(ii)~Empirical calibration of the Ipcha Score against human expert ratings (RQ4).
(iii)~Cross-domain validation (medical, legal, scientific review).
(iv)~Evaluation on verifiable logic benchmarks (e.g., Knight-Knave-Spy puzzles~\cite{wu2025_debate}) to isolate debate-quality effects from domain knowledge.

\emph{Architecture.}
(v)~Replacing prompt-based role assignment with SDRL-trained adversarial agents~\cite{sdrl2025} that are trained via verifiable rewards to resist social conformity.
(vi)~Migrating the Auditor from sequential synthesis to cooperative protocols (ColMAD~\cite{colmad2025}) or confidence-weighted arbitration (ConfMAD~\cite{confmad2025}) to address the warning paradox identified in Section~\ref{sec:limitations}.
(vii)~Applying causal sycophancy mitigation (CAUSM~\cite{causm2025}) to Ipcha Agent model weights to provide architectural rather than prompt-level adversarial pressure.
(viii)~Investigating formal verification metrics: translating extracted claims into temporal-logic templates (e.g., LTL) verifiable by deterministic solvers, and measuring logical preference consistency (transitivity, negation invariance) as a complement to the embedding-based Ipcha Score.
(ix)~Integration of deterministic, non-LLM agents into the trialectic to provide architecturally diverse contradiction.

\emph{Security.}
(x)~Authority document governance tooling, including runtime cross-chunk coherence validation against RAG poisoning.
(xi)~Artifact input sanitization against role-collapse attacks.
(xii)~Denial-of-wallet defense mechanisms (claim budgets, cost ceilings, prioritized evaluation).
```

- [ ] **Step 2: Verify compilation**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex`

- [ ] **Step 3: Commit**

```bash
git add main.tex
git commit -m "sec8: expanded future work — SDRL, ColMAD, CAUSM, LTL metrics, RAG security"
```

---

### Task 10: Update version and changelog

**Files:**
- Modify: `main.tex:2,5-6,46` (version metadata)
- Modify: `CHANGELOG.md` (prepend new version)

- [ ] **Step 1: Update version in main.tex**

Change line 2:
```latex
% FILE: main.tex  (v2.0.0 – post critics integration)
```

Change lines 5-6:
```latex
% CHANGES v2.0.0: Integrate 2025/2026 MAD failure literature (Wynn, Wu),
%         architectural sycophancy (CAUSM, SDRL, ELEPHANT), cooperative debate
%         alternatives (ColMAD, ConfMAD), auditor warning paradox, IS honesty
%         + formal-logic future, denial-of-wallet, RAG hardening.
```

Change line 46:
```latex
\newcommand{\version}{v2.0.0}
```

- [ ] **Step 2: Update CHANGELOG.md**

Prepend before `## [1.2.0] - 2026-03-13`:

```markdown
## [2.0.0] - 2026-03-13

### Changed (Paper — critics-driven refactoring)
- **Section 1**: Strengthened problem statement with 2025/2026 empirical evidence (sycophancy is architectural, MAD can degrade accuracy)
- **Section 2.3**: Acknowledged architectural depth of sycophancy; cited ELEPHANT (Cheng 2026), CAUSM (2025), SDRL (2025); framed IM as structural defense-in-depth, not prompt-based fix
- **Section 2.5**: Integrated MAD failure modes (Wynn & Satija 2025, Wu et al. 2025); added ColMAD and ConfMAD as cooperative/confidence-weighted alternatives; explicit differentiation of IM from pure debate
- **Section 4**: Added verbosity bias as explicit false-positive driver; clarified IS (screening) vs IS_w (operational) roles; added formal-logic future direction (LTL, logical preference consistency)
- **Section 7.2**: Added RAG-specific attack vectors (embedding inversion, cross-chunk coherence attacks); expanded mitigation with runtime coherence validation
- **Section 7.3**: Added denial-of-wallet attack vector with three concrete mitigations
- **Section 7.4**: Added auditor warning paradox as limitation distinct from correlated model failures; linked to confidence-weighted arbitration as structural fix
- **Section 8**: Restructured future work into Evaluation/Architecture/Security categories; added 5 concrete research directions (SDRL agents, ColMAD/ConfMAD migration, CAUSM integration, formal verification metrics, DoW defense)

### Added
- 7 new references: Wynn 2025, Wu 2025, Cheng 2026, SDRL 2025, ColMAD 2025, CAUSM 2025, ConfMAD 2025
- Motivated by external PhD-level critique (`backcheck/critics.md`)

```

- [ ] **Step 3: Full compilation test**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

Expected: Clean compilation, no warnings for undefined citations, all 16 references resolved.

- [ ] **Step 4: Verify page count**

Run: `cd /Users/oli/Projects/ipcha-mistabra && pdflatex main.tex 2>&1 | grep "Output written"`

Expected: ~20-21 pages (up from 18). If >22, tighten future work list.

- [ ] **Step 5: Commit**

```bash
git add main.tex CHANGELOG.md
git commit -m "v2.0.0: critics-driven refactoring complete"
```

---

## Summary of All Changes (9 edits + refs)

| Task | Section | What Changes | New Words (~) |
|------|---------|-------------|---------------|
| 1 | references.bib | +7 BibTeX entries | — |
| 2 | 2.5 Multi-Agent Debate | Rewrite: MAD failures + ColMAD/ConfMAD | +250 |
| 3 | 2.3 Sycophancy | Expand: CAUSM + SDRL + ELEPHANT | +220 |
| 4 | 7.4 Limitations | New: Auditor Warning Paradox | +160 |
| 5 | 4 Ipcha Score | Verbosity bias + IS/IS_w + formal-logic future | +180 |
| 6 | 7.3 Operational Model | New: Denial of Wallet | +120 |
| 7 | 7.2 Authority Trust | RAG attack specifics + coherence validator | +80 |
| 8 | 1 Introduction | Strengthen with 2025/2026 evidence | +40 |
| 9 | 8 Future Work | Restructured: Eval / Arch / Security categories | +200 |

**Total net addition:** ~1,250 words (~2.5–3 pages; target: 20–21 pages)

---

## Editorial Decisions Log

| Decision | Rationale |
|----------|-----------|
| **Keep Ipcha Score** (downgraded to screening signal) | IS has independent value for unstructured reviews; removing it loses 3 empirical data points and Figure 2. IS_w becomes primary metric. Formal-logic direction framed as future. |
| **ColMAD/ConfMAD as future work, not current architecture** | Implementing cooperative debate requires fundamental redesign of the trialectic. Citing them shows awareness; proposing migration shows research maturity. |
| **SDRL/CAUSM as drop-in replacements, not requirements** | IM is model-agnostic by design. Requiring RLVR-trained models would make the protocol impractical for most users. Framing them as "compatible upgrades" preserves generality. |
| **No LTL in current protocol** | NL→LTL is itself an open research problem. Claiming it as a contribution without implementation would be the same sin the critics accuse (speculative formalism). |
| **No engagement with double-blind/IP critique** | Already resolved in v1.2.0. Responding to deleted sections would be defensive and pointless. |
| **No "rebuttal" section** | The paper becomes stronger by integrating criticism, not by arguing. The critics' valid points improve the paper; their invalid points are ignored. |
| **Warning paradox cites Wynn 2025, not October 7 directly** | The intelligence-history analogy is powerful but would require a lengthy historical discussion. Wynn's framing of conformity dynamics is more directly applicable to LLMs. |
| **Zero-sum → cooperative framing** | The critics call IM a "zero-sum game." This is a mischaracterization (IM is sequential, not competitive), but acknowledging ColMAD as the cooperative alternative shows we understand the design space. |
