# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] - 2026-03-13

### Changed (Paper — scholarly revision)
- Removed Executive Summary (collapsed into abstract)
- Removed IP/Zenodo boilerplate (Sections 6.3, 6.4)
- Removed Appendices B–D (Dockerfile, Zenodo metadata, artifact manifest)
- Replaced external PDF figures with inline TikZ (Figure 1: architecture, Figure 2: IS bands with empirical data points)
- Tightened title to two-line format (removed "IP-Aware Publication" subtitle)
- Fixed affiliation: "nyxCore Systems Research Division" → "nyxCore Research Division"

### Added
- `references.bib` with 9 bibliography entries (resolves all [?] citations)
- Three empirical IS data points plotted in Figure 2 (IS=0.099, 0.256, 0.356)

### Fixed
- All unresolved `[?]` citations now compile cleanly

## [1.1.1] - 2026-03-13

### Fixed
- **F014**: Finding count mismatch — abstract and observations updated to "3 critical (incl. 1 blocker), 5 high, 4 medium/low (12 total)" matching pilot data

### Added
- `backcheck/` directory with Ipcha-on-Ipcha self-review outputs:
  - `claims.json` (20 extracted claims)
  - `findings.json` (20 findings with counter-arguments)
  - `audit_report.md` (gate decision: PASS, F1–F9 diff, IS computation)
- `paper/v1.0.0/` baseline for IS computation

## [1.1.0] - 2026-03-13

### Changed (Paper — post-Ipcha self-review)
- **F1**: Refined novelty claim from absolute to gap characterization; added feature comparison table (Table 1)
- **F2**: Ipcha Score fully specified: fixed embedding model (text-embedding-3-large), documented false-positive/negative failure modes, introduced finding-weighted variant IS_w
- **F3**: Removed illustrative pseudo-data benchmarks; replaced with hypothesized direction-of-effect table
- **F4**: Added correlated model failures as explicit core limitation with mitigations
- **F5**: Softened domain-agnosticity from claim to design goal
- **F6**: Added detailed subfunctions (Algorithm 2: ExtractClaims, Algorithm 3: IpchaContradict) and prompt templates (Appendix C)
- **F7**: New subsection "What Makes This a Protocol, Not a Prompt Chain" with three differentiation criteria
- **F8**: Softened fault-tolerance analogy ("inspired by", not formal equivalence)
- **F9**: Expanded Related Work from 0.5 to ~2 pages (Fagan, CAI, SPARROW, Debate, ATLAS, Red-Teaming)

### Added
- CLAUDE.md task prompt for Claude Code backcheck + implementation

## [1.0.0] - 2026-03-13

### Added
- Initial IMRaD manuscript (English, article class)
- Formal definitions (Claim, Assumption, Evidence, Finding, Gate Rule)
- Top-level pseudocode (Algorithm 1)
- Ipcha Score definition (Equation 1)
- Evaluation design with statistical analysis plan
- IP constraints discussion (DE/EU)
- Appendices: artifact manifest, repro commands, Zenodo metadata snippets
- Cover letter template
