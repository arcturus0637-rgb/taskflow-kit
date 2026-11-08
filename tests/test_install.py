"""Installation must preserve user files and fail before unrelated writes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1] / 'kit.py'


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', str(KIT), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def test_preserves_instruction_bytes_and_task_files(self):
        original = b'# Existing\r\nDo not replace this.\r\n'
        (self.root / 'AGENTS.md').write_bytes(original)
        (self.root / 'answer.py').write_bytes(b'print(7)\n')
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual((self.root / 'AGENTS.md').read_bytes(), original)
        self.assertEqual((self.root / 'answer.py').read_bytes(), b'print(7)\n')
        self.assertTrue((self.root / '.taskflow-kit' / 'kit.py').is_file())
        skills = self.root / '.agents' / 'skills'
        self.assertEqual(len(list(skills.glob('taskflow-*/SKILL.md'))), 5)
        self.assertFalse((skills / 'systematic-debugging').exists())

    def test_dry_run_creates_nothing(self):
        p = self.run_cli('install', '--project', str(self.root), '--dry-run')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_skill_conflict_is_rejected_before_runtime_copy(self):
        existing = self.root / '.agents' / 'skills' / 'taskflow-inbox'
        existing.mkdir(parents=True)
        (existing / 'SKILL.md').write_text('User owned\n', encoding='utf-8')
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertFalse((self.root / '.taskflow-kit').exists())
        self.assertEqual((existing / 'SKILL.md').read_text(encoding='utf-8'), 'User owned\n')

    def test_runtime_conflict_is_rejected_without_overwrite(self):
        existing = self.root / '.taskflow-kit'
        existing.mkdir()
        (existing / 'kit.py').write_text('user-owned', encoding='utf-8')
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertFalse((self.root / '.agents').exists())
        self.assertEqual((existing / 'kit.py').read_text(encoding='utf-8'), 'user-owned')

    def test_repeat_install_same_bytes_is_idempotent(self):
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        before = {str(x.relative_to(self.root)): x.read_bytes()
                  for x in self.root.rglob('*') if x.is_file()}
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        after = {str(x.relative_to(self.root)): x.read_bytes()
                 for x in self.root.rglob('*') if x.is_file()}
        self.assertEqual(after, before)

    def test_symbolic_link_install_target_is_rejected(self):
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        try:
            (self.root / '.agents').symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                self.skipTest('Host does not allow symbolic links')
            result = subprocess.run(['cmd', '/c', 'mklink', '/J',
                                     str(self.root / '.agents'), str(outside)],
                                    capture_output=True)
            if result.returncode:
                self.skipTest('Host does not allow symbolic links or junctions')
        p = self.run_cli('install', '--project', str(self.root))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == 'nt', 'NTFS compatibility case')
    def test_junction_rejected_without_new_pathlib_api(self):
        outside = Path(self.tmp.name) / 'outside310'
        outside.mkdir()
        result = subprocess.run(['cmd', '/c', 'mklink', '/J',
                                 str(self.root / '.agents'), str(outside)], capture_output=True)
        self.assertEqual(result.returncode, 0)
        code = ("import sys; from pathlib import Path; "
                "delattr(Path, 'is_junction') if hasattr(Path, 'is_junction') else None; "
                "from kit import main; sys.exit(main(['install','--project'," + repr(str(self.root)) + "]))")
        p = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=KIT.parent,
                           capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
