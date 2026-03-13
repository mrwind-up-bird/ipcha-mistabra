# Ipcha Mistabra

**Institutionalized Contradiction as a Verification Primitive for Epistemically Robust Text Reviews**

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE_CODE)
[![License: CC BY 4.0](https://img.shields.io/badge/Paper-CC%20BY%204.0-lightgrey.svg)](LICENSE_DOCS)

---

## What is this?

Ipcha Mistabra is a trialectic verification protocol that institutionalizes contradiction as a mandatory review phase for text artifacts (specifications, policies, threat models, architecture documents).

Three roles form the core pipeline:

1. **Proponent** — extracts claims, produces initial assessment
2. **Ipcha Agent** — structured falsification against authority documents
3. **Auditor** — synthesizes findings, enforces evidence binding, renders gate decision

The protocol produces auditable findings, evidence-bound remediation plans, and a quantitative **Ipcha Score** measuring semantic displacement between initial and validated output.

## Repository Structure

```
ipcha-mistabra/
├── main.tex                    # Paper source (v1.2.0)
├── main.pdf                    # Compiled paper (14 pages)
├── references.bib              # Bibliography
├── paper/
│   ├── pilot-data/             # Raw pilot study outputs (workflow 746b1ec0)
│   └── v1.0.0/                 # Pre-review baseline (for IS computation)
├── backcheck/                  # Ipcha-on-Ipcha self-review
│   ├── claims.json             # 20 extracted claims
│   ├── findings.json           # 20 findings with counter-arguments
│   └── audit_report.md         # Gate decision: PASS
├── CLAUDE.md                   # Claude Code task prompt
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

## Paper

Compile with:

```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

Figures are rendered inline via TikZ — no external figure files required.

## Ipcha Score

```
IS = 1 - cos(embed(A_p), embed(A_f))
```

| Range     | Interpretation                         |
|-----------|----------------------------------------|
| < 0.15    | Robust initial reasoning               |
| 0.15–0.45 | Normal dialectical refinement          |
| > 0.45    | Strong correction pressure detected    |

Reference embedding: `text-embedding-3-large` (3072 dim). See paper Section 4 for failure modes.

### Empirical data points

| Comparison | IS | Band |
|---|---|---|
| Paper v1.0.0 → v1.1.0 | 0.099 | Low (false-negative: additive revision) |
| Pilot: Prepare → Results | 0.256 | Mid |
| Pilot: Spec → Arbitration | 0.356 | Mid-high |

## Pilot Case Study

The protocol was applied to a production design specification (Persona Evaluation v2), surfacing 12 findings:

- 3 critical (including 1 blocker)
- 5 high-severity
- 4 medium/low

Cost: **$0.20** | Time: **2.8 min** | Providers: Gemini 2.5 Pro + Kimi K2

Raw pilot data is in `paper/pilot-data/`.

## Backcheck (Ipcha-on-Ipcha)

The protocol was applied to its own paper. Results in `backcheck/`:

- **20 claims** extracted from `main.tex`
- **20 findings** with counter-arguments
- **Gate: PASS** (all high-severity findings resolved)
- **IS computed** between v1.0.0 and v1.1.0

## License

- **Code**: [MIT](LICENSE_CODE)
- **Paper/Docs**: [CC BY 4.0](LICENSE_DOCS)

## Citation

```bibtex
@misc{baer2026ipcha,
  author = {Baer, Oliver},
  title  = {Ipcha Mistabra: Institutionalized Contradiction as a
            Verification Primitive for Epistemically Robust Text Reviews},
  year   = {2026},
  url    = {https://github.com/mrwind-up-bird/ipcha-mistabra},
  note   = {v1.2.0}
}
```
