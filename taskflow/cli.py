"""Machine-readable board CLI. All message sending belongs to the coordinator."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys

from .board import Board


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def _task_arguments(parser, request=False):
    parser.add_argument("--task" if request else "--id", dest="task_id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--scope", dest="scopes", action="append", required=True)
    parser.add_argument("--accept", required=True)
    parser.add_argument("--owner")
    parser.add_argument("--after" if request else "--depends", dest="depends", action="append", default=[])
    parser.add_argument("--read", action="append", default=[])
    parser.add_argument("--write", action="append", default=[])
    parser.add_argument("--priority", type=int, default=50)


def _parser():
    parser = _Parser(description="Transactional local task board")
    parser.add_argument("--root", required=True)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    init = commands.add_parser("init")
    init.add_argument("--workers", type=int, required=True)
    init.add_argument("--mode", choices=("shared", "serial"), required=True)
    agent = commands.add_parser("agent")
    agent.add_argument("--id", dest="agent_id", required=True)
    agent.add_argument("--target", required=True)
    agent.add_argument("--scope", dest="scopes", action="append", required=True)
    _task_arguments(commands.add_parser("add"))
    request = commands.add_parser("request")
    request.add_argument("--key", required=True)
    request.add_argument("--text", required=True)
    _task_arguments(request, request=True)
    for name in ("claim", "finish", "release"):
        command = commands.add_parser(name)
        command.add_argument("--task", dest="task_id", required=True)
        command.add_argument("--agent", dest="agent_id", required=True)
        if name == "finish":
            command.add_argument("--note", required=True)
        if name == "release":
            command.add_argument("--stopped", action="store_true")
            command.add_argument("--reason", required=True)
    integrate = commands.add_parser("integrate")
    integrate.add_argument("--task", dest="task_id", required=True)
    integrate.add_argument("--note", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--task", dest="task_id", required=True)
    verify.add_argument("--evidence", required=True)
    for name in ("ready", "status", "outbox"):
        commands.add_parser(name)
    route = commands.add_parser("route")
    route.add_argument("--key", required=True)
    route.add_argument("--owner", required=True)
    delivery = commands.add_parser("delivery")
    delivery.add_argument("--key", required=True)
    delivery.add_argument("--status", choices=("delivered", "unknown", "failed"), required=True)
    delivery.add_argument("--receipt")
    return parser


def main(argv=None):
    """Return 0 for success or 2 for errors; emit one UTF-8 JSON record."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args = vars(_parser().parse_args(argv))
        board = Board(args.pop("root"))
        command = args.pop("command")
        method = board.register_agent if command == "agent" else getattr(board, command)
        result = method(**args)
        code = 0
    except (ValueError, OSError, sqlite3.Error) as error:
        result = {"ok": False, "error": str(error)}
        code = 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
