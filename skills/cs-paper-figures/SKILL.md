---
name: cs-paper-figures
description: Create and audit publication-ready figures for computer-science, AI, ML, NLP, QA, RAG, and AAAI-style papers. Use for selection-gap accounting, risk/accuracy-coverage curves, cross-dataset transfer plots, ablations, decision-layer or evidence-candidate diagrams, LaTeX/TikZ integration, 计算机论文画图, 模型架构图, 实验结果图, 消融图, 机制图, AAAI论文配图. Do not use for decorative slide art or untraceable plots.
---

# CS Paper Figures

Create reproducible, claim-bounded computer-science paper figures. Keep
`academic-paper` responsible for narrative, caption wording, numbering, and
placement; own figure selection, generation, provenance, venue fit, and QA.

## Workflow

1. Read the nearest `AGENTS.md` and the target paper's source-of-truth files.
2. Resolve the venue before styling. Read `references/venue-profiles.md`.
3. Classify the artifact as empirical, diagnostic, or conceptual. Select a
   figure family using `references/ml-figure-catalog.md`.
4. Create `figure_request.json` using `references/figure-contract.md`.
5. For ReportFill work, also read `references/reportfill-profile.md` and keep
   discovery, heldout, oracle, and hard-slice surfaces separate.
6. Run `scripts/audit_figure_contract.py` before generating an empirical or
   diagnostic figure. Fail closed on provenance, denominator, label, oracle,
   split, or overclaim errors.
7. Generate the figure:
   - selection-gap or transfer accounting: `scripts/plot_selection_gap.py`;
   - risk/accuracy-coverage: `scripts/plot_risk_coverage.py`;
   - decision/evidence diagrams: adapt the templates under `assets/templates/`.
8. Run `scripts/check_latex_figure.py` for TikZ/LaTeX sources. Compile only
   when a local TeX tool already exists; never download one.
9. Deliver editable source, vector output, PNG preview, and
   `figure_package.json`. State any skipped render check explicitly.

## Venue-First Rules

- Inspect the actual paper class/style and surrounding figure usage.
- Use the paper's `\columnwidth` or `\textwidth`; do not force APA dimensions.
- Prefer PDF/SVG for plots and TikZ/LaTeX for schematics. Keep SVG text as text.
- Use restrained, colorblind-safe colors plus line/marker redundancy.
- Do not add chart titles when the venue expects the caption to carry the title.
- Keep labels readable at final two-column size and avoid dual axes, 3D, pie
  charts, rainbow maps, and unexplained truncated axes.

## Integrity Rules

- Never copy numbers from prose when a machine-readable source exists.
- Never relabel teacher, weak, heuristic, oracle, or project-adjudicated labels
  as independent human gold.
- Never present oracle diagnostics as deployable methods.
- Never mix non-equivalent evaluation surfaces into a leaderboard.
- Require a claim boundary for conceptual figures and caveats for strong causal,
  generalization, SOTA, or "solves" language.
- Refuse to overwrite existing artifacts unless the user passes `--overwrite`.

## Safety and Cost

Use local CPU-only plotting and static checks. Do not call a VLM, LLM judge,
OpenRouter, image-generation API, remote renderer, model, scorer, or GPU. The V1
execution record must remain: API calls `0`, model calls `0`, GPU commands `0`,
downloads `0`, external cost USD `0`.

## Outputs

Return:

- the validated `figure_request.json`;
- source data paths and hashes;
- any raw-to-plot data-transformation paths and hashes;
- editable plot/TikZ source;
- PDF and SVG for generated plots plus PNG preview;
- `figure_package.json` with transformation hash, claim trace, limitations,
  validation state, and zero-cost execution record.
