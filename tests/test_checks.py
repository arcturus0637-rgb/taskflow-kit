"""Real child processes prove failed/stale checks cannot become verification."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1] / 'kit.py'


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'source.py').write_text('x=1\n', encoding='utf-8')

    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', str(KIT), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def check(self, code, *options):
        return self.run_cli('check', '--root', str(self.root), '--task', 'T1',
                            '--watch', 'source.py', *options, '--',
                            sys.executable, '-X', 'utf8', '-c', code)

    def evidence(self, path, task='T1'):
        return self.run_cli('evidence', '--root', str(self.root), '--task', task,
                            '--path', str(path))

    def test_success_captures_korean_output_and_validates(self):
        p = self.check("print('검증 완료')")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        result = json.loads(p.stdout)
        path = Path(result['evidence'])
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(data['returncode'], 0)
        self.assertIn('검증 완료', Path(data['log_path']).read_text(encoding='utf-8'))
        p = self.evidence(path)
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_failed_command_is_not_valid_evidence(self):
        p = self.check('raise SystemExit(7)')
        self.assertEqual(p.returncode, 1, p.stderr + p.stdout)
        q = self.evidence(json.loads(p.stdout)['evidence'])
        self.assertEqual(q.returncode, 2, q.stdout)

    def test_source_change_after_check_invalidates_evidence(self):
        p = self.check('print(1)')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        (self.root / 'source.py').write_text('x=2\n', encoding='utf-8')
        p = self.evidence(json.loads(p.stdout)['evidence'])
        self.assertEqual(p.returncode, 2, p.stdout)

    def test_source_changed_during_check_is_not_success(self):
        p = self.check("from pathlib import Path; Path('source.py').write_text('changed')")
        self.assertEqual(p.returncode, 1, p.stderr + p.stdout)
        q = self.evidence(json.loads(p.stdout)['evidence'])
        self.assertEqual(q.returncode, 2, q.stdout)

    def test_directory_membership_change_invalidates_evidence(self):
        (self.root / 'src').mkdir()
        p = self.run_cli('check', '--root', str(self.root), '--task', 'T1',
                         '--watch', 'src', '--', sys.executable, '-c', 'print(1)')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        (self.root / 'src' / 'new.py').write_text('x=2', encoding='utf-8')
        q = self.evidence(json.loads(p.stdout)['evidence'])
        self.assertEqual(q.returncode, 2, q.stdout)

    def test_timeout_is_recorded_and_rejected(self):
        p = self.check('import time; time.sleep(3)', '--timeout', '0.1')
        self.assertEqual(p.returncode, 1, p.stderr + p.stdout)
        data = json.loads(Path(json.loads(p.stdout)['evidence']).read_text(encoding='utf-8'))
        self.assertTrue(data['timed_out'])
        self.assertNotEqual(data['returncode'], 0)

    def test_wrong_task_and_path_escape_rejected(self):
        p = self.check('print(1)')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        q = self.evidence(json.loads(p.stdout)['evidence'], task='T2')
        self.assertEqual(q.returncode, 2, q.stdout)

    @unittest.skipUnless(os.name == 'nt', 'NTFS compatibility case')
    def test_evidence_junction_rejected_without_new_pathlib_api(self):
        with tempfile.TemporaryDirectory() as target:
            result = subprocess.run(['cmd', '/c', 'mklink', '/J',
                                     str(self.root / '.taskflow'), target], capture_output=True)
            self.assertEqual(result.returncode, 0)
            args = ['check', '--root', str(self.root), '--task', 'T1', '--watch', 'source.py',
                    '--', sys.executable, '-c', 'print(1)']
            code = ("import sys; from pathlib import Path; "
                    "delattr(Path, 'is_junction') if hasattr(Path, 'is_junction') else None; "
                    "from kit import main; sys.exit(main(" + repr(args) + "))")
            p = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=KIT.parent,
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
            self.assertEqual(list(Path(target).iterdir()), [])
        q = self.run_cli('check', '--root', str(self.root), '--task', 'T1',
                         '--watch', '../outside', '--', sys.executable, '-c', 'print(1)')
        self.assertEqual(q.returncode, 2, q.stdout)


if __name__ == '__main__':
    unittest.main()
