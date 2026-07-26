# Compact RAG example

Use this only to demonstrate structure, not as a conclusion about every small model.

```text
ROOT-001
Question: Why does a small model fail on sufficient-context RAG?

Q-001
Question: Is failure caused by missing evidence or by selecting among sufficient candidates?

O-001
Observation: Correct evidence appears in the provided context, but answer accuracy remains low.
Status: reported

H-001
Hypothesis: Retrieval insufficiency is the primary cause.
Prediction: Supplying oracle-relevant evidence should substantially close the accuracy gap.
Rival: H-002

H-002
Hypothesis: Candidate selection is the primary cause once evidence is sufficient.
Prediction: Adding the correct candidate without reducing distractor competition will yield only
limited improvement; reducing selection difficulty while holding evidence fixed will improve more.
Rival: H-001

E-001
Purpose: Distinguish evidence insufficiency from candidate-selection failure.
Intervention: Hold model, prompt, and question set fixed; vary evidence sufficiency and candidate
competition independently.
Metrics: answer accuracy, candidate coverage, selection accuracy, uncertainty across seeds/items.
Support H-001: improvement tracks evidence sufficiency after competition is controlled.
Support H-002: performance remains low under sufficient evidence and improves when competition is
reduced with evidence held fixed.
Inconclusive: the intervention changes context length or answer exposure in a confounded way.

R-001
Result: Not yet recorded.

I-001
Insight: Do not create until E-001 produces checked evidence.
```

After the result, update H-001 and H-002 separately. Preserve a rejected hypothesis and its
falsifying evidence. Do not jump from a metric difference to “selection is the mechanism” without
checking intervention validity and alternative explanations.

