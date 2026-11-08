# 최종 결과물을 이해하는 단계

Understand Anything은 과제를 처음 요약하는 도구로 강제하지 않는다. 먼저 실제 결과물을 만들고 통합·검증한 뒤, 그 **완성된 결과물**에 적용한다. 사용자가 결과를 직접 설명하고 수정할 수 있도록 돕는 단계다.

## 기본 흐름

`과제 파악 → 구현·병렬 작업 → 통합·검증 → Understand Anything → 한국어 결과물 설명 → 최종 전달`

최종 설명에는 실제 목표·사용 방법·입력에서 출력까지의 흐름·중요한 파일과 관계·선택한 알고리즘이나 설계의 이유·실행한 검사·한계를 담는다. 결과물 옆의 `UNDERSTAND.ko.md`가 기본 설명 파일이며 제출 파일이 제한된 과제에서는 제출 묶음 바깥에 둔다.

소스와 다른 가상의 구조를 설명하거나 구현하지 않은 기능을 넣지 않는다. 기존 실행 근거를 참고하고, 그래프를 만든 뒤 구현이 바뀌면 설명과 관련 검사도 갱신한다. 코드가 없는 산출물은 실제 내용·구조·작성 방법을 설명하고 부적절한 소프트웨어 그래프를 억지로 만들지 않는다.

## 사용 요청

```text
완성된 이 결과물에 $understand를 적용해줘.
내가 직접 설명할 수 있도록 전체 구조, 입력에서 출력까지의 흐름,
핵심 알고리즘과 선택 이유, 실제 검증 결과와 한계를 한국어로 알려줘.
실제 파일과 근거를 연결하고, 가능한 경우 원본 지식 그래프와 탐색 순서도 제공해줘.
```

`$taskflow-workflow`에도 이 마지막 단계가 연결되어 있다. 과제의 최종 제출 이후 AI 사용이 제한된다면 그 이전의 허용된 작업 단계에서 수행한다.

## 원본과 준비 상태

원본 저장소는 [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)이며 커밋 `a6ea4024767df85ce4f99140d4f12ecfc5a81eb6`을 보존했다. 원본 스킬 9개·분석 에이전트·스크립트·코어·대시보드 소스가 함께 들어 있다.

```text
python .taskflow-kit/kit.py understand-status --root PROJECT
```

이 명령은 실제 프로젝트와 원본 경로, Node/pnpm 버전, 코어 빌드 상태를 확인한다. 분석·그래프 생성·모델 호출·패키지 설치는 하지 않는다. 프로젝트를 새로 만들거나 Git 훅을 등록하지도 않는다.

원본 그래프 파이프라인에는 Node.js ≥22, pnpm ≥10과 빌드한 코어가 필요하다. 패키지 설치가 허용되는 환경에서만 status의 `plugin_root` 폴더를 cwd로 하여 다음을 실행한다.

```text
pnpm install --frozen-lockfile
pnpm --filter @understand-anything/core build
```

의존성·빌드 결과는 배포물에 미리 설치하지 않았다. 준비가 안 되거나 환경에서 설치를 허용하지 않으면 구체적인 이유를 알리고, 그래프 실행과 구분한 실제 소스 기반 한국어 설명을 제공한다. 설치·준비 상태를 그래프 완성으로 표시하지 않는다.

## 원본 연결 규칙

- 원본 위치는 `PROJECT/.taskflow-kit/upstream/understand-anything/understand-anything-plugin`이다. 스킬 사본의 상대 경로를 추측하지 않고 `understand-status`가 반환하는 실제 원본을 읽는다.
- 원본의 `<SKILL_DIR>`는 `.agents/skills/understand` 연결 스킬이 아니라 원본 `skills/understand` 디렉터리다. `CLAUDE_PLUGIN_ROOT`는 해당 분석 호출에만 적용한다.
- `UNDERSTAND_NO_WORKTREE_REDIRECT=1`로 다른 작업 사본이나 메인 저장소로 이동하지 않는다. 분석 대상은 실제 완성된 과제 폴더다.
- 기본 원본 인자는 `--language ko --no-auto-update`다. 저장소 전체가 아니라 필요한 완성 범위를 선택하고 `.taskflow-kit`, `.agents`, `.taskflow`, 의존성과 임시 그래프 파일은 분석 대상에서 제외한다.
- 다른 understand-* 스킬을 참조하면 같은 원본 소스의 해당 문서를 읽는다. 원본 9개를 전부 별도 발견 스킬로 설치한 것으로 가정하지 않는다.
- 실제 native 에이전트가 제공될 때만 원본의 병렬 분석을 실행한다. 작업자는 최종 소스를 읽고 배정된 그래프 중간 파일만 쓴다. 자동 Git 훅·외부 업로드·다른 모델 설치는 수행하지 않는다.
- 실제 그래프는 `.ua/knowledge-graph.json`에 저장하고 기존 `.understand-anything` 데이터 폴더가 있으면 유지한다. 원본 검증과 경고를 확인한다. 대시보드는 사용자가 원하고 실행 준비가 된 경우에 연다.

이 팩 자체를 읽는 데에는 [소스에 근거한 구조 설명](UNDERSTAND.ko.md)도 제공한다. 해당 문서는 원본 그래프 생성 실행 결과와 구분한다.
