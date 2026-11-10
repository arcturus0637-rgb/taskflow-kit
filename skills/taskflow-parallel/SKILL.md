---
name: taskflow-parallel
description: Use when independent parts of an implementation, analysis or investigation can proceed concurrently, including multiple workers within one subsystem or backend.
---

# Parallel work with explicit ownership

Read `../taskflow-workflow/references/decision-policy.md`. Delegate only within an approved work batch, with its decision reference and any unresolved choices. Check which native agent tools actually exist and their observed concurrency limit. Do not infer support from this pack, installed files or ordinary chat creation tools. When unsupported, use serial/self-review mode honestly.

For COFA/managed IDEs, use `../taskflow-workflow/references/cofa-startup.md`. Terminal tabs, queued parent input and native child-agent concurrency are different facilities. A listed `queue` command is not successful message delivery, and multiple terminals do not establish cross-session coordination. Keep unsupported modes explicit rather than change managed settings or start a substitute runner.

Before assigning a model, read [the pinned routing policy](references/model-routing.md). Use Luna 6 for bounded basic work and Sol 6.1 with suitable effort for standard/critical work; the allowed named alternatives are Sol 6.0 and, only with a verified exact native ID, Terra 5.6. Never use Astra, inherit an unknown default or auto-update models/settings. Validate availability with the offline `agent-plan` helper and pass explicit model/effort fields to supported native tools; requested and observed effective models are different facts.

For supported native tools, delegate independent work in parallel. A worker assignment contains: task ID and outcome; the minimum original requirements/source locations and criteria revision; approval/budget reference; difficulty/risk, model/effort and rationale; worker cwd; writable paths; shared resources read/written; contract versions; dependencies; acceptance checks; expected return summary. Keep role names and worker count adaptive, not fixed front/backend roles. Do not copy the entire chat into every worker when a focused packet suffices.

Distinguish collaborating on disjoint modules from competing candidate variants. For variants, start from a known accepted base in isolated checkouts and keep separate outputs/configs, DBs, ports and caches where needed; identical relative paths in different checkouts do not share file edits, but external resources can still conflict. Record the actual cwd/root for each task; the single-root board does not itself manage worktrees. Compare variants under compatible data/criteria and record lineage. A candidate cannot enter the default backend/frontend before user adoption approval. For required UI work, publish versioned contracts/sample responses early instead of waiting for the full model.

For variants on one board, use actual separate directories/checkouts under the same approved board root, e.g. `variants/C1/src/solver.py` and `variants/C2/src/solver.py`. Register/claim those real root-relative scopes and give each worker its actual candidate cwd; reserve common external resources on the same board. Prefixes must correspond to different real files, not invented names for the same file. Do not weaken symlink/junction/path checks, include all variants in the submission, or label candidate completion as accepted integration. If the host requires checkouts outside an allowed common root, this board cannot provide cross-root reservations: use explicit coordinator ownership/resource records or serial scheduling, not separate boards presented as global conflict protection.

Use a read-only independent critic for consequential model experiments when supported and approved. Its packet includes raw requirements, actual changes/outputs and measurements, and asks for assumptions, counterexamples, cross-module effects and confirmed/conditional/unknown findings. A reviewer proposes checks and recommendations, not user approval or a veto based on unsupported suspicion. Do not require every trivial edit to wait for an expensive full review.

Use the local board (`kit.py board --root PROJECT --help`) for durable reservations and next tasks. Register each worker's domain and **returned native target ID**. Claim work before edits. Overlapping file/directory write scopes and conflicting read/write resources must not run together. Declare contracts, schema, shared databases, ports, generated files and dependency manifests when relevant. Read/read resource sharing is allowed.

Scopes are cooperative reservations, not filesystem permissions. Workers must honor them. Never change or release another worker's scope just to bypass a conflict. If scope expands, replan while preserving existing work. Finish releases a running slot; the result's edit reservation stays until integration. `done` is not a dependency-ready integrated result.

When isolated Git worktrees are appropriate and allowed, create separate checkouts from a known base, explicitly start each worker in its checkout, and integrate sequentially into the submission workspace. A branch alone is not isolation. Keep dirty user changes intact. Without isolation, use disjoint write ownership; a shared diff cannot reliably attribute edits to individual workers.

On completion: inspect actual changes, integrate a small result, run relevant connection checks, update the board, and dispatch the next ready task immediately. A blocked high-priority item must not prevent unrelated ready work. Never apply an unreviewed blanket overwrite to resolve conflicts.

Reclaim a running task only after the native worker is confirmed stopped; `release --stopped` records that observation, it does not stop the worker. Timeouts or silence are not proof of stopping. Handle semantic contract changes through the inbox protocol before consumers resume.
