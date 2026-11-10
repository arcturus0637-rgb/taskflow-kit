# Small, traceable experiment records

Use existing project records if equivalent; do not introduce a second tracker. Otherwise keep private task records under `.taskflow/`, outside a restricted submission set and the public skill repository. The existing board tracks assigned work/dependencies; it does not interpret metrics, obtain approval or run this loop for the agent.

## Record enough to distinguish states

- `.taskflow/model-plan.md`: task sources/criteria revision, input/output semantics, minimal module graph and methods, assumptions, checks and approved initial scope.
- `.taskflow/decisions.md`: the [decision policy](../../taskflow-workflow/references/decision-policy.md) approval records and unresolved priority conflicts. Copy/reference actual user decisions; never generate consent.
- `.taskflow/accepted.md`: currently approved and verified version/fingerprints, adoption decision reference, reproduction, evidence, known limits and previous rollback target. Keep it unchanged while a candidate is pending. If there is no accepted result yet, say so rather than assign one by default.
- `.taskflow/experiments/C1.md` (or a small table for trivial cases): candidate ID, base accepted version; task/criteria/contracts/data revision; hypothesis and affected modules; approved batch reference and budget; changed source/config fingerprints; comparison conditions and real evidence; critic findings; recommendation; user adoption decision reference if any; integration/verification outcome; post-adoption diagnosis and next proposal.

Candidate states may be `proposed -> batch-approved -> running -> evaluated -> awaiting-adoption -> adopted`, with `inconclusive`, `rejected`, `stale` or `integration-failed` where appropriate. These are documentation states, not new board commands. `evaluated` or `worker-done` does not mean approved, integrated or adopted. An adoption approval cannot make failed/stale checks pass. Record rejected/inconclusive outcomes so the next iteration does not repeat them without new evidence.

## Post-adoption diagnosis

For each remaining issue record: observed case/profile and source of evidence; affected requirement/module; measured impact or unknown; suspected cause and confidence; smallest discriminating test; proposed change/alternative; expected benefit and regression; cost/dependencies; priority from the actual task or a pending user question. Include cross-module costs and changes to bottlenecks. If diagnosis was not included in the approved adoption/batch scope, propose it and wait first.

The next experiment must point to its new accepted base version. Concurrent candidates based on an older version are not automatically invalid, but they cannot be promoted as improvements over the new accepted result without a fresh compatible comparison and, for integration, conflict/interaction checks. Preserve any reserved final evaluation and do not treat a reused development benchmark as unseen performance evidence.
