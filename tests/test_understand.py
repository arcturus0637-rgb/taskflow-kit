"""The added skill must install with its original support files, not just prose."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UnderstandTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'kit.py'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def test_new_project_installs_understand_and_its_original_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.run_cli('install', '--project', tmp)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            installed = Path(tmp)
            self.assertTrue((installed / '.agents/skills/understand/SKILL.md').is_file())
            plugin = installed / '.taskflow-kit/upstream/understand-anything/understand-anything-plugin'
            self.assertTrue((plugin / 'skills/understand/build-fingerprints.mjs').is_file())
            self.assertTrue((plugin / 'agents/project-scanner.md').is_file())
            p = subprocess.run([sys.executable, '-X', 'utf8', str(installed / '.taskflow-kit/kit.py'),
                                'understand-status', '--root', tmp], capture_output=True,
                               text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(Path(data['plugin_root']), plugin.resolve())
            self.assertEqual(data['stage'], 'after-implementation-and-verification')
            self.assertFalse(data['core_built'])
            self.assertFalse(data['ready'])
            self.assertFalse((installed / '.ua').exists())

    def test_status_uses_final_project_and_existing_legacy_data_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.understand-anything').mkdir()
            p = self.run_cli('understand-status', '--root', tmp)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(Path(data['project_root']), root.resolve())
            self.assertEqual(Path(data['graph_path']), root / '.understand-anything/knowledge-graph.json')
            self.assertFalse((root / '.ua').exists())
            self.assertFalse((root / '.understand-anything/config.json').exists())

    def test_invalid_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.run_cli('understand-status', '--root', str(Path(tmp) / 'missing'))
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)


if __name__ == '__main__':
    unittest.main()
