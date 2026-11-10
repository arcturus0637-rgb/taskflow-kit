---
name: taskflow-verify
description: Use before reporting a task complete or ready to submit, when combining agent results, or when later source or contract changes may have invalidated previous checks.
---

# Verify the delivered result

Read `../taskflow-workflow/references/decision-policy.md`; verification inside an approved batch does not itself grant candidate adoption. Use the requirement table and its actual priority/criteria revision as the acceptance checklist. Ask the user if priorities still conflict rather than choose a convenient score. Inspect actual artifacts and integration changes; a worker's completion message is not execution evidence. Read the pinned verification source in the runtime kit through `docs/SOURCES.ko.md` when verification planning is needed.

Pick meaningful checks for the deliverable: execute actual inputs and outputs for software/algorithms; compare to an independent baseline and valid held-out data for analysis; render and inspect final documents/media where layout or playback matters. Include required edge cases, preservation constraints and relevant failures. Do not create redundant tests merely mirroring implementation text.

Load only the applicable guide: [data/contracts/properties](references/data-and-properties.md) for independent numerical/data checks or counterexamples; [web application checks](references/webapp-checks.md) for a required, permitted UI. Each routes to pinned passive upstream sources with its original license, not an automatically active plugin. Never auto-install a testing dependency/browser or claim actual tests from source availability. Managed COFA capability/permission checks are in `../taskflow-workflow/references/cofa-startup.md`.

Report successful execution, requirement/constraint validity, quality and robustness separately. During improvement, compare complete pipelines with compatible inputs, task criteria and budgets; check combined candidates again. Keep final evaluation out of repeated model selection and post-adoption diagnosis. User approval cannot turn stale/failed evidence into success; use the actual approved integrated version and refresh its checks. After successful adoption use `../taskflow-improve/SKILL.md` to diagnose the new accepted version and propose the next batch within the recorded scope.

Record implemented, integrated, executed and verified states separately. A task can be worker-done while its dependency remains blocked until integration. Use `kit.py check --root PROJECT --task T1 --watch SOURCE ... -- COMMAND ARGS...` to capture a real command, log, return status and watched source fingerprints. Choose watches covering relevant code, contracts, inputs, tests and dependency manifests; watching one file does not validate the whole project. Keep expected generated outputs outside source watches or validate them separately.

`board verify --task T1 --evidence FILE` accepts only matching, successful, unchanged-source evidence. Revalidate before the final claim, since later edits can make recorded verified states stale. These records provide local consistency checks, not tamper-proof attestation, automatic UI observation or proof of every requirement. Never record a manual screen check you have not actually observed.

Confirm the final submission workspace contains all integrated work and the required output files. Preserve original inputs. Provide a short explanation grounded in the actual implementation: what was built, why the chosen approach fits, measured results, known limits and reproduction steps. Do not claim optimality, causality, performance gains or submission without corresponding evidence.

If final submission is a separate user/platform action, state precisely what remains. The helper never presses a submit button. Honor actual contest rules for tool use and any post-submission stage; do not import preliminary-round restrictions as facts about a different round.

After implementation checks, use the bundled `understand` adapter to explain the completed result in Korean, with an actual source-grounded walkthrough and optional executed graph. Keep this before any stage that prohibits AI use. Do not let explanation generation silently change tested implementation; refresh affected checks if it does.
