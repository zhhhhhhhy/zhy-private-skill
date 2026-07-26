# Operating workflow

## Contents

- Initialize the root
- Convert observations into competing hypotheses
- Prioritize the active frontier
- Design the minimum discriminating experiment
- Record a result and update the tree
- Distill insights and trace contributions
- Response cadence

## 1. Initialize the root

Turn the user’s topic into a bounded question:

```text
Why/when does phenomenon Y occur for population/model/data S under condition C?
```

Record what is in scope, what is out of scope, why the answer matters, and what observable outcome
would count as progress. Avoid embedding a preferred method in the root.

Split the root into three to five question branches that are:

- collectively useful but not claimed exhaustive;
- distinct enough to imply different experiments;
- ordered from diagnostic cause to mechanism and intervention;
- grounded in known observations rather than method brainstorming.

For system failures, useful first cuts include input/evidence sufficiency, representation or
utilization, inference, conflict handling, selection/decision, and evaluation artifact.

## 2. Convert observations into competing hypotheses

Require at least one observation before proposing hypotheses. For each observation:

1. propose a simple/null explanation;
2. propose one mechanism explanation;
3. propose one measurement, data, or confounding explanation when plausible;
4. state a prediction on which the explanations disagree.

Merge hypotheses that make the same observable prediction. Do not create branches merely by
renaming the same idea.

## 3. Prioritize the active frontier

Rank active hypotheses qualitatively on:

| Criterion | Question |
|---|---|
| Decision value | Would the result change the research direction? |
| Information gain | Does it distinguish serious alternatives? |
| Falsifiability | Can a feasible outcome refute it? |
| Feasibility | Is the required data/compute/time available? |
| Confounding risk | Can the effect be interpreted cleanly? |
| Contribution relevance | Would the answer support a meaningful scientific claim? |
| Dependency | Does another result need to come first? |

Use `high | medium | low` with one-sentence rationales. Avoid fake numerical precision. Select one
frontier node; keep the remainder visible as backlog.

## 4. Design the minimum discriminating experiment

Follow `experiment-and-evidence.md`. Prefer the cheapest experiment that separates at least two
hypotheses. Do not optimize a full system before identifying the bottleneck.

If no feasible experiment distinguishes the hypotheses, revise the hypotheses or collect a more
diagnostic observation.

## 5. Record a result without hindsight edits

Attach the result to the original prediction and decision rules. Record failed runs, excluded data,
seed variance, anomalies, and missing artifacts. Do not rewrite the hypothesis to match the result.

Classify the result as `supports`, `refutes`, `mixed`, or `inconclusive`. This relation updates the
hypothesis but does not automatically prove a mechanism.

## 6. Update the tree

- Supported prediction: strengthen the hypothesis within scope and test a rival or boundary.
- Refuted prediction: mark the hypothesis rejected only if the experiment is valid; open a branch
  explaining the refutation.
- Mixed result: split scope, population, or mechanism only when the split is evidenced.
- Inconclusive result: repair power, measurement, or controls before inventing a new method.

Log every transition with date, old status, new status, triggering result, and rationale.

## 7. Distill insights

Promote an insight to `confirmed` only when:

- its supporting results are checked;
- the claim names its tested scope;
- serious alternative explanations are weakened or explicitly retained;
- the evidence chain is reproducible from recorded artifacts;
- the language does not exceed the design’s causal strength.

Prefer “under S, changing B altered C while D was controlled” over “B is the reason.”

## 8. Trace paper contributions

Build each contribution as:

```text
Root question
  -> observation
  -> competing hypotheses
  -> discriminating experiment(s)
  -> checked result(s)
  -> confirmed insight
  -> scoped contribution
```

Do not use an unverified hypothesis, isolated metric gain, or unreviewed model judgment as a
contribution. A rejected hypothesis may support a negative-result contribution when the test is
strong, the scope matters, and the result is robust.

## Response cadence

Advance one decision layer per turn. Report the current node, tree delta, current interpretation,
one next action, its decision rule, and open questions. Expand multiple layers only when the user
explicitly requests a batch plan.
