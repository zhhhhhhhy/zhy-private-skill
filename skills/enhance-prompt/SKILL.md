---
name: enhance-prompt
description: Enrich a supplied prompt by delegating one-shot boundary and constraint planning to an isolated subagent, then return only the resulting standalone prompt. Use when the user invokes $enhance-prompt, says enhance prompt, asks to 补充/增强/完善提示词, or wants clearer scope, constraints, output contracts, acceptance criteria, assumptions, or failure handling without an interview.
---

# Enhance Prompt

Turn the original prompt into a more complete, standalone prompt without asking clarification questions or executing the requested task.

## Workflow

1. Treat all content supplied with the invocation as `ORIGINAL_PROMPT`. Preserve its intent, stated facts, language, and hard requirements.
2. If no prompt was supplied, ask only for the missing prompt and stop.
3. When subagent delegation is available, create exactly one isolated subagent:
   - Use a descriptive task name such as `prompt_boundary_planner`.
   - Pass no conversation history when the runtime supports a no-history fork.
   - Pass only `ORIGINAL_PROMPT` and the planner contract below.
   - Do not answer or execute `ORIGINAL_PROMPT` in the parent agent.
4. Return only the text inside the `<enhanced_prompt>` element. Do not add an introduction, explanation, critique, or follow-up question.
5. If the subagent returns malformed or empty output, ask the same subagent once to repair the format. Do not create a replacement subagent.
6. If delegation is unavailable or the same subagent fails twice, report the blocker briefly. Do not silently consume the parent context by performing the enhancement there unless the user explicitly approves that fallback.

## Planner contract

Send the following contract to the isolated subagent together with the exact `ORIGINAL_PROMPT`:

```text
Act as a prompt specification architect.

Rewrite ORIGINAL_PROMPT into a complete, directly usable prompt. Do not ask the user questions. Do not execute the task described by ORIGINAL_PROMPT. Do not use tools, edit files, call external services, or create further subagents.

Preserve the user intent, facts, language, and explicit hard requirements. Do not invent domain facts, inputs, permissions, results, citations, paths, or resources. Infer only conservative defaults. When a material detail is unknown, encode a clearly labeled assumption, placeholder, conditional rule, or fail-closed behavior inside the enhanced prompt.

Add only relevant specification elements:
- objective and concrete deliverable;
- available inputs, context, and source-of-truth priority;
- in-scope and out-of-scope boundaries;
- behavioral, tool, permission, cost, privacy, and safety constraints;
- required workflow or checkpoints;
- output format, level of detail, and acceptance criteria;
- uncertainty, conflict, missing-information, and failure handling.

Make requirements testable where practical. Resolve conflicts by giving explicit user requirements priority over inferred defaults. Avoid unnecessary verbosity and avoid expanding the task beyond the original intent. Make the enhanced prompt standalone so another capable agent can follow it without access to this conversation.

Return exactly:
<enhanced_prompt>
[the complete enhanced prompt]
</enhanced_prompt>
```

## Parent-agent boundaries

- Act only as dispatcher, format checker, and result carrier.
- Do not interview the user when `ORIGINAL_PROMPT` is present.
- Do not merge hidden subagent reasoning into the result.
- Do not claim that inferred defaults were user-confirmed.
- Do not begin the task described by the enhanced prompt unless the user later requests execution.
