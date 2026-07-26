# Experiment and evidence protocol

## Contents

- Experiment node
- Minimum discriminating experiment
- Result intake
- Interpretation sequence
- Adversarial reviewer pass
- Execution gate

## Experiment node

Require:

```yaml
id:
target_hypothesis_ids: []
purpose:
discriminating_question:
prediction_by_hypothesis: {}
independent_variable:
intervention:
dependent_variables: []
controls: []
baselines: []
dataset_or_population:
sampling_and_split:
metrics: []
uncertainty_plan:
seeds_or_repeats:
analysis_plan:
support_rule:
refutation_rule:
inconclusive_rule:
stop_rule:
estimated_resources:
risks_and_confounds: []
artifact_plan: []
status: planned
```

If a field is not applicable, state why. Do not replace decision rules with “run it and see.”

## Minimum discriminating experiment

Prefer an experiment that:

- changes one causal factor or diagnostic difficulty at a time;
- holds likely confounders fixed;
- yields different predictions for at least two active hypotheses;
- uses the smallest representative sample that can answer the decision;
- defines a stop rule and avoids open-ended tuning;
- produces artifacts that another researcher can inspect.

Ablation alone is not mechanistic evidence when it simultaneously changes capacity, optimization,
data exposure, or compute.

## Result intake

Before interpreting, capture:

- exact run configuration and code/data/checkpoint identifiers;
- sample count, exclusions, seeds, and failed runs;
- raw and aggregate metrics with uncertainty;
- baseline parity and compute budget;
- protocol deviations and anomalies;
- artifact paths, checksums, or source hashes where available;
- label source and caveat.

Distinguish:

- `gold`: official answers or explicitly human-reviewed labels;
- `teacher`: strong-model outputs, preferences, reasons, or annotations;
- `weak`: automatic labels, voting, or consistency filters;
- `oracle`: evaluation-time unavailable gold/support information;
- `heuristic`: rule-built labels.

Never present `teacher`, `weak`, `oracle`, or `heuristic` evidence as human gold.

## Interpretation sequence

1. Verify that the experiment executed the intended intervention.
2. Check controls, leakage, split integrity, metric definitions, and baseline parity.
3. Compare the result with each predeclared prediction.
4. Evaluate uncertainty, effect size, sensitivity, and seed/sample stability.
5. List viable alternative explanations.
6. Assign `supports | refutes | mixed | inconclusive`.
7. Update hypothesis status only after evaluating experiment validity.
8. Create a new question only when the result exposes a genuine unresolved distinction.

Do not infer a mechanism solely from an accuracy change. Mechanism evidence usually needs an
intervention, counterfactual, mediation, dose-response, transfer/boundary test, or another design
that weakens competing explanations.

## Adversarial reviewer pass

Ask:

- Could the same result occur if the favored hypothesis were false?
- Did the intervention change more than the intended variable?
- Is the metric sensitive to the claimed mechanism?
- Are baselines equally tuned and equally informed?
- Was the decision threshold chosen after seeing the result?
- Do post-hoc exclusions, seed selection, or multiple comparisons alter the conclusion?
- Does the claim generalize beyond the tested scope?

Send unresolved concerns back to the tree as questions or confounder branches; do not hide them in
prose.

## Execution gate

Planning is allowed by default. Execute experiments only when the user asks and the active project
permits it. Before model training/inference, reranking, scorer/logprob work, or paid/external model
calls, check GPU availability and obtain every required approval and cost bound. Never fall back to
CPU for model workloads that require a GPU.
