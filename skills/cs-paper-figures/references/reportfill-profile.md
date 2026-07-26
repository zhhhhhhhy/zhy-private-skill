# ReportFill Profile

Read `AGENTS.md`, `docs/PROJECT_INDEX_20260617.md`, `plan.md`, and
`EXPERIMENT_RESULTS_REGISTRY.md` before paper-facing work.

## Surface Mapping

- T7 core167 OOF and MuSiQue dev/discovery surfaces: discovery/internal.
- MuSiQue heldout100 full context: frozen public heldout.
- Support-only or official-support layouts: oracle diagnostic.
- 35/33/40-case selection-gap subsets: hard slices for probes/case studies.

Never combine these roles as interchangeable test rows. A cross-dataset
transfer figure may show different roles only when it uses explicit separated
surface provenance and caveats; it must not sort them as one leaderboard. Keep
denominators and candidate-source/fixed-menu conditions visible.

## Claim Boundaries

- Frame the paper as sufficient-context QA and evidence-conditioned selection
  failure, not a new benchmark or leaderboard.
- Treat current cross-dataset selector transfer as negative or partial unless a
  frozen gate says otherwise.
- Keep teacher outputs `teacher`, internal-agent labels caveated, oracle support
  diagnostic, and project-adjudicated labels named precisely.
- Reuse B116 and B117 builders/tests as golden examples; do not rewrite their
  active paper outputs while developing this skill.
