---
name: taskflow-model
description: Use when task requirements and input/output artifacts must be turned into a minimal working prediction, optimization, retrieval or analysis pipeline, before choosing module methods.
---

# Design the smallest complete model

Read the sibling `../taskflow-workflow/references/decision-policy.md` first. Use the task brief and actual files as authority. Here "model" means the whole input-to-output solution; do not assume it requires machine learning, a web app or a particular solver.

Within the approved planning scope, produce a short `.taskflow/model-plan.md`:

- **Purpose and evidence:** task type(s), requirement IDs/sources, intended decision, mandatory conditions, stated objective and priority rules. Ask the user about unresolved conflicts; do not invent a ranking to proceed.
- **Input/output contract:** fields, IDs, granularity, units, allowed values, missing/invalid behavior, output format, status and limits. Identify which information exists at the real decision/prediction time. Inspect supplied goal/sample-output files; keep illustrative or reserved final answers out of fitting/selection, do not hard-code sample values or infer a scoring rule from an illustration. Legitimate historical training labels remain usable.
- **Minimum module graph:** each necessary module's responsibility, input/output semantics, dependencies, simplest adequate method, why it fits and a key assumption. Consider a simpler alternative. Use the actual data, labels, problem structure, dependencies and runtime to choose; consult [method selection](references/method-selection.md) when needed.
- **Checks and comparison:** runnable input-to-output case; independent validity checks or tiny known-answer cases; task-appropriate quality metrics and resource limits. For prediction, keep training, selection and final evaluation roles separate and choose time/group splits when required by use. For optimization, check constraints/objective separately from claims of optimality.
- **Implementation batch proposal:** scope/contracts, owners, execution budget, risks, acceptance checks and the point at which user discussion resumes. Explain it in Korean and obtain approval before implementation outside prior approval.

Choose minimum complexity, not a deliberately weak algorithm or a fixed "one method per module" rule. A specialized exact solver can be the simplest adequate baseline. A module is optional unless the requirements need its responsibility; combine or remove unnecessary boundaries. Publish stable contracts early so independent backend modules and a required frontend can proceed in parallel under `../taskflow-parallel/SKILL.md`.

Build the approved baseline through real input and output before optional complexity. Report working execution, validity and quality separately. Preserve a reproducible baseline snapshot and its evidence; do not hide failed requirements with defaults or fabricated predictions. Use `../taskflow-verify/SKILL.md` for integration checks. A baseline is not accepted merely because the implementer says it runs; establish its use under the user's recorded approval. Then use `../taskflow-improve/SKILL.md` for bounded improvement, including an initial weakness analysis.
