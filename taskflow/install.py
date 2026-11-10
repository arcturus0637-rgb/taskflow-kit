"""Conservative project-local registration; never edit existing instructions."""
import argparse
import hashlib
import json
from pathlib import Path
import os
from .paths import is_link

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'__pycache__', '.git', '.taskflow', '.pytest_cache', 'node_modules', 'dist', '.pnpm-store', '.ua', '.understand-anything'}
RUNTIME_DIRS = ('taskflow', 'skills', 'upstream', 'config', 'docs', 'tests', 'scripts')
RUNTIME_FILES = ('kit.py', 'README.ko.md', 'LICENSE', '.gitattributes', 'bundle-lock.json')


def source_files(source):
    files = [source / name for name in RUNTIME_FILES if (source / name).is_file()]
    for name in RUNTIME_DIRS:
        directory = source / name
        if directory.exists():
            files.extend(p for p in directory.rglob('*') if p.is_file()
                         and not EXCLUDED.intersection(p.relative_to(source).parts))
    return sorted(files)


def reject_links(root, target):
    current = root
    for part in target.relative_to(root).parts:
        current = current / part
        if is_link(current):
            raise ValueError('Install target contains a symbolic link or junction: ' + str(current))
        if current.exists() and current != target and not current.is_dir():
            raise ValueError('Install parent is not a directory: ' + str(current))


def install(project, source=ROOT, dry_run=False):
    root, source = Path(project).resolve(), Path(source).resolve()
    if not root.is_dir():
        raise ValueError('Project directory does not exist')
    if root == source or root.is_relative_to(source):
        raise ValueError('Install into the actual task project, outside the source kit')
    skills = sorted(p for p in (source / 'skills').iterdir() if p.is_dir())
    required = {'taskflow-workflow', 'taskflow-brief', 'taskflow-model', 'taskflow-improve',
                'taskflow-parallel', 'taskflow-inbox', 'taskflow-verify', 'understand'}
    if not required.issubset({p.name for p in skills}) or not all((p / 'SKILL.md').is_file() for p in skills):
        raise ValueError('The source pack is missing complete required skills')
    required_references = ('taskflow-workflow/references/decision-policy.md',
                           'taskflow-model/references/method-selection.md',
                           'taskflow-improve/references/experiment-record.md',
                           'taskflow-parallel/references/model-routing.md',
                           'taskflow-parallel/references/model-policy.json')
    if not all((source / 'skills' / name).is_file() for name in required_references):
        raise ValueError('The source pack is missing required skill references')
    manifest = source / 'bundle-lock.json'
    if manifest.exists():
        verify_bundle(source)
    mapping = [(p, root / '.taskflow-kit' / p.relative_to(source)) for p in source_files(source)]
    for skill in skills:
        for p in skill.rglob('*'):
            if p.is_file() and not EXCLUDED.intersection(p.relative_to(skill).parts):
                mapping.append((p, root / '.agents' / 'skills' / skill.name / p.relative_to(skill)))
    writes, skipped = [], 0
    # Inspect the entire plan before writing any destination files.
    for src, dst in mapping:
        if src.is_symlink():
            raise ValueError('Source symlinks are not allowed: ' + str(src))
        reject_links(root, dst)
        data = src.read_bytes()
        if dst.exists():
            if not dst.is_file() or dst.read_bytes() != data:
                raise ValueError('Existing file differs; nothing overwritten: ' + str(dst))
            skipped += 1
        else:
            writes.append((dst, data))
    if not dry_run:
        for dst, data in writes:
            reject_links(root, dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                with dst.open('xb') as handle:
                    handle.write(data)
            except FileExistsError:
                if dst.read_bytes() != data:
                    raise ValueError('Concurrent install conflict; existing file preserved: ' + str(dst))
    return {'ok': True, 'dry_run': dry_run, 'project': str(root),
            'files_to_write': len(writes), 'identical_files': skipped,
            'skills': [p.name for p in skills], 'agents_md': 'preserved; never edited',
            'next': 'Use $taskflow-workflow in the task project; discuss and approve the work batch first. Native subagents must be available separately.'}


def verify_bundle(source):
    source = Path(source).resolve()
    manifest = source / 'bundle-lock.json'
    if not manifest.is_file():
        raise ValueError('bundle-lock.json is missing')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('files'), dict):
        raise ValueError('Invalid bundle manifest')
    actual = {p.relative_to(source).as_posix() for p in source_files(source)
              if p.name != 'bundle-lock.json'}
    if actual != set(data['files']):
        raise ValueError('Bundle file inventory does not match the manifest')
    count = 0
    for name, digest in data['files'].items():
        p = source / name
        if not p.resolve().is_relative_to(source) or p.is_symlink():
            raise ValueError('Unsafe manifest path: ' + name)
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            raise ValueError('Bundle integrity mismatch: ' + name)
        count += 1
    return {'verified_files': count, 'version': data.get('version')}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    result = install(args.project, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0
