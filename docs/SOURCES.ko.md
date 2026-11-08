# TaskFlow가 재사용한 공개 원본

TaskFlow는 작업 보드·설치·요청 전달·검증 기록을 새로 연결하고, 아래 공개 문서를 조건에 맞게 참고한다. 원본을 전체 실행 프레임워크로 설치하지 않는다. 활성 어댑터는 `taskflow-workflow`, `taskflow-brief`, `taskflow-parallel`, `taskflow-inbox`, `taskflow-verify` 다섯 개와 `understand` 연결 스킬 하나이며, `upstream/`의 원본은 필요한 부분을 읽는 참고 자료다.

기본 세 저장소에서 26개 파일, 총 85,550바이트를 선별했다. v1.1에는 Understand Anything 고정 소스 385개를 더해 네 저장소의 원본 파일 총 411개를 포함한다. 이 수치는 원본 파일과 해당 라이선스만 포함한다. 최신판이라는 주장은 하지 않는다. 고정 커밋·원본 경로·로컬 경로·파일별 SHA-256·Git blob SHA-1·라이선스는 [sources.lock.json](../config/sources.lock.json)에 기록했다.

## 고정 출처와 라이선스

| 출처 | 고정 커밋 | 포함 내용 | 보존한 라이선스 |
|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b) | `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` | systematic-debugging 전체 디렉터리, verification-before-completion | [MIT, Jesse Vincent](../upstream/superpowers/LICENSE) |
| [mattpocock/skills](https://github.com/mattpocock/skills/tree/a496f5513d4a4cf889bc48e189e579f4b0bdf6aa) | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | code-review, domain-modeling, to-spec, to-tickets의 전체 디렉터리 | [MIT, Matt Pocock](../upstream/matt-pocock/LICENSE) |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/f8c5e7a1dcb71b10cb74586224b5401f3de5db28/plugins/code-simplifier) | `f8c5e7a1dcb71b10cb74586224b5401f3de5db28` | code-simplifier 에이전트 원문 | [Apache-2.0](../upstream/code-simplifier/plugins/code-simplifier/LICENSE) |

원본의 저작권·라이선스 문구를 그대로 보존했다. Anthropic 고정 커밋의 저장소 루트와 code-simplifier 디렉터리에는 별도 `NOTICE` 파일이 없음을 확인했다. 선택한 자료에는 라이선스 파일의 부재로 보류한 항목이 없다. TaskFlow 자체 라이선스가 이 원본들의 라이선스를 대체하지 않는다.

## 언제 무엇을 읽는가

아래 경로는 배포 묶음 루트를 기준으로 한다. 프로젝트 설치 후에는 앞에 `.taskflow-kit/`를 붙인다. 참고 자료를 `.agents/skills/`로 복사하거나 독립 활성 스킬로 등록하지 않는다.

| 조건 | 진입 경로 | TaskFlow에서 참고할 목적 |
|---|---|---|
| 오류·실패·예상 밖 동작을 고칠 때 | `upstream/superpowers/skills/systematic-debugging/SKILL.md` | 재현, 원인 추적, 한 가설씩 검사, 수정 후 실제 재검증 |
| 완료·통과·수정 성공을 말하기 전 | `upstream/superpowers/skills/verification-before-completion/SKILL.md` | 주장과 이를 뒷받침하는 새 실행 증거를 연결 |
| 이미 논의한 요청을 요구사항으로 정리할 때 | `upstream/matt-pocock/skills/engineering/to-spec/SKILL.md` | 문제·사용자 행동·범위 밖 항목·검증 기준을 빠뜨리지 않기 |
| 일을 검증 가능한 단위와 의존성으로 나눌 때 | `upstream/matt-pocock/skills/engineering/to-tickets/SKILL.md` | 완료 기준, 실제 차단 관계, 독립적으로 확인할 수 있는 작업 단위 |
| 중요한 용어나 상태의 뜻이 충돌할 때 | `upstream/matt-pocock/skills/engineering/domain-modeling/SKILL.md` | 용어를 명확히 하고 필요한 결정의 이유를 기록 |
| 기준 Git 커밋과 요구사항을 비교하는 코드 검토 때 | `upstream/matt-pocock/skills/engineering/code-review/SKILL.md` | 저장소 규칙 준수와 요구사항 충족을 각각 확인 |
| 변경한 코드를 동작 유지 조건으로 정리할 때 | `upstream/code-simplifier/plugins/code-simplifier/agents/code-simplifier.md` | 최근 변경 범위 안에서 명료성·일관성·복잡도를 점검 |

문서·분석·CLI·알고리즘 등에도 TaskFlow 어댑터의 요구사항 정리와 검증 흐름을 적용할 수 있다. Git diff, React 코드, 도메인 용어집처럼 전제 조건이 필요한 원본은 그 조건이 실제로 맞을 때만 읽는다. 원본을 읽었다는 이유로 작업 범위를 늘리지 않는다.

## 그대로 활성화하면 안 되는 원본 전제

- Matt Pocock의 `to-spec`, `to-tickets`, `code-review`에는 이슈 트래커 설정, 게시, 질문·승인 단계가 있다. TaskFlow의 자동 후속 작업 흐름에서 이를 추가 승인이나 외부 게시의 권한으로 해석하지 않는다. 현재 사용자 지시와 프로젝트 범위가 우선한다. 로컬 작업 보드에 기록하는 것은 이슈 트래커 게시와 다르다.
- `code-review`의 두 병렬 에이전트는 소비 환경에서 실제 도구가 제공되고 허용될 때만 사용한다. 지원되지 않으면 두 관점을 순서대로 검토하고 직렬 실행임을 밝힌다. 문서만 읽고 병렬 실행이나 메시지 전송이 이루어졌다고 말하지 않는다.
- `code-simplifier.md`는 `SKILL.md`가 아닌 에이전트 사양이다. 원문의 `model: opus`, Claude 설정 파일 가정, JS/TypeScript/React 스타일, 상시 자율 정리 지시는 전역 설정이 아니다. 실제 언어·저장소 규칙·배정된 쓰기 범위가 맞는 조언만 적용하며, 이 파일로 모델이나 서비스를 설치·선택하지 않는다.
- 도메인 모델링 원본의 `GLOSSARY.md`와 ADR 작성도 배정된 파일 범위 안에서만 한다. 모든 과제에 용어집이나 ADR을 새로 만들지 않는다.
- Superpowers 원본의 다른 스킬 이름과 예제 명령은 자동 설치·실행 지시가 아니다. TaskFlow의 표준 라이브러리 실행기는 이 문서의 Bash·npm·TypeScript 예제를 실행하지 않는다. 실제 과제에서 필요한 명령은 해당 환경과 권한을 확인해 별도로 선택한다.

## 지원 파일의 포함 범위

선택한 각 원본 디렉터리에 있는 모든 Git blob을 포함했다. 따라서 디버깅의 `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`, `find-polluter.sh`, TypeScript 예제, 원본 자체의 평가·작성 기록이 함께 있다. 도메인 모델링의 `GLOSSARY-FORMAT.md`, `ADR-FORMAT.md`, Matt Pocock의 `agents/openai.yaml`도 원본 경로 그대로 보존했다. 파일이 존재한다는 사실과 해당 환경에서 실행 검증을 마쳤다는 주장은 구별한다. 이 참고 스크립트들은 실행하지 않았다.

선택 디렉터리의 파일은 완비했지만, 외부 이름 참조까지 모두 설치한 묶음은 아니다. 예를 들어 Superpowers의 `superpowers:test-driven-development`, Matt Pocock의 `/setup-matt-pocock-skills`와 이슈 트래커 문서, 사용자 프로젝트의 `CLAUDE.md`·기준 커밋·요구사항은 포함되지 않는다. 필요한 자료가 실제로 있는지 소비 어댑터가 확인하고, 없으면 해당 전제를 생략하거나 제한을 밝힌다. 전체 Superpowers 초기화·전역 훅·이슈 트래커 설정·대체 모델 실행기는 포함하지 않았다.

Vercel React 최적화 규칙, Supabase, 최적화 솔버·조합최적화 자료는 이 범용 핵심 묶음에서 제외했다. 특정 기술이나 과제가 요구할 때 출처와 라이선스를 별도로 고정해 추가한다. 기존 다른 묶음의 자료가 존재한다는 사실만으로 이 묶음의 기능으로 간주하지 않는다.

## 원본 확인 방식

연결된 GitHub 도구로 위 고정 커밋의 공개 Git 트리·디렉터리·라이선스를 확인했다. 기존 cofa 참고 사본의 각 파일을 GitHub Git blob SHA-1과 대조했고, 일치하는 12개 파일만 그대로 재사용했다. Windows CRLF 차이가 있던 14개 파일은 같은 커밋에서 base64 원문으로 다시 읽었다. 저장 전 모든 파일의 Git blob SHA-1과 크기를 원격 메타데이터와 대조하고, 저장된 바이트의 SHA-256을 매니페스트에 기록했다. 원본 파일의 내용·줄바꿈·파일명을 변경하지 않았다.

이 검사는 출처·선별 경로·바이트 일치의 확인이다. 원본 조언의 모든 주장이 모든 과제에 맞는지, 원본 예제의 실행 성공, 최적해 보장, 외부 제출 성공을 검증했다는 뜻은 아니다. 실제 과제의 검사 기록과 완료 판단은 TaskFlow의 검증 흐름에서 별도로 남긴다.


## v1.1 Understand Anything

- 원본: https://github.com/Egonex-AI/Understand-Anything
- 고정 커밋: `a6ea4024767df85ce4f99140d4f12ecfc5a81eb6`
- 라이선스: 원본 MIT와 내부 구성요소의 라이선스·BUILD 문서 보존. `LICENSE`의 Yuxiang Lin 및 Infinite Universe, Inc. 저작권을 유지한다.
- 포함: `understand-anything-plugin/` 전체 파일과 루트 LICENSE·README·워크스페이스·잠금 파일·타입스크립트 설정·npm 설정, 총 385개. 모든 선택 파일의 Git blob SHA-1·크기를 공식 고정 Git 트리와 대조하고 SHA-256을 기록했다. 원문 바이트를 변경하지 않았다.
- 실제 발견 스킬은 TaskFlow 연결 지침 `skills/understand/SKILL.md`다. 원본의 9개 스킬 디렉터리를 모두 자동 활성화하지 않으며 연결 지침에서 실제 원본 위치를 읽는다.
- 목적은 **최종 구현과 검증 이후의 결과물 이해**다. 과제 요구사항을 처음 요약하는 `taskflow-brief`와 구분한다.
- Node.js ≥22, pnpm ≥10, 코어 빌드와 실제 에이전트 실행이 필요하다. 소스가 있다는 사실을 그래프 생성·대시보드 실행 성공으로 표시하지 않는다. 패키지 설치·훅·다른 모델·외부 업로드를 자동 실행하지 않는다.
- 원본의 작업 사본 자동 리다이렉트는 이 통합에서 끄고 실제 최종 과제 폴더를 유지한다. 그래프용 임시 파일만 분석 작업자의 쓰기 범위로 배정한다.
