"""Model planning stays pinned, explicit and offline before native dispatch."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from taskflow.models import POLICY, plan

ROOT = Path(__file__).resolve().parents[1]
OBSERVED = ['gpt-6.1-sol', 'gpt-6-luna', 'gpt-6-sol', 'gpt-6.1-terra']


class ModelPlanTests(unittest.TestCase):
    def test_basic_uses_exact_luna_and_low_effort(self):
        result = plan('basic', OBSERVED)
        self.assertEqual((result['model'], result['reasoning_effort']), ('gpt-6-luna', 'low'))
        self.assertFalse(result['automatic_updates'])
        self.assertFalse(result['performed_dispatch'])
        self.assertFalse(result['performed_update'])

    def test_standard_and_critical_keep_same_sol_version_with_distinct_effort(self):
        standard, critical = (plan(tier, OBSERVED) for tier in ('standard', 'critical'))
        self.assertEqual(standard['model'], 'gpt-6.1-sol')
        self.assertEqual(critical['model'], 'gpt-6.1-sol')
        self.assertEqual((standard['reasoning_effort'], critical['reasoning_effort']), ('medium', 'high'))

    def test_sol_60_is_only_an_explicit_alternative(self):
        result = plan('standard', OBSERVED, 'Sol 6.0')
        self.assertEqual(result['model'], 'gpt-6-sol')
        with self.assertRaisesRegex(ValueError, 'not in the observed'):
            plan('standard', ['gpt-6-sol'])

    def test_missing_luna_never_falls_back_to_available_sol(self):
        with self.assertRaisesRegex(ValueError, 'not in the observed'):
            plan('basic', ['gpt-6.1-sol'])

    def test_terra_56_stays_unresolved_not_terra_61_or_sol_56(self):
        with self.assertRaisesRegex(ValueError, 'no verified native ID'):
            plan('critical', ['gpt-6.1-terra', 'gpt-5.6-sol'], 'Terra 5.6')

    def test_astra_and_other_labels_cannot_be_requested(self):
        for label in ('Astra', 'ASTRA 6', 'gpt-6-astra', 'Terra 6.1', 'Sol 5.6', 'latest'):
            with self.subTest(label=label), self.assertRaises(ValueError):
                plan('critical', OBSERVED + ['gpt-6-astra'], label)

    def test_astra_exposed_by_host_is_never_selected(self):
        result = plan('basic', OBSERVED + ['gpt-6-astra'])
        self.assertEqual(result['model'], 'gpt-6-luna')

    def test_empty_availability_is_not_permission_to_inherit_default(self):
        with self.assertRaisesRegex(ValueError, 'not in the observed'):
            plan('basic', [])

    def test_auto_updates_or_astra_mapping_are_rejected(self):
        original = json.loads(POLICY.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            policy_path = Path(tmp) / 'model-policy.json'
            for kind in ('updates', 'astra', 'default'):
                policy = json.loads(json.dumps(original))
                if kind == 'updates':
                    policy['automatic_updates'] = True
                else:
                    policy['models'][2]['native_id'] = 'gpt-6-AsTrA' if kind == 'astra' else 'DEFAULT'
                policy_path.write_text(json.dumps(policy), encoding='utf-8')
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    plan('basic', OBSERVED + ['gpt-6-AsTrA', 'DEFAULT'], policy_path=policy_path)

    def test_cli_only_returns_plan_and_rejects_unlisted_model(self):
        success = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'kit.py'), 'agent-plan',
                                  '--tier', 'basic', '--available', 'gpt-6-luna'],
                                 capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(success.returncode, 0, success.stdout + success.stderr)
        result = json.loads(success.stdout)
        self.assertFalse(result['performed_dispatch'])
        self.assertFalse(result['performed_update'])
        failure = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'kit.py'), 'agent-plan',
                                  '--tier', 'basic', '--available', 'gpt-6-astra'],
                                 capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(failure.returncode, 2, failure.stdout + failure.stderr)
        self.assertFalse(json.loads(failure.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
