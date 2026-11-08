---
name: taskflow-verify
description: Use before reporting a task complete or ready to submit, when combining agent results, or when later source or contract changes may have invalidated previous checks.
---

# Verify the delivered result

Use the requirement table as the acceptance checklist. Inspect actual artifacts and integration changes; a worker's completion message is not execution evidence. Read the pinned verification source in the runtime kit through `docs/SOURCES.ko.md` when verification planning is needed.

Pick meaningful checks for the deliverable: execute actual inputs and outputs for software/algorithms; compare to an independent baseline and valid held-out data for analysis; render and inspect final documents/media where layout or playback matters. Include required edge cases, preservation constraints and relevant failures. Do not create redundant tests merely mirroring implementation text.

Record implemented, integrated, executed and verified states separately. A task can be worker-done while its dependency remains blocked until integration. Use `kit.py check --root PROJECT --task T1 --watch SOURCE ... -- COMMAND ARGS...` to capture a real command, log, return status and watched source fingerprints. Choose watches covering relevant code, contracts, inputs, tests and dependency manifests; watching one file does not validate the whole project. Keep expected generated outputs outside source watches or validate them separately.

`board verify --task T1 --evidence FILE` accepts only matching, successful, unchanged-source evidence. Revalidate before the final claim, since later edits can make recorded verified states stale. These records provide local consistency checks, not tamper-proof attestation, automatic UI observation or proof of every requirement. Never record a manual screen check you have not actually observed.

Confirm the final submission workspace contains all integrated work and the required output files. Preserve original inputs. Provide a short explanation grounded in the actual implementation: what was built, why the chosen approach fits, measured results, known limits and reproduction steps. Do not claim optimality, causality, performance gains or submission without corresponding evidence.

If final submission is a separate user/platform action, state precisely what remains. The helper never presses a submit button. Honor actual contest rules for tool use and any post-submission stage; do not import preliminary-round restrictions as facts about a different round.
