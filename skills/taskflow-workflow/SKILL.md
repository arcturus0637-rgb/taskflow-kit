---
name: taskflow-workflow
description: Use when a substantial task must be understood, implemented, validated and handed over under a deadline, including unfamiliar assignments and projects with ongoing user changes.
---

# TaskFlow workflow

Use the actual assignment as authority. Choose the medium, stack and methods from its requirements and existing environment. This pack supplies coordination, not a domain solution or a new permission grant.

1. Read `taskflow-brief/SKILL.md` beside this skill. Give the user a short actionable brief early; distinguish required, optional, examples and assumptions. Inspect the existing project before choosing architecture.
2. Establish the available execution time and host capabilities from observed tools. Read `taskflow-parallel/SKILL.md` when independent work exists. A skill cannot create native agent support. If unavailable, state serial mode and continue useful work. Never launch extra model CLIs, use personal credentials or change global settings as a workaround.
3. Build the smallest complete path through real input and output before optional polish. For analysis use a simple baseline; for algorithms an independently checkable small case; for documents the required content and render; for software a runnable core flow. Pick only what the assignment needs.
4. Keep a short task board and requirement-to-check mapping. Assign concrete outcomes, write scopes, dependency/contract versions and completion checks. Reconcile worker completion and dispatch newly ready work as results arrive, rather than waiting for every worker in a batch.
5. **On every new user message while work continues**, run `taskflow-inbox/SKILL.md` at the next observable boundary. Answer brief status questions, preserve the objective and route actual changes. Never silently drop a request or call an unacknowledged message delivered.
6. Diagnose reproducible failures before speculative changes. Read only the relevant upstream source through `docs/SOURCES.ko.md` in the runtime kit. Use targeted review or simplification when they improve the actual deliverable, without importing whole upstream processes or extra approval gates.
7. Read `taskflow-verify/SKILL.md` before completion. Reserve enough remaining time for integration, meaningful checks and the specified submission.
8. After the implementation and checks, read the sibling `understand/SKILL.md`. Apply Understand Anything to the actual final result and deliver a source-grounded Korean explanation so the user can understand it. Keep graph-runtime blockers explicit and final source checks current. Then report actual results, limitations and the next required user action if any.

## Runtime

Project-local installation puts `kit.py`, upstream references and docs in `.taskflow-kit/`. Use `python .taskflow-kit/kit.py --help`; use `python3` if that is the available interpreter. With a source checkout, use its `kit.py` directly. Do not copy private task data to the public pack.

The board is a helper, not a background agent service. While a turn runs, the coordinator must actually use the native dispatch/message/followup tools and reconcile their results. Before yielding with unfinished work, preserve pending requests, active target IDs and blockers; do not imply execution continues after the host stops it.
