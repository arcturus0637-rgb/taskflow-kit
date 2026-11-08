"""Execute real checks; evidence becomes stale when watched sources change."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import subprocess
import uuid
from .paths import is_link

IGNORED = {'.git', '.taskflow', '__pycache__', '.pytest_cache', '.mypy_cache'}


def safe_path(root, name):
    if not name or PureWindowsPath(name).drive or Path(name).is_absolute():
        raise ValueError('Watch paths must be relative to the project')
    pieces = name.replace('\\', '/').split('/')
    if '..' in pieces:
        raise ValueError('Path escapes are not allowed')
    path = root.joinpath(*pieces)
    current = root
    for part in pieces:
        current = current / part
        if is_link(current):
            raise ValueError('Symbolic links and junctions are not watched: ' + name)
    if not path.resolve().is_relative_to(root):
        raise ValueError('Watch path escapes the project')
    return path


def fingerprint(root, watches):
    result = {}
    for name in watches:
        path = safe_path(root, name)
        relative = path.relative_to(root).as_posix() or '.'
        if not path.exists():
            result[relative] = 'missing'
        elif path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            result[relative + '/'] = 'directory'
            for folder, dirs, files in os.walk(path, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in IGNORED)
                for item in [*dirs, *sorted(files)]:
                    child = Path(folder) / item
                    if is_link(child):
                        raise ValueError('Symbolic link in watched directory: ' + str(child))
                    key = child.relative_to(root).as_posix()
                    result[key + '/' if child.is_dir() else key] = (
                        'directory' if child.is_dir()
                        else hashlib.sha256(child.read_bytes()).hexdigest())
        else:
            raise ValueError('Unsupported source type: ' + name)
    return dict(sorted(result.items()))


def validate_evidence(path, root, task_id):
    root = Path(root).resolve()
    try:
        evidence = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('Cannot read evidence: ' + str(exc)) from exc
    if not isinstance(evidence, dict) or evidence.get('schema_version') != 1:
        raise ValueError('Unrecognized evidence format')
    if evidence.get('task_id') != task_id or evidence.get('root') != str(root):
        raise ValueError('Evidence belongs to a different task or project')
    if evidence.get('returncode') != 0 or evidence.get('timed_out') is not False:
        raise ValueError('The recorded check did not pass')
    watches = evidence.get('watch')
    if not isinstance(watches, list) or not watches or not all(isinstance(x, str) for x in watches):
        raise ValueError('Evidence has no valid watched source paths')
    before, after = evidence.get('before'), evidence.get('after')
    if not isinstance(before, dict) or before != after:
        raise ValueError('Sources changed during the check')
    if fingerprint(root, watches) != after:
        raise ValueError('Evidence is stale: watched sources changed')
    if not isinstance(evidence.get('command'), list) or not evidence['command']:
        raise ValueError('Evidence has no command')
    log_path = Path(evidence.get('log_path', ''))
    if not log_path.is_file():
        raise ValueError('Evidence log is missing')
    if hashlib.sha256(log_path.read_bytes()).hexdigest() != evidence.get('log_sha256'):
        raise ValueError('Evidence log was changed')
    return evidence


def run_check(root, task_id, watches, command, timeout):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Project directory does not exist')
    if not task_id.strip() or not command or not watches:
        raise ValueError('A task, watched sources and an executable command are required')
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('Timeout must be a positive finite number')
    before = fingerprint(root, watches)
    storage = root / '.taskflow' / 'evidence'
    for part in (root / '.taskflow', storage):
        if is_link(part):
            raise ValueError('Evidence directory cannot be a symbolic link or junction')
    storage.mkdir(parents=True, exist_ok=True)
    identifier = uuid.uuid4().hex
    log_path, evidence_path = storage / (identifier + '.log'), storage / (identifier + '.json')
    timed_out, rc = False, None
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    with log_path.open('wb') as log:
        try:
            proc = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                    env=env, shell=False)
            try:
                rc = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                proc.wait()
                log.write(b'\n[TaskFlow] Direct process timed out and was stopped.\n')
        except OSError as exc:
            log.write(str(exc).encode('utf-8', errors='replace'))
    # Do not turn post-run source inspection failure into successful evidence.
    inspection_error = None
    try:
        after = fingerprint(root, watches)
    except (ValueError, OSError) as exc:
        after, inspection_error = {}, str(exc)
    evidence = {'schema_version': 1, 'task_id': task_id, 'root': str(root),
                'command': command, 'cwd': str(root), 'watch': watches,
                'returncode': rc, 'timed_out': timed_out,
                'before': before, 'after': after,
                'finished_at': datetime.now(timezone.utc).isoformat(),
                'log_path': str(log_path),
                'log_sha256': hashlib.sha256(log_path.read_bytes()).hexdigest(),
                'inspection_error': inspection_error}
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    passed = rc == 0 and not timed_out and before == after and not inspection_error
    return {'ok': passed, 'evidence': str(evidence_path), 'log': str(log_path),
            'returncode': rc, 'timed_out': timed_out,
            'sources_unchanged': before == after, 'inspection_error': inspection_error}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    check = subs.add_parser('check', help='Run an actual check without a shell')
    check.add_argument('--root', required=True)
    check.add_argument('--task', required=True)
    check.add_argument('--watch', action='append', required=True)
    check.add_argument('--timeout', type=float, default=120)
    check.add_argument('executable', nargs=argparse.REMAINDER)
    validate = subs.add_parser('evidence', help='Reject stale or failed evidence')
    validate.add_argument('--root', required=True)
    validate.add_argument('--task', required=True)
    validate.add_argument('--path', required=True)
    args = parser.parse_args(argv)
    if args.command == 'evidence':
        validate_evidence(args.path, args.root, args.task)
        print(json.dumps({'ok': True, 'evidence': str(Path(args.path).resolve())}, ensure_ascii=False))
        return 0
    executable = args.executable
    if executable and executable[0] == '--':
        executable = executable[1:]
    result = run_check(args.root, args.task, args.watch, executable, args.timeout)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['ok'] else 1
