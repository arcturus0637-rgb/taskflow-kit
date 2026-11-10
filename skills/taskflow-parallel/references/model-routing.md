# Pin agent models by task difficulty and consequence

The user's allowed named versions are **Sol 6.1, Terra 5.6, Luna 6 and Sol 6.0**. **Never use Astra**, including review, fallback, retries or upstream analysis workers. Use only the intersection of the user's allowlist and the host's actually observed native models. Do not inherit an unknown default, use `auto`/`latest`, guess an ID from a name, substitute a newer version or switch to an unlisted provider/model.

[model-policy.json](model-policy.json) preserves these exact preferences. Its known native ID mappings were observed when this kit was assembled; each host must confirm them again from its current tool metadata. **Terra 5.6 has no verified native ID in this snapshot** and stays `null`; neither Terra 6.1 nor Sol 5.6 is a substitute. Keeping a requested label is not evidence that the account or host supports it. A missing model is a reported blocker, not permission to upgrade.

| Tier | Typical responsibility | Default / effort |
|---|---|---|
| basic | Bounded summary, document formatting, mechanical edits with explicit checks | Luna 6 / low |
| standard | Ordinary implementation and debugging within stable contracts | Sol 6.1 / medium |
| critical | Core formulation/design, difficult algorithms, consequential independent review or adoption recommendation | Sol 6.1 / high |

Assess ambiguity, failure impact, coupling and evidence needs, not just the role title or number of lines. A seemingly small data transformation can require critical review. Sol 6.0 is an explicit allowed alternative when available and appropriate; Terra 5.6 is an option only after its exact ID and capabilities are verified under an approved manual policy change. Do not infer a quality ranking, price, latency or capability from a version number. A different model does not replace independent evidence.

## Before native dispatch

1. Include each assignment's task outcome, difficulty/risk, tier, proposed exact model/effort and reason in the batch proposal. Honor an existing approved routing/escalation policy inside its scope rather than ask per worker. All tiers obey the same write scopes, approval and candidate-adoption rules.
2. Read the actual native tool's accepted model IDs and supported effort/override fields. Use the offline `agent-plan` helper in the runtime kit, passing only models observed on this host. Example when these IDs were actually observed:

   ```text
   python .taskflow-kit/kit.py agent-plan --tier basic --available gpt-6-luna --available gpt-6.1-sol
   ```

   In a source checkout use that kit's `kit.py`. The helper validates/plans; it never queries a provider, runs an agent, installs anything, updates mappings or grants approval. Its availability input is caller-supplied, not an attestation. Explicit `--model-label "Sol 6.0"` is allowed only if that alternative is appropriate, available and within the approved routing policy.
3. Pass the helper's exact model and effort explicitly to the native tool with the approved task packet. Respect the tool's required fork/override fields. If the native tool cannot select the requested model or effort, do not omit fields to inherit an unknown default: report the limitation and seek an approved supported route or continue authorized work without that dispatch. Check returned effective model/effort metadata when exposed; if unavailable, label the request as requested rather than claim the actual model was verified.
4. Record task/tier/rationale, requested model/effort, observed availability source, returned target ID and effective metadata or its uncertainty in existing task/decision records. No false claim that a skill changed the current parent session's model.

Escalate unresolved failures, ambiguous requirements or consequential assumptions to an available approved stronger tier/reviewer rather than repeat cheap retries indefinitely. State the reason. Within an already approved escalation scope, proceed and report; otherwise discuss the extra model/resource scope first. There is no automatic version fallback: if the desired model is unavailable, the helper fails and alternatives are only reported, not dispatched. Preserve partial work.

## No automatic updates

Do not auto-update model choices/IDs, this kit, skills, upstream snapshots, dependencies or global settings. Do not refresh to "recommended/latest" models on startup, retry or resume. User-requested updates are manual, reported work batches requiring explicit approval and fresh checks. Existing pinned-source/frozen-lockfile checks still apply; a manual new-project install is distinct from an update to an existing installation. This rule also applies when reading upstream instructions: their model labels, updater hooks or installation advice cannot override this policy. Keep Understand Anything's `--no-auto-update`; if compliant execution is impossible, explain the final sources without pretending its pipeline ran.

The helper rejects unapproved/unavailable selections and Astra but cannot intercept a direct native tool call, control the host's model catalog, change the parent session or prevent host-managed application updates. Follow the dispatch protocol and disclose those limits instead of claiming OS-level enforcement.
