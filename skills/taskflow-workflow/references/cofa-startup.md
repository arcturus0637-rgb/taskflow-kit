# COFA startup capability check

Use this checklist at the start of an approved, read-only discovery batch in the contest browser IDE (VSCode-like editor, terminal `codex`, and web preview). The contest build and its enabled features are not known in advance. Do not infer capabilities from this kit or another host.

## Check in order

1. **Read the actual assignment and applicable runtime/task policy first**, if available. Record the source and any limits on local inspection, terminal commands, browser use, files, models, or delegation. Do not inspect credentials, secrets, managed settings, or hidden platform state. The existing approval covers only its stated discovery scope; reuse it and do not ask again for work inside it. Follow the [decision policy](decision-policy.md) and [model routing policy](../../taskflow-parallel/references/model-routing.md), including the user's model whitelist, no Astra, and no automatic updates.
2. **Observe the supplied interface.** Record which editor, terminal, preview, browser, and native agent/message tools are visibly exposed. A browser or Hypothesis package in dependency metadata is evidence of a dependency only; it does not prove tests ran, access is permitted, or a service is available.
3. **Check `codex` only when the task rules permit it.** Capture the existing executable's version and help/capability listing if available. Do not install, update, change configuration, authenticate, or invoke a model. A CLI queue/help listing proves only that a command is listed, not that work was delivered or completed. Tab/Enter queue and steering behavior is version-dependent: report it only after observing it in this runtime. Otherwise mark it unknown.
4. **Determine delegation from actual native tool exposure and limits.** Only a visible, usable native child-agent facility and its observed concurrency limit establish native delegation. Distinguish parent input availability from child-agent concurrency. If supported, use only that approved native mode and honor the pinned model policy. If unsupported or unknown, work serially or name the specific blocked item. Never start extra model CLIs, spawn a daemon, edit global settings, install packages, or bypass platform limits. Two terminal tabs are not two automatically coordinated AI workers.
5. **Establish workspace and shared-resource facts only with safe permitted evidence.** Check whether workers truly share files using already visible paths or an approved harmless local marker. If writing a marker is not approved, leave sharing unknown. Separate variants need distinct, genuinely prefixed paths under the same approved board root. Check whether the task board database and required ports are shared before promising isolation. Do not assume separate tabs, terminals, or paths imply isolated workers or resources.
6. **Treat browser checks as conditional.** Use a web check only when the actual task needs it, contest policy allows it, and the required browser/runtime is already available. Otherwise use permitted manual inspection or API checks, or report the check blocked/unknown. Never silently install a browser, dependency, or testing tool.
7. **Report evidence by status.** Keep actual observations, user-reported information, documented-only claims, and unknowns separate. A file request record is not message delivery: this kit has no always-on service or cross-session message transport. Do not claim execution, testing, delegation, delivery, workspace sharing, or a limit from a listing or inference.

## Korean report template

```text
COFA 시작 점검
- 운영 모드: [확인된 native 위임 / 순차 진행 / 차단 항목]
- 실제 관찰: [환경·버전·도구·동시성·공유 자원; 출처와 허용 범위]
- 사용자 보고: [내용 또는 없음]
- 문서에만 기재됨: [내용 또는 없음]
- 미확인: [내용 또는 없음]
- 제약과 다음 조치: [확인된 한계, 순차 진행 항목 또는 명시적 차단]
- 사용자 결정 필요: [정말 남은 우선순위·범위 선택만; 없으면 없음]
```
