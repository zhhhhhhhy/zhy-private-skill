# Persistence contract

## Contents

- When to persist
- Files
- Canonical JSON
- Markdown view
- Decision log
- Experiment records
- Manifest

## When to persist

If the user supplies a project root or asks to create/save/manage the tree, keep the tree inside
that active project. Otherwise return the tree delta in chat and ask about persistence only when it
would materially help.

Never place one project’s tree in another project or connect projects through paths, links,
imports, environments, checkpoints, or result files.

## Files

Use:

```text
research-tree/
├── research-tree.json
├── research-tree.md
├── decision-log.md
├── manifest.json
└── experiments/
    └── E-xxx.md
```

Treat `research-tree.json` as the canonical state. Treat Markdown as the human-readable view. Patch
existing files; never erase rejected nodes or prior decisions.

## Canonical JSON

```json
{
  "tree_id": "string",
  "root_id": "ROOT-001",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "scope": {},
  "nodes": [],
  "edges": [],
  "active_frontier": [],
  "next_action": {},
  "open_questions": []
}
```

Keep node and edge fields consistent with `research-tree-schema.md`. Use relative artifact paths
inside the project.

## Markdown view

Render:

```markdown
# Research Tree

## Root
- Question:
- Scope:
- Status:

## Active Frontier
### H-xxx — title
- Observation:
- Hypothesis:
- Prediction:
- Next experiment:
- Decision rule:
- Status:

## Confirmed Insights

## Rejected Hypotheses

## Candidate Contributions

## Open Questions
```

Use symbols only as a view aid:

- 🟡 active/proposed;
- 🟢 verified/confirmed;
- 🔴 rejected;
- ⚪ inconclusive/paused.

The text status is authoritative.

## Decision log

Append one entry for every material change:

```text
timestamp
operation
affected_node_ids
old_status -> new_status
evidence/result IDs
rationale
next decision
```

Correct mistakes by appending a correction; do not rewrite history silently.

## Experiment records

Create one `experiments/E-xxx.md` per planned experiment. Include the predeclared prediction and
decision rules before results. After execution, append configuration, metrics, uncertainty,
artifacts, deviations, interpretation, and resulting tree transitions.

## Manifest

Record:

```json
{
  "tree_id": "string",
  "project_root": ".",
  "inputs": [],
  "node_counts": {},
  "active_frontier_count": 0,
  "label_sources": [],
  "label_caveats": [],
  "external_api_calls": [],
  "cost_usd": 0,
  "files": {},
  "source_hashes": {}
}
```

Do not store secrets or full private source contents in the manifest.
