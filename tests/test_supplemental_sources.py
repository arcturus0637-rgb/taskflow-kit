"""Approved supplemental references stay pinned, complete and passive."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW_IDS = {'trailofbits-property-testing', 'anthropic-webapp-testing'}


class SupplementalSourceTests(unittest.TestCase):
    def sources(self):
        lock = json.loads((ROOT / 'config/sources.lock.json').read_text(encoding='utf-8'))
        sources = [s for s in lock['sources'] if s['id'] in NEW_IDS]
        self.assertEqual({s['id'] for s in sources}, NEW_IDS)
        return sources

    def test_every_supplemental_blob_matches_pinned_hash_and_size(self):
        total = 0
        for source in self.sources():
            self.assertRegex(source['commit'], r'^[0-9a-f]{40}$')
            self.assertEqual(source['mode'], 'passive-reference')
            for record in source['files']:
                with self.subTest(path=record['local_path']):
                    path = ROOT / record['local_path']
                    self.assertTrue(path.resolve().is_relative_to(ROOT.resolve()))
                    data = path.read_bytes()
                    self.assertEqual(len(data), record['size_bytes'])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])
                    self.assertEqual(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),
                                     record['git_blob_sha1'])
                    self.assertIn('/blob/'+source['commit']+'/', record['source_url'])
                total += 1
        self.assertEqual(total, 17)

    def test_selected_snapshots_have_no_unrecorded_or_missing_source_files(self):
        for source in self.sources():
            actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / source['snapshot']).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts}
            recorded = {f['local_path'] for f in source['files']}
            self.assertEqual(actual, recorded, source['id'])
            self.assertTrue(set(source['entry_paths']).issubset(recorded))

    def test_licenses_and_notices_are_preserved_as_pinned_files(self):
        for source in self.sources():
            recorded = {f['local_path'] for f in source['files']}
            self.assertTrue(source['license_paths'])
            self.assertTrue(set(source['license_paths']).issubset(recorded))
        licenses = {s['id']:s['license'] for s in self.sources()}
        self.assertEqual(licenses['trailofbits-property-testing'], 'CC-BY-SA-4.0')
        self.assertIn('Apache-2.0', licenses['anthropic-webapp-testing'])

    def test_install_copies_guides_and_raw_sources_without_plugin_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            p = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'kit.py'), 'install',
                                '--project', tmp], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            expected = {'taskflow-workflow','taskflow-brief','taskflow-model','taskflow-improve',
                        'taskflow-parallel','taskflow-inbox','taskflow-verify','understand'}
            self.assertEqual(set(json.loads(p.stdout)['skills']), expected)
            self.assertEqual({p.name for p in (project / '.agents/skills').iterdir()}, expected)
            for source in self.sources():
                for entry in source['entry_paths'] + source['license_paths']:
                    self.assertEqual((project / '.taskflow-kit' / entry).read_bytes(),
                                     (ROOT / entry).read_bytes())
            for relative in ('taskflow-workflow/references/cofa-startup.md',
                             'taskflow-verify/references/data-and-properties.md',
                             'taskflow-verify/references/webapp-checks.md'):
                self.assertEqual((project / '.agents/skills' / relative).read_bytes(),
                                 (ROOT / 'skills' / relative).read_bytes())
            self.assertFalse((project / '.claude').exists())
            self.assertFalse((project / '.taskflow').exists())


if __name__ == '__main__':
    unittest.main()
