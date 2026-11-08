"""Behavioral CLI tests, including real competing Python processes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONPATH=str(PACKAGE))

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "taskflow.cli", "--root", str(self.root), *args],
            cwd=PACKAGE, env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=25,
        )
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("CLI must emit machine-readable JSON: " + result.stdout + result.stderr)
        self.assertEqual(data["ok"], ok, data)
        return data

    def init(self, workers=3, mode="shared"):
        return self.cli("init", "--workers", str(workers), "--mode", mode)

    def agent(self, name, *scopes):
        args = ["agent", "--id", name, "--target", "native-" + name]
        for scope in scopes or ("src/",):
            args += ["--scope", scope]
        return self.cli(*args)

    def add(self, name, scope="src/a.py", owner=None, after=(), read=(), write=(), priority=50, ok=True):
        args = ["add", "--id", name, "--title", "Task " + name, "--scope", scope, "--accept", "Check behavior", "--priority", str(priority)]
        if owner:
            args += ["--owner", owner]
        for key, values in (("--depends", after), ("--read", read), ("--write", write)):
            for value in values:
                args += [key, value]
        return self.cli(*args, ok=ok)

    def request(self, key="u1", task="next", owner=None, after=(), scope="src/next.py", text="추가 요청: 동작을 확인해 줘", ok=True):
        args = ["request", "--key", key, "--text", text, "--task", task, "--title", "Next work", "--scope", scope, "--accept", "Next behavior"]
        if owner:
            args += ["--owner", owner]
        for item in after:
            args += ["--after", item]
        return self.cli(*args, ok=ok)

    def claim(self, task, agent, ok=True):
        return self.cli("claim", "--task", task, "--agent", agent, ok=ok)

    def finish(self, task, agent):
        return self.cli("finish", "--task", task, "--agent", agent, "--note", "Work executed")

    def integrate(self, task):
        return self.cli("integrate", "--task", task, "--note", "Reviewed actual result and applied it")

    def ready(self):
        return {t["id"]: t for t in self.cli("ready")["tasks"]}

    def directory_link(self, link, target):
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            if os.name != "nt":
                self.skipTest("Symlink unavailable: " + str(error))
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, timeout=10)
            if result.returncode:
                self.skipTest("Neither symlink nor NTFS junction is available")

    def test_read_commands_and_invalid_commands_do_not_initialize_state(self):
        self.assertFalse(self.cli("status")["state"]["initialized"])
        self.assertEqual(self.cli("ready")["tasks"], [])
        self.assertEqual(self.cli("outbox")["requests"], [])
        self.cli("claim", "--task", "absent", "--agent", "absent", ok=False)
        self.cli("init", "--workers", "0", "--mode", "shared", ok=False)
        self.cli("nonexistent-command", ok=False)
        self.assertFalse((self.root / ".taskflow").exists())

    def test_cli_reopens_persistent_unicode_state(self):
        self.init()
        self.agent("a")
        self.add("t")
        self.claim("t", "a")
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "running")
        self.finish("t", "a")
        self.integrate("t")
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "integrated")

    def test_idempotent_task_and_request_reject_changed_payload_without_mutation(self):
        self.init()
        self.agent("a")
        self.add("t")
        self.add("t")
        self.add("t", scope="src/other.py", ok=False)
        first = self.request()
        second = self.request()
        self.assertEqual(first["request_key"], second["request_key"])
        self.assertEqual(first["delivery_payload"], second["delivery_payload"])
        self.request(text="changed original request", ok=False)
        state = self.cli("status")
        self.assertEqual(len(state["tasks"]), 2)
        self.assertEqual(len(state["requests"]), 1)
        self.assertEqual(state["requests"][0]["text"], "추가 요청: 동작을 확인해 줘")

    def test_busy_owner_and_done_dependency_do_not_start_next_task(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.add("current", owner="a")
        self.claim("current", "a")
        request = self.request(owner="a", after=("current",))
        self.assertEqual(request["target"], "native-a")
        self.assertEqual(request["state"], "pending")
        self.claim("next", "a", ok=False)
        self.claim("next", "b", ok=False)
        self.assertFalse(self.ready()["next"]["eligible"])
        self.finish("current", "a")
        self.claim("next", "a", ok=False)
        self.integrate("current")
        self.assertTrue(self.ready()["next"]["eligible"])
        self.claim("next", "a")

    def test_unique_domain_route_only_and_no_fake_unassigned_target(self):
        self.init()
        self.agent("a", "src/a/")
        one = self.request(scope="src/a/file.py")
        self.assertEqual(one["target"], "native-a")
        self.agent("b", "src/a/")
        two = self.request(key="u2", task="two", scope="src/a/second.py")
        self.assertIsNone(two["target"])
        self.assertIsNone(two["task"]["owner"])
        three = self.request(key="u3", task="three", scope="docs/file.md")
        self.assertIsNone(three["target"])
        self.request(key="bad", task="bad", owner="missing", ok=False)
        self.assertEqual(len(self.cli("status")["requests"]), 3)

    def test_inferred_request_retry_stays_stable_when_registration_changes(self):
        self.init()
        self.agent("a")
        first = self.request()
        self.agent("b")
        self.assertEqual(first["target"], self.request()["target"])

    def test_explicit_route_resolves_ambiguous_request_without_changing_original(self):
        self.init()
        self.agent("a")
        self.agent("b")
        original = self.request()
        self.assertIsNone(original["target"])
        routed = self.cli("route", "--key", "u1", "--owner", "a")
        self.assertEqual(routed["target"], "native-a")
        self.assertEqual(routed["task"]["owner"], "a")
        self.assertEqual(routed["request_key"], original["request_key"])
        self.assertEqual(routed["task_key"], original["task_key"])
        retry = self.request()
        self.assertEqual(retry["text"], original["text"])
        self.assertEqual(retry["delivery_payload"], routed["delivery_payload"])
        repeated = self.cli("route", "--key", "u1", "--owner", "a")
        self.assertEqual(repeated["task"]["history"], routed["task"]["history"])
        self.cli("route", "--key", "u1", "--owner", "b", ok=False)
        self.claim("next", "b", ok=False)
        self.cli("delivery", "--key", "u1", "--status", "delivered", "--receipt", "native successful receipt")
        self.assertEqual(self.cli("outbox")["requests"], [])
        self.claim("next", "a")

    def test_route_rejects_unknown_noncovering_owner_and_active_task(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.agent("outside", "docs/")
        self.request()
        self.cli("route", "--key", "u1", "--owner", "missing", ok=False)
        self.cli("route", "--key", "u1", "--owner", "outside", ok=False)
        self.assertIsNone(self.cli("outbox")["requests"][0]["target"])
        self.claim("next", "a")
        self.cli("route", "--key", "u1", "--owner", "a", ok=False)
        self.assertIsNone(self.cli("status")["requests"][0]["target"])

    def test_ambiguous_request_can_only_be_claimed_by_covering_domain(self):
        self.init()
        self.agent("a", "src/")
        self.agent("b", "src/")
        self.agent("c", "docs/")
        self.request()
        self.claim("next", "c", ok=False)
        self.claim("next", "a")

    def test_unknown_and_failed_delivery_remain_durable_and_do_not_start_work(self):
        self.init()
        self.agent("a")
        self.request()
        self.cli("delivery", "--key", "u1", "--status", "delivered", ok=False)
        self.cli("delivery", "--key", "u1", "--status", "unknown", "--receipt", "native call timed out")
        item = self.cli("outbox")["requests"][0]
        self.assertEqual(item["delivery_status"], "unknown")
        self.assertEqual(item["request_key"], "u1")
        self.assertEqual(item["task_key"], "next")
        self.cli("delivery", "--key", "u1", "--status", "failed", "--receipt", "native tool rejected target")
        self.assertEqual(self.cli("outbox")["requests"][0]["delivery_status"], "failed")
        self.cli("delivery", "--key", "u1", "--status", "delivered", "--receipt", "successful native-tool receipt #123")
        self.assertEqual(self.cli("outbox")["requests"], [])
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "pending")

    def test_delivery_without_registered_target_cannot_be_delivered(self):
        self.init()
        self.request()
        self.cli("delivery", "--key", "u1", "--status", "delivered", "--receipt", "claimed receipt", ok=False)

    def test_ready_skips_blocked_head_of_line(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.add("active", "src/shared/", owner="a")
        self.claim("active", "a")
        self.add("blocked", "src/shared/file.py", priority=1)
        self.add("ready", "src/independent.py", priority=90)
        tasks = self.ready()
        self.assertFalse(tasks["blocked"]["eligible"])
        self.assertTrue(tasks["blocked"]["blockers"])
        self.assertTrue(tasks["ready"]["eligible"])
        self.claim("ready", "b")

    def test_prefix_scope_case_separator_normalization_and_boundary(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.add("directory", "SRC\\Folder\\")
        self.claim("directory", "a")
        self.add("inside", "src/folder/a.py")
        self.claim("inside", "b", ok=False)
        self.add("sibling", "src/folder-two/a.py")
        self.claim("sibling", "b")

    def test_scope_escapes_and_wildcards_are_rejected_atomically(self):
        self.init()
        self.agent("a")
        for index, scope in enumerate(("../escape", "/absolute", "C:\\escape", "\\\\host\\share", "src/*", "src/?.py", "src/[x]", "src/../../escape", ".", "src/name:stream")):
            with self.subTest(scope=scope):
                self.add("bad" + str(index), scope, ok=False)
        self.assertEqual(self.cli("status")["tasks"], [])

    def test_windows_dot_and_space_aliases_cannot_bypass_active_scope(self):
        self.init()
        self.agent("a")
        self.agent("b")
        (self.root / "src").mkdir()
        (self.root / "src" / "one.py").write_text("actual file", encoding="utf-8")
        self.add("canonical", "src/one.py")
        self.claim("canonical", "a")
        aliases = ("src/one.py.", "src/one.py ", "src./one.py", "src /one.py")
        for index, alias in enumerate(aliases):
            with self.subTest(alias=alias):
                self.add("alias" + str(index), alias, ok=False)
        self.assertEqual(len(self.cli("status")["tasks"]), 1)

    def test_existing_symlink_scope_cannot_escape_project(self):
        self.init()
        with tempfile.TemporaryDirectory() as outside:
            self.directory_link(self.root / "link", outside)
            self.add("escape", "link/file.py", ok=False)

    def test_internal_symlink_or_junction_cannot_create_alias_reservations(self):
        self.init()
        target = self.root / "actual"
        target.mkdir()
        self.directory_link(self.root / "alias", target)
        self.add("alias", "alias/file.py", ok=False)

    def test_state_directory_symlink_or_junction_is_rejected_without_mutation(self):
        target = self.root / "storage"
        target.mkdir()
        self.directory_link(self.root / ".taskflow", target)
        self.cli("init", "--workers", "2", "--mode", "shared", ok=False)
        self.assertEqual(list(target.iterdir()), [])

    def test_scope_becoming_external_link_after_add_blocks_claim(self):
        self.init()
        self.agent("a")
        self.add("one", "src/new/file.py")
        (self.root / "src").mkdir()
        with tempfile.TemporaryDirectory() as outside:
            self.directory_link(self.root / "src" / "new", outside)
            self.claim("one", "a", ok=False)
            self.assertFalse(self.ready()["one"]["eligible"])

    def test_board_verify_accepts_only_successful_current_task_evidence(self):
        from taskflow.checks import run_check

        self.init()
        self.agent("a")
        self.add("one")
        source = self.root / "source.txt"
        source.write_text("current source", encoding="utf-8")
        passed = run_check(self.root, "one", ["source.txt"], [sys.executable, "-c", "print('actual check')"], 10)
        self.cli("verify", "--task", "one", "--evidence", passed["evidence"], ok=False)
        self.claim("one", "a")
        self.finish("one", "a")
        self.integrate("one")
        wrong_task = run_check(self.root, "another", ["source.txt"], [sys.executable, "-c", "print('check')"], 10)
        self.cli("verify", "--task", "one", "--evidence", wrong_task["evidence"], ok=False)
        failed = run_check(self.root, "one", ["source.txt"], [sys.executable, "-c", "raise SystemExit(3)"], 10)
        self.cli("verify", "--task", "one", "--evidence", failed["evidence"], ok=False)
        source.write_text("changed source", encoding="utf-8")
        self.cli("verify", "--task", "one", "--evidence", passed["evidence"], ok=False)
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "integrated")
        current = run_check(self.root, "one", ["source.txt"], [sys.executable, "-c", "print('actual current check')"], 10)
        result = self.cli("verify", "--task", "one", "--evidence", current["evidence"])
        self.assertEqual(result["task"]["state"], "verified")

    def test_serial_mode_capacity_is_one(self):
        self.init(workers=9, mode="serial")
        self.agent("a")
        self.agent("b")
        self.add("one", "src/one.py")
        self.add("two", "src/two.py")
        self.claim("one", "a")
        self.claim("two", "b", ok=False)
        self.finish("one", "a")
        self.claim("two", "b")

    def test_readers_coexist_and_writer_waits_until_integration(self):
        self.init()
        for name in ("a", "b", "c"):
            self.agent(name)
        self.add("read1", "src/one.py", read=("public-api",))
        self.add("read2", "src/two.py", read=("public-api",))
        self.add("write", "src/three.py", write=("public-api",))
        self.claim("read1", "a")
        self.claim("read2", "b")
        self.claim("write", "c", ok=False)
        self.finish("read1", "a")
        self.finish("read2", "b")
        self.claim("write", "c", ok=False)
        self.integrate("read1")
        self.integrate("read2")
        self.claim("write", "c")

    def test_scope_reservation_survives_worker_done_until_integrated(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.add("one")
        self.add("two")
        self.claim("one", "a")
        self.finish("one", "a")
        self.claim("two", "b", ok=False)
        self.integrate("one")
        self.claim("two", "b")

    def test_release_requires_confirmed_stop_and_preserves_reason(self):
        self.init()
        self.agent("a")
        self.add("one")
        self.claim("one", "a")
        self.cli("release", "--task", "one", "--agent", "a", "--reason", "stopping", ok=False)
        self.cli("release", "--task", "one", "--agent", "a", "--stopped", "--reason", "", ok=False)
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "running")
        task = self.cli("release", "--task", "one", "--agent", "a", "--stopped", "--reason", "Native worker confirmed stopped")["task"]
        self.assertEqual(task["state"], "pending")
        self.assertIn("Native worker confirmed stopped", json.dumps(task))

    def test_invalid_transition_and_wrong_worker_are_atomic(self):
        self.init()
        self.agent("a")
        self.agent("b")
        self.add("one")
        self.cli("integrate", "--task", "one", "--note", "not done", ok=False)
        self.claim("one", "a")
        self.cli("finish", "--task", "one", "--agent", "b", "--note", "wrong worker", ok=False)
        self.assertEqual(self.cli("status")["tasks"][0]["state"], "running")

    def test_dependency_must_exist_and_task_cannot_depend_on_itself(self):
        self.init()
        self.add("missing", after=("unknown",), ok=False)
        self.add("self", after=("self",), ok=False)
        self.assertEqual(self.cli("status")["tasks"], [])

    def test_agent_registration_is_idempotent_and_preserves_target(self):
        self.init()
        self.agent("a")
        self.agent("a")
        self.cli("agent", "--id", "a", "--target", "another-target", "--scope", "src/", ok=False)
        self.assertEqual(len(self.cli("status")["agents"]), 1)

    def test_real_multiprocess_same_scope_claim_has_exactly_one_winner(self):
        self.init(workers=4)
        for name in ("a", "b", "c", "d"):
            self.agent(name)
            self.add(name, "src/shared.py")
        code = "import sys; from taskflow.cli import main; print('ready', flush=True); sys.stdin.readline(); sys.exit(main(sys.argv[1:]))"
        children = []
        try:
            for name in ("a", "b", "c", "d"):
                child = subprocess.Popen(
                    [sys.executable, "-X", "utf8", "-c", code, "--root", str(self.root), "claim", "--task", name, "--agent", name],
                    cwd=PACKAGE, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8",
                )
                children.append(child)
            for child in children:
                self.assertEqual(child.stdout.readline().strip(), "ready")
            for child in children:
                child.stdin.write("go\n")
                child.stdin.flush()
            results = [child.communicate(timeout=25) for child in children]
            self.assertEqual(sorted(child.returncode for child in children), [0, 2, 2, 2], results)
            self.assertEqual(sum(task["state"] == "running" for task in self.cli("status")["tasks"]), 1)
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                    child.communicate()


if __name__ == "__main__":
    unittest.main()
