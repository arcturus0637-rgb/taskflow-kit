---
name: taskflow-brief
description: Use when an unfamiliar assignment, long specification or revised requirement is hard to understand, before implementation decisions depend on its meaning.
---

# Fast, grounded task brief

Read `../taskflow-workflow/references/decision-policy.md` and honor the approved discovery scope. Produce an early brief the user can scan in one or two minutes. Keep the assignment's terminology and exact file/output constraints. Read source documents, tables and figures that determine the requirements; do not replace unseen content with guesses.

The brief contains:
- **Goal:** who needs what result and what decision or action it enables.
- **Required output:** executable/file/service/analysis, format, entry point and submission rules actually stated.
- **Requirement table:** stable ID, requirement, category (required/optional/example), source location, observable acceptance check.
- **Inputs and constraints:** available data, schemas/units, preserved source fields, tools, dependencies, time and resource limits.
- **Improvement criteria:** actual task objectives, mandatory eligibility conditions and stated priority/tie-break rules with sources. Separate operating correctness, validity and quality. Where competing priorities remain unresolved, ask the user before dependent choices; do not invent weights.
- **Unknowns:** distinguish absent information, conflicting instructions and your assumptions. Ask only questions that materially block the next decision; continue independent work.
- **First complete result:** smallest path that meets the core requirement; next eligible tasks and the largest current risk.

Preserve negative requirements such as "do not change input files" and hidden/edge inputs explicitly mentioned. An illustrative number is not a fixed target; a suggested interface or user-proposed method is not automatically a mandatory product or established fact. Do not invent evaluation weights or predict the hidden task. For computational pipelines, hand off input/output artifacts and requirements to `../taskflow-model/SKILL.md` rather than choose methods from the topic name alone.

For changing requirements, retain stable IDs, record the new source, identify affected tasks/contracts/checks, and revise only impacted decisions. The user should be able to trace a disputed summary item back to the original text.

If decomposition or domain boundaries remain unclear, consult the pinned Matt Pocock references listed under `docs/SOURCES.ko.md` in the runtime kit. Borrow the relevant reasoning, not its issue-tracker publishing, mandatory approval or tool-specific workflow.
