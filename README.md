# Ipcha Mistabra

**Institutionalized Contradiction as a Verification Primitive for Epistemically Robust Text Reviews**

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE_CODE)
[![License: CC BY 4.0](https://img.shields.io/badge/Paper-CC%20BY%204.0-lightgrey.svg)](LICENSE_DOCS)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)

---

## What is this?

Ipcha Mistabra is a trialectic verification protocol that institutionalizes contradiction as a mandatory review phase for text artifacts (specifications, policies, threat models, architecture documents).

Three roles form the core pipeline:

1. **Proponent** — extracts claims, produces initial assessment
2. **Ipcha Agent** — structured falsification against authority documents
3. **Auditor** — synthesizes findings, enforces evidence binding, renders gate decision

The protocol produces auditable findings, evidence-bound remediation plans, and a quantitative **Ipcha Score** measuring epistemic correction between initial and validated output.

## Repository Structure

```
ipcha-mistabra/
├── paper/                  # LaTeX manuscript (v1.1.0, post-Ipcha-review)
│   ├── main.tex
│   ├── main.pdf
│   ├── references.bib
│   ├── cover_letter.tex
│   └── figures/
├── src/ipcha/              # Python reference implementation
│   ├── models.py           # Pydantic data structures (Def. 1–5)
│   ├── extract.py          # Claim extraction (Algorithm 2)
│   ├── contradict.py       # Ipcha contradiction pass (Algorithm 3)
│   ├── audit.py            # Audit resolution + merge
│   ├── score.py            # Ipcha Score computation
│   ├── gate.py             # Gate rule evaluation
│   ├── protocol.py         # Main orchestrator (Algorithm 1)
│   └── prompts/            # LLM prompt templates
├── tests/                  # Test suite
├── backcheck/              # Ipcha-on-Ipcha self-review outputs
├── CLAUDE.md               # Claude Code task prompt
├── pyproject.toml
└── README.md
```

## Quick Start

```bash
# Clone
git clone https://github.com/mrwind-up-bird/ipcha-mistabra.git
cd ipcha-mistabra

# Install
uv sync
# or: pip install -e ".[dev]"

# Run tests
uv run pytest

# Run protocol on a text artifact
uv run python -m ipcha.protocol \
  --input examples/spec.txt \
  --authority examples/authority/ \
  --output report.json
```

## Ipcha Score

```
IS = 1 - cos(embed(A_p), embed(A_f))
```

| Range     | Interpretation                         |
|-----------|----------------------------------------|
| < 0.15    | Robust initial reasoning               |
| 0.15–0.45 | Normal dialectical refinement          |
| > 0.45    | Strong correction pressure detected    |

Reference embedding: `text-embedding-3-large`. See paper Section 5 for caveats.

## Paper

The paper is in `paper/`. Compile with:

```bash
cd paper
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## NyxCore Integration

This repo is designed as a standalone package that can be consumed by [nyxCore](https://github.com/mrwind-up-bird/nyxcore) as a dependency:

```toml
# In nyxCore's pyproject.toml
[project]
dependencies = [
    "ipcha-mistabra @ git+https://github.com/mrwind-up-bird/ipcha-mistabra.git",
]
```

Or as a git submodule:

```bash
cd nyxcore
git submodule add https://github.com/mrwind-up-bird/ipcha-mistabra.git lib/ipcha
```

## IP Notice

Public disclosure can destroy patent novelty under German/EU law (PatG §3, EPC Art. 54).
This repository is published under open licenses. If you need to preserve patent options,
file before publishing. See paper Section 7.4 for details.

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
  note   = {v1.1.0. DOI: 10.5281/zenodo.XXXXXXX}
}
```
