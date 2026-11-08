"""A local cooperative task board. No model execution or message transport.

SQLite transactions serialize reservations across coordinator processes. Scope
reservations are conventions followed by cooperating workers, not OS write locks.
Finishing frees an execution slot; write/resource reservations last until integration.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import ntpath
from pathlib import Path
import sqlite3


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError(label + " must be nonempty text")
    return value


def _now():
    return datetime.now(timezone.utc).isoformat()


def _is_link(path):
    """Recognize NTFS junctions on Python 3.10 as well as symbolic links."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return path.is_symlink() or getattr(info, "st_reparse_tag", 0) in (0xA0000003, 0xA000000C)


def _covers(domain, scope):
    if domain.endswith("/"):
        return scope.rstrip("/") == domain[:-1] or scope.startswith(domain)
    return domain == scope


def _overlaps(left, right):
    return _covers(left, right) or _covers(right, left)


class Board:
    """Board rooted at an existing project directory; construction is read-only."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError("project root must be an existing directory")
        self.directory = self.root / ".taskflow"
        self.path = self.directory / "board.sqlite3"
        self._check_storage_path()

    def _check_storage_path(self):
        if not self.path.resolve().is_relative_to(self.root):
            raise ValueError("board storage escapes project root through a symlink")
        if _is_link(self.directory) or _is_link(self.path):
            raise ValueError("board storage must not be a symlink or junction")

    def _scope(self, value):
        _text(value, "scope")
        raw = value.replace("\\", "/")
        if raw.startswith("/") or ntpath.splitdrive(raw)[0]:
            raise ValueError("scope must be a relative project path: " + value)
        if any(char in raw for char in "*?[]:\x00"):
            raise ValueError("scope cannot contain wildcards, drive syntax, or streams: " + value)
        components = raw.split("/")
        if ".." in components:
            raise ValueError("scope cannot contain parent traversal: " + value)
        components = [part for part in components if part not in ("", ".")]
        if not components:
            raise ValueError("scope must name a file or directory inside the project")
        if any(part.endswith((".", " ")) for part in components):
            raise ValueError("scope components cannot end in a dot or space (Windows path aliases)")
        candidate = self.root.joinpath(*components)
        try:
            current = self.root
            for part in components:
                current = current / part
                if _is_link(current):
                    raise ValueError("scope must not traverse a symlink or junction: " + value)
            if not candidate.resolve().is_relative_to(self.root):
                raise ValueError("scope escapes project root through a symlink: " + value)
        except (OSError, RuntimeError) as error:
            raise ValueError("cannot safely resolve scope: " + value) from error
        return "/".join(components).casefold() + ("/" if raw.endswith("/") else "")

    def _scopes(self, values):
        scopes = sorted({self._scope(value) for value in values})
        if not scopes:
            raise ValueError("at least one write scope is required")
        return scopes

    @staticmethod
    def _resources(values):
        return sorted({_text(value, "resource").casefold() for value in values})

    def _connect(self, write=False):
        self._check_storage_path()
        if not self.path.is_file():
            raise ValueError("board is not initialized; run init first")
        if write:
            connection = sqlite3.connect(str(self.path), timeout=30, isolation_level=None)
        else:
            connection = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    @contextmanager
    def _transaction(self, write=False):
        connection = self._connect(write)
        try:
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _settings(connection):
        row = connection.execute("SELECT payload FROM settings WHERE id=1").fetchone()
        if row is None:
            raise ValueError("board is not initialized")
        return json.loads(row["payload"])

    def init(self, workers, mode="shared"):
        if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
            raise ValueError("workers must be a positive integer")
        if mode not in ("shared", "serial"):
            raise ValueError("mode must be shared or serial")
        config = {"workers": workers, "mode": mode, "capacity": 1 if mode == "serial" else workers}
        self._check_storage_path()
        if self.path.exists():
            with self._transaction() as connection:
                if self._settings(connection) != config:
                    raise ValueError("board already initialized with different settings")
            return self.status()
        self.directory.mkdir(exist_ok=True)
        connection = sqlite3.connect(str(self.path), timeout=30, isolation_level=None)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK (id=1), payload TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS agents (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL, agent TEXT, history TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS requests (key TEXT PRIMARY KEY, payload TEXT NOT NULL, task_id TEXT NOT NULL, target TEXT, delivery_status TEXT NOT NULL, receipt TEXT, history TEXT NOT NULL)")
            row = connection.execute("SELECT payload FROM settings WHERE id=1").fetchone()
            if row is not None and json.loads(row[0]) != config:
                raise ValueError("board already initialized with different settings")
            connection.execute("INSERT OR IGNORE INTO settings(id,payload) VALUES(1,?)", (_json(config),))
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.status()

    @staticmethod
    def _agent(row):
        return json.loads(row["payload"])

    @staticmethod
    def _task(row):
        task = json.loads(row["payload"])
        task.update(state=row["state"], agent=row["agent"], history=json.loads(row["history"]))
        # Routing is mutable coordination metadata; the original keyed payload
        # remains unchanged so retries can still compare the original request.
        for event in task["history"]:
            if event["action"] == "route":
                task["owner"] = event["owner"]
        return task

    def _get_task(self, connection, task_id):
        row = connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise ValueError("unknown task: " + task_id)
        return self._task(row)

    def _get_agent(self, connection, agent_id):
        row = connection.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
        if row is None:
            raise ValueError("unknown agent: " + agent_id)
        return self._agent(row)

    def register_agent(self, agent_id, target, scopes):
        payload = {"id": _text(agent_id, "agent id"), "target": _text(target, "native target"), "scopes": self._scopes(scopes)}
        with self._transaction(write=True) as connection:
            row = connection.execute("SELECT payload FROM agents WHERE id=?", (agent_id,)).fetchone()
            if row:
                if json.loads(row[0]) != payload:
                    raise ValueError("agent id already registered with a different payload: " + agent_id)
            else:
                connection.execute("INSERT INTO agents(id,payload) VALUES(?,?)", (agent_id, _json(payload)))
        return {"ok": True, "agent": payload}

    def _task_payload(self, task_id, title, scopes, accept, owner=None, depends=(), read=(), write=(), priority=50):
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise ValueError("priority must be an integer")
        dependencies = sorted({_text(item, "dependency id") for item in depends})
        if task_id in dependencies:
            raise ValueError("task cannot depend on itself")
        return {
            "id": _text(task_id, "task id"), "title": _text(title, "title"),
            "scopes": self._scopes(scopes), "accept": _text(accept, "acceptance criterion"),
            "owner": _text(owner, "owner") if owner is not None else None,
            "depends": dependencies, "read": self._resources(read), "write": self._resources(write),
            "priority": priority,
        }

    def _domain_covers(self, agent, scopes):
        return all(any(_covers(domain, scope) for domain in agent["scopes"]) for scope in scopes)

    def _insert_task(self, connection, payload):
        row = connection.execute("SELECT * FROM tasks WHERE id=?", (payload["id"],)).fetchone()
        if row:
            if json.loads(row["payload"]) != payload:
                raise ValueError("task key already has a different payload: " + payload["id"])
            return self._task(row)
        if payload["owner"] is not None:
            owner = self._get_agent(connection, payload["owner"])
            if not self._domain_covers(owner, payload["scopes"]):
                raise ValueError("owner domain does not include all task scopes")
        for dependency in payload["depends"]:
            self._get_task(connection, dependency)
        connection.execute("INSERT INTO tasks(id,payload,state,agent,history) VALUES(?,?,'pending',NULL,'[]')", (payload["id"], _json(payload)))
        return self._get_task(connection, payload["id"])

    def add(self, task_id, title, scopes, accept, owner=None, depends=(), read=(), write=(), priority=50):
        payload = self._task_payload(task_id, title, scopes, accept, owner, depends, read, write, priority)
        with self._transaction(write=True) as connection:
            task = self._insert_task(connection, payload)
        return {"ok": True, "task": task}

    def _claim_blockers(self, connection, task, agent):
        blockers = []
        if task["state"] != "pending":
            blockers.append("task is " + task["state"] + "; only pending tasks can be claimed")
        if task["owner"] is not None and task["owner"] != agent["id"]:
            blockers.append("task belongs to owner " + task["owner"])
        if not self._domain_covers(agent, task["scopes"]):
            blockers.append("agent " + agent["id"] + " domain does not include all write scopes")
        for scope in task["scopes"]:
            try:
                self._scope(scope)
            except ValueError as error:
                blockers.append(str(error))
        for dependency in task["depends"]:
            predecessor = self._get_task(connection, dependency)
            if predecessor["state"] not in ("integrated", "verified"):
                blockers.append("dependency " + dependency + " is " + predecessor["state"] + "; requires integrated or verified")
        running = [self._task(row) for row in connection.execute("SELECT * FROM tasks WHERE state='running'")]
        if len(running) >= self._settings(connection)["capacity"]:
            blockers.append("worker capacity is full")
        for other in running:
            if other["agent"] == agent["id"]:
                blockers.append("agent " + agent["id"] + " is busy with task " + other["id"])
        active = [self._task(row) for row in connection.execute("SELECT * FROM tasks WHERE state IN ('running','done')")]
        for other in active:
            if other["id"] == task["id"]:
                continue
            for scope in task["scopes"]:
                for held in other["scopes"]:
                    if _overlaps(scope, held):
                        blockers.append("write scope " + scope + " conflicts with " + other["id"] + ": " + held)
            conflicts = (set(task["write"]) & (set(other["read"]) | set(other["write"]))) | (set(task["read"]) & set(other["write"]))
            for resource in sorted(conflicts):
                blockers.append("resource " + resource + " conflicts with task " + other["id"])
        return list(dict.fromkeys(blockers))

    def _transition(self, connection, task, state, action, note, agent=None, evidence=None):
        event = {"action": action, "note": note, "at": _now()}
        if agent is not None:
            event["agent"] = agent
        if evidence is not None:
            event["evidence"] = evidence
        history = task["history"] + [event]
        worker = agent if state == "running" else (None if state == "pending" else task["agent"])
        connection.execute("UPDATE tasks SET state=?,agent=?,history=? WHERE id=?", (state, worker, _json(history), task["id"]))
        return self._get_task(connection, task["id"])

    def claim(self, task_id, agent_id):
        with self._transaction(write=True) as connection:
            task = self._get_task(connection, task_id)
            agent = self._get_agent(connection, agent_id)
            blockers = self._claim_blockers(connection, task, agent)
            if blockers:
                raise ValueError("; ".join(blockers))
            task = self._transition(connection, task, "running", "claim", "Explicit worker claim", agent_id)
        return {"ok": True, "task": task}

    def finish(self, task_id, agent_id, note):
        _text(note, "completion note")
        with self._transaction(write=True) as connection:
            task = self._get_task(connection, task_id)
            if task["state"] != "running" or task["agent"] != agent_id:
                raise ValueError("finish requires the task's running worker")
            task = self._transition(connection, task, "done", "finish", note, agent_id)
        return {"ok": True, "task": task}

    def integrate(self, task_id, note):
        _text(note, "actual integration action note")
        with self._transaction(write=True) as connection:
            task = self._get_task(connection, task_id)
            if task["state"] != "done":
                raise ValueError("integration requires worker-done state")
            task = self._transition(connection, task, "integrated", "integrate", note)
        return {"ok": True, "task": task}

    def verify(self, task_id, evidence):
        from .checks import validate_evidence

        with self._transaction(write=True) as connection:
            task = self._get_task(connection, task_id)
            if task["state"] != "integrated":
                raise ValueError("verification requires integrated state")
            validated = validate_evidence(evidence, self.root, task_id)
            task = self._transition(connection, task, "verified", "verify", "Successful current-source check evidence", evidence={"path": str(Path(evidence).resolve()), "record": validated})
        return {"ok": True, "task": task}

    def release(self, task_id, agent_id, stopped, reason):
        if not stopped:
            raise ValueError("release requires explicit confirmed stop (--stopped)")
        _text(reason, "release reason")
        with self._transaction(write=True) as connection:
            task = self._get_task(connection, task_id)
            if task["state"] != "running" or task["agent"] != agent_id:
                raise ValueError("release requires the task's running worker")
            task = self._transition(connection, task, "pending", "release", reason, agent_id)
        return {"ok": True, "task": task}

    def _request_record(self, row, connection):
        source = json.loads(row["payload"])
        task = self._get_task(connection, row["task_id"])
        payload = {
            "request_key": row["key"], "task_key": row["task_id"] ,
            "text": source["text"], "task": {key: value for key, value in task.items() if key not in ("state", "agent", "history")},
            "instruction": "Deduplicate request_key and task_key. Queue this task; claim only when eligible. A delivered receipt does not mean started or completed.",
        }
        return {
            "request_key": row["key"], "task_key": row["task_id"], "text": source["text"],
            "target": row["target"], "state": task["state"], "delivery_status": row["delivery_status"],
            "receipt": row["receipt"], "delivery_history": json.loads(row["history"]),
            "delivery_payload": payload,
        }

    def request(self, key, text, task_id, title, scopes, accept, owner=None, depends=(), read=(), write=(), priority=50):
        _text(key, "request key")
        _text(text, "raw request text")
        payload = self._task_payload(task_id, title, scopes, accept, owner, depends, read, write, priority)
        source = {"key": key, "text": text, "task": payload}
        with self._transaction(write=True) as connection:
            row = connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone()
            if row:
                if json.loads(row["payload"]) != source:
                    raise ValueError("request key already has a different payload: " + key)
            else:
                payload = dict(payload)
                if owner is None:
                    matches = [self._agent(item) for item in connection.execute("SELECT * FROM agents") if self._domain_covers(self._agent(item), payload["scopes"])]
                    if len(matches) == 1:
                        payload["owner"] = matches[0]["id"]
                task = self._insert_task(connection, payload)
                target = self._get_agent(connection, task["owner"])["target"] if task["owner"] is not None else None
                connection.execute("INSERT INTO requests(key,payload,task_id,target,delivery_status,receipt,history) VALUES(?,?,?,?,'pending',NULL,'[]')", (key, _json(source), task_id, target))
                row = connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone()
            record = self._request_record(row, connection)
            task = self._get_task(connection, row["task_id"])
        return {"ok": True, **record, "request": record, "task": task}

    def delivery(self, key, status, receipt=None):
        if status not in ("delivered", "unknown", "failed"):
            raise ValueError("delivery status must be delivered, unknown, or failed")
        if status == "delivered":
            _text(receipt, "successful native-tool receipt")
        with self._transaction(write=True) as connection:
            row = connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone()
            if row is None:
                raise ValueError("unknown request: " + key)
            if status == "delivered" and row["target"] is None:
                raise ValueError("unassigned request has no native delivery target")
            if row["delivery_status"] == "delivered":
                if status != "delivered" or row["receipt"] != receipt:
                    raise ValueError("delivered request is already acknowledged; cannot replace its receipt")
            else:
                history = json.loads(row["history"]) + [{"status": status, "receipt": receipt, "at": _now()}]
                connection.execute("UPDATE requests SET delivery_status=?,receipt=?,history=? WHERE key=?", (status, receipt, _json(history), key))
            record = self._request_record(connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone(), connection)
        return {"ok": True, "request": record}

    def route(self, key, owner):
        """Explicitly resolve a previously unassigned, still-pending request."""
        _text(key, "request key")
        _text(owner, "owner")
        with self._transaction(write=True) as connection:
            row = connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone()
            if row is None:
                raise ValueError("unknown request: " + key)
            task = self._get_task(connection, row["task_id"])
            if task["state"] != "pending" or row["delivery_status"] == "delivered":
                raise ValueError("routing requires a pending task and an undelivered request")
            agent = self._get_agent(connection, owner)
            if not self._domain_covers(agent, task["scopes"]):
                raise ValueError("owner domain does not include all task scopes")
            if task["owner"] is not None and task["owner"] != owner:
                raise ValueError("task is already assigned to a different owner")
            if row["target"] is not None and row["target"] != agent["target"]:
                raise ValueError("request is already routed to a different native target")
            if row["target"] is None:
                if task["owner"] is None:
                    history = task["history"] + [{"action": "route", "owner": owner, "note": "Explicit coordinator routing", "at": _now()}]
                    connection.execute("UPDATE tasks SET history=? WHERE id=?", (_json(history), task["id"]))
                history = json.loads(row["history"]) + [{"action": "route", "owner": owner, "target": agent["target"], "at": _now()}]
                connection.execute("UPDATE requests SET target=?,history=? WHERE key=?", (agent["target"], _json(history), key))
                row = connection.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone()
            record = self._request_record(row, connection)
            task = self._get_task(connection, row["task_id"])
        return {"ok": True, **record, "request": record, "task": task}

    def outbox(self):
        if not self.path.exists():
            return {"ok": True, "requests": []}
        with self._transaction() as connection:
            requests = [self._request_record(row, connection) for row in connection.execute("SELECT * FROM requests WHERE delivery_status != 'delivered' ORDER BY rowid")]
        return {"ok": True, "requests": requests}

    def status(self):
        if not self.path.exists():
            return {"ok": True, "state": {"initialized": False}, "tasks": [], "agents": [], "requests": [], "delivery": {"pending": 0, "unknown": 0, "failed": 0, "delivered": 0}}
        with self._transaction() as connection:
            config = self._settings(connection)
            tasks = [self._task(row) for row in connection.execute("SELECT * FROM tasks ORDER BY rowid")]
            agents = [self._agent(row) for row in connection.execute("SELECT * FROM agents ORDER BY rowid")]
            requests = [self._request_record(row, connection) for row in connection.execute("SELECT * FROM requests ORDER BY rowid")]
        counts = {status: sum(item["delivery_status"] == status for item in requests) for status in ("pending", "unknown", "failed", "delivered")}
        return {"ok": True, "state": {"initialized": True, **config}, "tasks": tasks, "agents": agents, "requests": requests, "delivery": counts}

    def ready(self):
        if not self.path.exists():
            return {"ok": True, "tasks": []}
        with self._transaction() as connection:
            agents = [self._agent(row) for row in connection.execute("SELECT * FROM agents ORDER BY id")]
            tasks = [self._task(row) for row in connection.execute("SELECT * FROM tasks WHERE state='pending'")]
            tasks.sort(key=lambda task: (task["priority"], task["id"]))
            for task in tasks:
                candidates = [agent for agent in agents if task["owner"] is None or agent["id"] == task["owner"]]
                by_agent = {agent["id"]: self._claim_blockers(connection, task, agent) for agent in candidates}
                eligible = [agent_id for agent_id, blockers in by_agent.items() if not blockers]
                blockers = [] if eligible else list(dict.fromkeys(reason for reasons in by_agent.values() for reason in reasons))
                if not candidates:
                    blockers = ["no registered agent is available for this task"]
                task.update(eligible=bool(eligible), eligible_agents=eligible, blockers=blockers, blockers_by_agent=by_agent)
        return {"ok": True, "tasks": tasks}
