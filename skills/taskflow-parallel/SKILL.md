---
name: taskflow-parallel
description: Use when independent parts of an implementation, analysis or investigation can proceed concurrently, including multiple workers within one subsystem or backend.
---

# Parallel work with explicit ownership

Check which native agent tools actually exist and their observed concurrency limit. Do not infer support from this pack, installed files or ordinary chat creation tools. When unsupported, use serial mode honestly.

For supported native tools, delegate independent work in parallel. A worker assignment contains: task ID and outcome; the minimum original requirements/source locations; worker cwd; writable paths; shared resources read/written; contract versions; dependencies; acceptance checks; expected return summary. Keep role names and worker count adaptive, not fixed front/backend roles. Do not copy the entire chat into every worker when a focused packet suffices.

Use the local board (`kit.py board --root PROJECT --help`) for durable reservations and next tasks. Register each worker's domain and **returned native target ID**. Claim work before edits. Overlapping file/directory write scopes and conflicting read/write resources must not run together. Declare contracts, schema, shared databases, ports, generated files and dependency manifests when relevant. Read/read resource sharing is allowed.

Scopes are cooperative reservations, not filesystem permissions. Workers must honor them. Never change or release another worker's scope just to bypass a conflict. If scope expands, replan while preserving existing work. Finish releases a running slot; the result's edit reservation stays until integration. `done` is not a dependency-ready integrated result.

When isolated Git worktrees are appropriate and allowed, create separate checkouts from a known base, explicitly start each worker in its checkout, and integrate sequentially into the submission workspace. A branch alone is not isolation. Keep dirty user changes intact. Without isolation, use disjoint write ownership; a shared diff cannot reliably attribute edits to individual workers.

On completion: inspect actual changes, integrate a small result, run relevant connection checks, update the board, and dispatch the next ready task immediately. A blocked high-priority item must not prevent unrelated ready work. Never apply an unreviewed blanket overwrite to resolve conflicts.

Reclaim a running task only after the native worker is confirmed stopped; `release --stopped` records that observation, it does not stop the worker. Timeouts or silence are not proof of stopping. Handle semantic contract changes through the inbox protocol before consumers resume.
