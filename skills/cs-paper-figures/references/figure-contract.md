# Figure Contract

## Input

Use JSON with `schema_version: cs-paper-figure-request-v1`.

Required for every request:

- `artifact_id`: lowercase letters, digits, `_` or `-`;
- `venue`: target venue or `template-derived`;
- `figure_type`: `selection_gap_accounting`, `risk_coverage`,
  `cross_dataset_transfer`, or `decision_layer_schematic`;
- `source_kind`: `empirical`, `diagnostic`, or `conceptual`;
- `split_role`: one value or list from `train`, `validation`, `test`,
  `frozen_heldout`, `oracle_diagnostic`, `hard_slice`, `not_applicable`;
- `label_class`: `gold`, `teacher`, `weak`, `oracle`, `heuristic`,
  `project_adjudicated`, `mixed`, or `not_applicable`;
- `label_source`: precise free-text provenance;
- `oracle_status`: `none`, `diagnostic_only`, or `leaky`;
- `caption_claim`: the interpretation the figure supports;
- `caveats`: JSON list;
- `output_dir`: output directory, relative to the request or absolute.

Empirical and diagnostic requests also require:

- non-empty `source_data`, each with `path`, `sha256`, and optional
  `split_role`/`role`;
- positive `denominator` (number or non-empty map of surface to number);
- non-empty `metrics` list.

When plot-ready input is derived from an upstream result, add optional
`data_transformations`, each with `path`, `sha256`, and optional `role`, so the
raw-to-plot transformation remains independently reproducible.

Conceptual requests may use empty `source_data`, but require a non-empty
`claim_boundary` and `split_role`, `label_class` set to `not_applicable`.

Optional `planned_outputs` paths participate in overwrite checks.

For a cross-dataset figure whose surfaces genuinely have different split or
label provenance, set `label_class: mixed`, `surface_role_separation: true`,
and provide `surface_provenance`. Each surface entry must contain
`split_role`, `label_class`, `label_source`, and `oracle_status`. This exception
is valid only for `cross_dataset_transfer`; the caption/caveats must state that
the rows are not interchangeable leaderboard test sets. The
`surface_provenance` keys must exactly match the per-surface `denominator` keys.

## Output Package

Write `figure_package.json` with:

- request path/hash and normalized source-data paths/hashes;
- normalized upstream data-transformation paths/hashes, when present;
- transformation script path/hash;
- generated artifacts with kind/path/hash;
- `claim_trace` containing caption claim, metrics, and source paths;
- limitations copied from caveats;
- validation status, errors, and warnings;
- execution counters fixed to zero for API/model/GPU/download/cost.

## Fail-Closed Conditions

Reject missing or mismatched hashes, invalid denominators, missing label
provenance, unseparated mixed ReportFill split roles, gold claims whose source names reveal
teacher/weak/oracle/heuristic origin, oracle labels declared non-oracle, strong
overclaim language without caveats, and existing outputs without `--overwrite`.
