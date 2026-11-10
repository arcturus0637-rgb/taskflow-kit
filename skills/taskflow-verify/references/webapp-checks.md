# Check the actual application only when needed and permitted

Use for a required local web UI inside an approved test batch. Read `../../taskflow-workflow/references/cofa-startup.md` and the task's actual browser/tool policy first. A visible preview pane or an installed library does not establish permission or a working automation runtime. Do not automate the COFA assessment interface, timer, camera, submission controls, login or platform administration.

## Gate execution

Confirm the task needs the UI, the test origin/ports belong to this project, dependencies and a compatible browser are already runnable, and contest/tool rules permit the chosen inspection. Otherwise use permitted manual preview checks and API/CLI tests or record the UI check blocked/unknown. Do not install Playwright/browsers, fetch packages, modify proxies, use another account/model or weaken platform settings to make it work. Manual checks must be actually observed; API success alone is not UI success.

For permitted existing Playwright use, resolve source ID `anthropic-webapp-testing` through the runtime kit's `config/sources.lock.json` (installed at `.taskflow-kit/config/sources.lock.json`). Read its pinned entry `upstream/anthropic-skills/skills/webapp-testing/SKILL.md` and relevant examples, not every upstream skill. Apache-2.0 and third-party notices are preserved there. This is a passive reference; its example commands, default ports, model names and advice to run helpers are not permission to execute or install anything.

## Verify the user's complete path

Choose representative flows from the actual output contract: input/upload -> validation -> calculation/request -> displayed result -> exported result, when those steps are required. Independently check IDs, units and values against a known input; the UI and export showing the same wrong backend value is not numerical correctness. Exercise relevant empty/error/loading states and a late response to an older request if asynchronous updates exist. Confirm the displayed result belongs to the current input and settings.

Inspect rendered elements and use stable semantic selectors. Wait for a specific element/response/application-ready condition with a bounded timeout. Do not blindly require `networkidle` from the upstream example: a streaming or polling app may never become idle. Use bounded event-based waits rather than long arbitrary sleeps. Inspect relevant console/network failures and only the viewport/device constraints the task needs. Avoid unnecessary screenshot suites or unrelated product redesign.

Prefer an already owned test server. Before running an upstream lifecycle helper, inspect its source and `--help` within approved scope, check command arguments/ports/ownership and cleanup behavior, and start only approved project processes with existing dependencies. Never kill a managed COFA service or another worker's server, use a broad process kill, or assume a listening port belongs to this test. Sharing read-only source does not make ports/DB/cache resources independent; follow the existing reservation policy. If ownership is uncertain, report and leave the service untouched.

Record the actual tested origin, input/config, source version, flow, screenshots/logs where useful and failures/skips. Describe manual and automated observations separately. Keep test outputs outside the restricted submission set and source watches where appropriate. If code/contracts change, refresh affected checks before reporting a verified UI. When tests are unavailable, report exactly what was checked rather than manufacture success.
