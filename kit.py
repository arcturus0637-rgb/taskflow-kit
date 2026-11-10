"""Portable entry point; all model/agent execution remains in the host."""
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('-h', '--help'):
        print('TaskFlow 1.3: install | board | check | evidence | verify-bundle | understand-status | agent-plan\n'
              'Run: python kit.py COMMAND --help')
        return 0
    command, rest = args[0], args[1:]
    try:
        if command == 'board':
            from taskflow.cli import main as board_main
            return board_main(rest)
        if command == 'install':
            from taskflow.install import main as install_main
            return install_main(rest)
        if command == 'understand-status':
            from taskflow.understand import main as understand_main
            return understand_main(rest)
        if command == 'agent-plan':
            from taskflow.models import main as models_main
            return models_main(rest)
        if command in ('check', 'evidence'):
            from taskflow.checks import main as check_main
            return check_main([command, *rest])
        if command == 'verify-bundle':
            from taskflow.install import verify_bundle
            from pathlib import Path
            result = verify_bundle(Path(__file__).resolve().parent)
            print(json.dumps({'ok': True, **result}, ensure_ascii=False))
            return 0
        raise ValueError('Unknown command: ' + command)
    except (ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
