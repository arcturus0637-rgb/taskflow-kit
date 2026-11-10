---
name: taskflow-improve
description: Use after a working baseline exists to diagnose weaknesses, compare bounded method or architecture experiments, discuss candidate adoption and reassess each accepted model.
---

# Improve from evidence and reassess the accepted model

Read `../taskflow-workflow/references/decision-policy.md`. Improvement means better satisfaction of the task's actual guidelines and requirements under their stated priorities. Ask the user when priorities remain unresolved. Do not optimize an invented metric or equate more modules/methods with improvement. Use [experiment records](references/experiment-record.md) for the small durable record; it is not an automated execution/approval service.

## Start from an accepted, reproducible result

Identify the baseline/current accepted version, actual source/data/config fingerprints, requirements/criteria revision, contract versions, execution limits and evidence. Preserve a runnable snapshot or reproduction/rollback path. Keep candidate edits separate from it. If it fails a mandatory condition, report the defect and prioritize a corrective batch, not a higher score that hides the failure.

Within approved analysis scope, diagnose errors by case/subgroup, constraint violations, runtime/memory profile and data/assumption gaps. Distinguish measured bottlenecks from hypotheses. Ask whether the limitation is in the objective, data, formulation, a module, its connections or the UI's interpretation. Propose a bounded experiment batch with expected benefits, possible regressions, owners/scopes, fair comparisons, cost and stopping rules; discuss and obtain approval before dependent execution.

## Experiment inside the approved batch

- Consider method replacement, multiple candidate methods in parallel, hybrid methods, module addition/removal/simplification or dependency-preserving order changes. Make changes attributable where useful, then test plausible interactions; do not exhaust every combination. Reordering cannot use unavailable future information or bypass validation/required responsibilities.
- Use the same actual task, compatible input/criteria/contract versions and comparable resource budgets. Include preprocessing, routing, candidate selection and combination costs in end-to-end measurements. Separate repeatable execution/validity checks from quality evidence. Where stochastic, report variation using suitable repeated runs rather than one favorable seed. Keep final evaluation separate from repeated selection; do not query hidden/final tests to guide iterative choices.
- Give each candidate a stable ID/base version, falsifiable hypothesis, changed modules/methods, expected gain/regression, approved scope/budget, measured evidence and status. Prefer experiments tied to a demonstrated failure or bottleneck; retain some approved exploration for different structures when justified. A simpler or unchanged model is a legitimate winner.
- Parallelize independent modules or isolated competing variants through `../taskflow-parallel/SKILL.md`. An independent critic reads raw requirements, actual diffs/outputs and comparison evidence, creates counterexamples, examines effects across modules and labels confirmed defects, conditional risks and unknowns. Route ready approved work promptly; the critic cannot approve adoption. When native tools are absent, disclose serial/self-review mode.

## Compare, discuss and adopt

Compare complete pipelines against the current accepted result, checking mandatory conditions first, then the task's stated priorities. Separate isolated module gains from measured end-to-end benefit; evaluate combinations again. If priorities conflict, ask the user and preserve the accepted result while waiting. Report unsupported/ambiguous evidence as inconclusive, not an improvement.

For a data/calculation counterexample use `../taskflow-verify/references/data-and-properties.md`; for a required local UI use `../taskflow-verify/references/webapp-checks.md` only after runtime/permission checks. Dependencies and upstream source presence are not executed verification. Do not add packages or apply unrelated properties merely to expand test counts.

Present the exact candidate, reproducible evidence, costs/regressions, critic findings, recommendation, rollback target and proposed post-adoption diagnosis scope/budget for user discussion. **Wait for explicit approval of adoption even when the experiment batch was approved.** Do not replace the accepted pointer, wire the candidate into the default API/UI, submit it or call it selected while pending. Recheck candidate/evidence freshness before the approved integration, then execute relevant whole-result checks. Revert to the prior accepted result if integration fails. More edits require new evidence and renewed approval; a newly combined candidate is not covered by separate approvals for its components.

## After every successful adoption

Run an explicitly scoped post-adoption diagnosis of the **new accepted model**, not a reused critique of its predecessor. Measure remaining failure cases/subgroup weaknesses, constraint margins/violations, runtime/memory bottlenecks and effects across module boundaries. A fixed bottleneck can move elsewhere. Separate findings from untested suspicions; avoid inspecting reserved final/hidden evaluation to invent the next improvement.

Record the new version, comparison evidence and residual risks. Turn findings into next candidate hypotheses with expected benefit, verification, cost and dependencies. Explain what changed, why it was adopted and what is still weak in Korean. Report the next proposed batch and seek approval unless that precise follow-on scope is already approved; every future adoption still needs renewed discussion. If no meaningful gain or justified next experiment remains, recommend stopping or simplifying instead of manufacturing work.

Reserve time for integration, fresh verification, required outputs and final explanation. Stop starting experiments that cannot finish and be checked within the approved remaining budget. Approval waits do not disappear near a deadline. Preserve the best **approved, verified** result and unresolved candidates if the host turn/time ends; never imply an endless background loop. At handoff read `../taskflow-verify/SKILL.md`, then explain the final actual result with `../understand/SKILL.md`.
