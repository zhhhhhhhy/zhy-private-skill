# Research-tree schema

## Contents

- Node identity
- Required common fields
- Type-specific fields
- Status rules
- Edge semantics

## Node identity

Assign a stable ID and keep it for the lifetime of the tree:

| Type | Prefix | Purpose |
|---|---|---|
| Root question | `ROOT-` | Define the research problem and scope |
| Question | `Q-` | Represent one unresolved decision |
| Observation | `O-` | Record an observed phenomenon with provenance |
| Hypothesis | `H-` | Explain an observation with a falsifiable claim |
| Experiment | `E-` | Test one or more hypotheses |
| Result | `R-` | Record the outcome of an experiment |
| Insight | `I-` | State a scoped regularity or mechanism |
| Contribution | `C-` | Trace a paper claim to confirmed evidence |

Use one checkable assertion per node. Connect nodes by IDs instead of relying on visual nesting.

## Required common fields

```yaml
id:
type:
title:
parent_ids: []
created_at:
updated_at:
status:
summary:
evidence_ids: []
assumptions: []
caveats: []
next_action:
```

## Type-specific fields

### Question

```yaml
question:
scope:
why_it_matters:
resolution_rule:
```

### Observation

```yaml
statement:
source:
setting:
measurement:
replication_status:
label_source: gold | teacher | weak | oracle | heuristic | author_reported | unknown
```

Do not call an intuition an observation. Use `author_reported` or `unknown` until evidence is
attached.

### Hypothesis

```yaml
if_condition:
mechanism:
then_prediction:
rival_hypothesis_ids: []
falsifier:
scope:
```

Write: “If A is a primary cause under scope S, then intervention B should change outcome C relative
to control D.” Avoid hypotheses that can explain every possible result.

### Experiment

Use the complete fields in `experiment-and-evidence.md`.

### Result

```yaml
experiment_id:
observed_values:
uncertainty:
quality_checks:
anomalies:
prediction_match: supports | refutes | mixed | inconclusive
artifact_refs: []
```

### Insight

```yaml
statement:
supported_by: []
weakened_alternatives: []
scope:
confidence: low | medium | high
boundary_conditions: []
```

### Contribution

```yaml
claim:
insight_ids: []
evidence_chain: []
novelty_basis:
limitations:
```

## Status rules

- Question: `active | resolved | paused`
- Observation: `reported | checked | disputed`
- Hypothesis: `proposed | active | verified | rejected | inconclusive | paused`
- Experiment: `planned | running | completed | blocked | invalid`
- Result: `recorded | checked | disputed`
- Insight: `candidate | confirmed | retired`
- Contribution: `candidate | supported | withdrawn`

Use `verified` to mean supported within the tested scope, not universally proven. Reject a
hypothesis only when a predeclared falsifier is met by valid evidence. Use `inconclusive` for low
power, failed controls, mixed predictions, or non-identifying experiments.

## Edge semantics

Use only explicit relationships:

```text
decomposes | motivates | explains | rivals | tests | produces
supports | refutes | qualifies | reveals | contributes_to
```

Never overwrite a rejected branch. Add a status transition and preserve its evidence chain.
