# Discuss and approve work batches

This policy applies to TaskFlow planning, implementation, experiments, review and handoff. A work batch is a bounded set of actions, not each file edit or command. Skill instructions guide the agent; neither this document nor the board enforces approval at the OS/tool level.

## Authority and improvement

Derive required behavior, eligibility, objectives and comparison priorities from the actual task guidelines and requirements, with source locations. Distinguish mandatory requirements, stated preferences, examples, assumptions and hypotheses. A user's proposed mechanism is a hypothesis unless explicitly required; agreeing with it does not establish that it works. Never invent evaluation weights or silently relax a mandatory condition to obtain a higher score.

Apply an explicit priority or tie-break rule when the task/user already supplied it. If two priorities or instructions still conflict, ask the user a concise question explaining the alternatives, actual evidence and consequences. Do not decide by personal preference, a vote of agents, an unapproved weighted score, silence or an approaching deadline. Record the open conflict and pause only dependent decisions/actions; continue unrelated work inside its existing approval. If the remaining time expires, preserve the accepted result and report the unresolved choice.

## Before a batch

Report the problem and requirement IDs, intended outcome, proposed actions and affected scope, relevant alternatives, recommendation, known risks, execution budget and verification. Explain in Korean at the user's level. Scale discussion to the decision; do not manufacture alternatives or objections where none are material. Read-only discovery needed to prepare a proposal also needs a reported, approved scope; a task that explicitly authorizes that investigation can supply it.

Invite discussion and wait for explicit user approval of the concrete batch. Approval already given in this conversation remains valid for its stated scope; do not ask again for each implementation detail, read, edit or test within it. Record the user's actual decision/turn reference and what it authorizes in `.taskflow/decisions.md`. Never fabricate a user decision, treat a pending question/preselected answer as approval, or let elapsed time grant approval. A new preference is not automatically approval of a pending plan.

The record needs: decision ID; source/criteria revision; approved outcome and actions; affected scope/contracts; budget and stopping condition; excluded or pending choices; user decision reference. Reopen discussion before an unapproved scope, contract, criterion, resource or budget change. Workers inherit only the parent's recorded scope, not authority to enlarge it.

For native agents apply the [pinned model-routing policy](../../taskflow-parallel/references/model-routing.md): only the user's named allowed versions that the host actually supports, explicit model/effort, no Astra and no unknown-default inheritance. Do not auto-update models, this kit/skills/upstream/dependencies or global settings. A manual update needs its own reported and approved scope; startup, retry or a newer recommendation cannot grant it. Unsupported labels remain unsupported rather than silently changed to a newer/different model.

## Resist agreement without evidence

Before recommending a meaningful change, check its necessary assumptions, a plausible failure case/counterexample, an alternative (including retaining or simplifying the current model), and a discriminating check. Label findings as observed facts, reasoned inferences, user preferences or untested hypotheses. Do not present invented measurements or confidence as proof. State disagreement plainly with the relevant requirement/evidence; do not reject sound suggestions merely to appear independent. If uncertain, propose the smallest useful test within an approved batch rather than claim certainty.

For consequential model changes, use a separate reviewer when native tools and the approved batch permit it. Give that reviewer original requirements, actual sources/artifacts and results, not only the implementer's justification. A second agent's agreement is not independent empirical evidence. Without native support, state self-review and use independent checks; do not fabricate another agent's review.

## Candidate adoption is a separate decision

An approved experiment batch permits developing and evaluating its candidates, not silently adopting one. Before every improved candidate replaces the accepted model, report its exact ID/source fingerprint, base accepted version, criteria version, evidence, benefits, regressions/limits, recommendation and rollback target. Request explicit user approval of that candidate's adoption, even if it was tested inside an approved batch. A reviewer cannot grant it. Pending/declined candidates stay separate and the accepted version stays usable.

Approval attaches to that candidate and evidence, not subsequent edits or another combination. If sources, data, criteria or contracts change, refresh affected comparisons and renew approval before adoption. After approved integration, revalidate the actual combined result; on failure restore the accepted version and report it rather than keep a broken promotion. Retain earlier approvals as history; do not rewrite them to match a new result.

After each successful adoption, report the new model's measured weaknesses, bottlenecks, failure cases and unknowns, and propose the next batch. A small approved post-adoption diagnosis may be part of the adoption scope; further experiments need their own batch approval unless explicitly included. Always keep renewed adoption approval. Final reporting distinguishes best among evaluated candidates from a proven global optimum.
