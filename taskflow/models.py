"""Validate a pinned native-agent model plan offline; never dispatch or update."""
import argparse
import json
from pathlib import Path

POLICY = Path(__file__).resolve().parents[1] / 'skills/taskflow-parallel/references/model-policy.json'


def plan(tier, available, model_label=None, policy_path=None):
    policy = json.loads(Path(policy_path or POLICY).read_text(encoding='utf-8'))
    if policy.get('schema_version') != 1 or policy.get('automatic_updates') is not False:
        raise ValueError('Pinned model policy must disable automatic updates')
    tiers = policy.get('tiers', {})
    if tier not in tiers:
        raise ValueError('Unknown agent tier: ' + str(tier))
    choice = tiers[tier]
    label = model_label if model_label is not None else choice['model_label']
    if not isinstance(label, str) or 'astra' in label.casefold():
        raise ValueError('Astra or an invalid model label is forbidden')
    models = {item['label']: item['native_id'] for item in policy['models']}
    if label not in models:
        raise ValueError('Model label is outside the user allowlist: ' + label)
    model = models[label]
    if model is None:
        raise ValueError(label + ' has no verified native ID; do not guess or substitute a version')
    if not isinstance(model, str) or 'astra' in model.casefold() or model.casefold() in ('auto', 'latest', 'default', ''):
        raise ValueError('Forbidden or unpinned native model: ' + str(model))
    observed = set(available)
    if model not in observed:
        raise ValueError('Requested model is not in the observed native availability list: ' + model
                         + '; report alternatives and obtain any needed approval, not automatic fallback')
    effort = choice['reasoning_effort']
    if effort not in ('low', 'medium', 'high'):
        raise ValueError('Unsupported pinned reasoning effort: ' + str(effort))
    return {'ok': True, 'tier': tier, 'model_label': label, 'model': model,
            'reasoning_effort': effort, 'automatic_updates': False,
            'performed_dispatch': False, 'performed_update': False,
            'availability_source': 'caller-observed native tool metadata; not independently attested',
            'approval': 'Check the actual approved batch and native override support before dispatch'}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tier', choices=('basic', 'standard', 'critical'), required=True)
    parser.add_argument('--available', action='append', required=True,
                        help='Exact model ID observed in this host native tool; repeat as needed')
    parser.add_argument('--model-label', help='Explicit allowed alternative inside approved routing scope')
    args = parser.parse_args(argv)
    print(json.dumps(plan(args.tier, args.available, args.model_label), ensure_ascii=False))
    return 0
