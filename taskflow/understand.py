"""Inspect the bundled Understand Anything runtime without installing or running it."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def _tool(name, minimum):
    executable = shutil.which(name)
    if not executable:
        return {'path': None, 'version': None, 'supported': False}
    try:
        p = subprocess.run([executable, '--version'], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=8)
        match = re.search(r'(\d+)\.\d+', p.stdout)
        return {'path': executable, 'version': p.stdout.strip() if p.returncode == 0 else None,
                'supported': p.returncode == 0 and match is not None and int(match.group(1)) >= minimum}
    except (OSError, subprocess.SubprocessError):
        return {'path': executable, 'version': None, 'supported': False}


def status(project, source=ROOT):
    project, source = Path(project).resolve(), Path(source).resolve()
    if not project.is_dir():
        raise ValueError('Final project directory does not exist')
    snapshot = source / 'upstream' / 'understand-anything'
    plugin = snapshot / 'understand-anything-plugin'
    skill = plugin / 'skills' / 'understand' / 'SKILL.md'
    required = [skill, plugin / 'package.json', plugin / 'pnpm-workspace.yaml',
                plugin / 'skills/understand/build-fingerprints.mjs',
                plugin / 'agents/project-scanner.md', snapshot / 'LICENSE']
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise ValueError('Incomplete Understand Anything snapshot: ' + ', '.join(missing))
    node, pnpm = _tool('node', 22), _tool('pnpm', 10)
    core_built = (plugin / 'packages/core/dist/index.js').is_file()
    data = project / ('.understand-anything' if (project / '.understand-anything').is_dir() else '.ua')
    reasons = []
    if not node['supported']:
        reasons.append('Node.js >=22 is required for upstream analysis')
    if not pnpm['supported']:
        reasons.append('pnpm >=10 is required for upstream workspace preparation')
    if not core_built:
        reasons.append('Bundled source is present; upstream core is not built')
    return {'ok': True, 'stage': 'after-implementation-and-verification',
            'project_root': str(project), 'plugin_root': str(plugin),
            'original_skill': str(skill), 'snapshot_license': str(snapshot / 'LICENSE'),
            'graph_path': str(data / 'knowledge-graph.json'),
            'explanation_name': 'UNDERSTAND.ko.md', 'node': node, 'pnpm': pnpm,
            'core_built': core_built, 'ready': not reasons, 'blockers': reasons,
            'performed_analysis': False, 'installed_packages': False,
            'native_subagents': 'must be checked by the consuming host',
            'runtime_environment': {'CLAUDE_PLUGIN_ROOT': str(plugin),
                                    'UNDERSTAND_NO_WORKTREE_REDIRECT': '1'},
            'source_arguments': ['--language', 'ko', '--no-auto-update'],
            'excluded_artifacts': ['.taskflow-kit/**', '.agents/**', '.taskflow/**', 'node_modules/**'],
            'preparation': 'Only if allowed: pnpm install --frozen-lockfile, then pnpm --filter @understand-anything/core build, in plugin_root. No preparation was executed.'}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='The actual completed task project')
    args = parser.parse_args(argv)
    print(json.dumps(status(args.root), ensure_ascii=False))
    return 0
