# 조율 담당자 운영 안내

프로젝트에 설치했다면 `python .taskflow-kit/kit.py`를 사용한다. 소스 폴더에서 쓰면 해당 `kit.py`를 직접 지정한다. 명령은 모델을 실행하지 않으며 실제 하위 에이전트 도구는 조율 담당자가 호출한다. 아래 A/T1/U1은 연습용 식별자이고 실제 작업의 ID와 경로로 바꾼다.

## 실행 배치의 논의와 승인

먼저 [모델 정의 스킬](../skills/taskflow-model/SKILL.md)로 입력·출력의 의미, 목표·제약·평가 기준과 최소 완성 흐름을 정한다. 무엇이 개선인지는 원문 요구와 과제 지침에서 찾는다. 사실·사용자 선호·검증 전 가설을 구분하고, 우선순위가 충돌하면 임의 가중치를 넣지 말고 사용자와 해결한다.

실행할 작업 묶음의 범위·완료 기준·실험 한도·현재 채택 모델 보존 및 복구 방법을 보고하고 논의한 뒤 명시적 승인을 받는다. 승인 근거와 범위를 `.taskflow/decisions.md`에 남긴다. 이후 그 범위의 구현·검사는 명령마다 재승인받지 않고 진행한다. 범위 변경과 **각 개선 후보의 채택**에는 다시 논의와 승인이 필요하다. 침묵이나 기한 경과는 승인이 아니다.

이 기록과 판단은 [공통 의사결정 정책](../skills/taskflow-workflow/references/decision-policy.md)을 따르는 에이전트의 책임이다. 아래 작업판 명령은 승인 여부를 OS 차원에서 강제하거나 실험을 자동 실행하지 않는다.

## 시작과 작업 배정

```text
python kit.py board --root PROJECT init --workers 3 --mode shared
python kit.py board --root PROJECT agent --id A --target ACTUAL_NATIVE_TARGET --scope backend/
python kit.py board --root PROJECT add --id T1 --title "핵심 계산" --scope backend/calc.py --accept "작은 입력의 기대 결과와 일치" --owner A --read contract:api
python kit.py board --root PROJECT claim --task T1 --agent A
```

`--workers`는 조율 담당자를 제외한 실제 지원 작업자 수 이하다. 실제 병렬 도구가 없으면 `--mode serial --workers 1`로 시작하고 target에 `local-coordinator` 같은 정직한 로컬 표기를 쓴다. 도구가 없는 환경에서 명령만 실행했다고 병렬 작업이 시작되는 것은 아니다.

각 작업자는 명시된 cwd와 수정 범위에서만 일한다. 다른 작업이 맡은 공통 파일을 수정해야 하면 보고하고 범위를 다시 나눈다. 이 도구는 OS 권한을 제한하지 않으므로 지시를 어긴 직접 파일 수정을 막지는 못한다. 독립 작업 사본을 쓸 때는 실제로 각 작업자의 cwd를 바꿔 배정해야 한다.

프론트엔드·백엔드 내부의 독립 모듈도 나눌 수 있고, 경쟁 후보를 서로 다른 사본에서 비교할 수도 있다. 공통 입력·출력 계약과 의존성을 먼저 확인하고 실제 native 도구로 작업을 배정한다. 독립 비평자는 원문 요구·평가 기준·실제 결과를 받아 검토하며, 구현자의 자체 점검을 독립 비평으로 표시하지 않는다. 비평자의 권고는 사용자의 채택·배포 승인을 대신하지 않는다.

작업의 `--priority`는 작은 정수가 먼저이며 기본값은 50이다. 우선순위가 높아도 선행 작업·수정 예약·작업자 실행 한도를 무시하지 않는다. 차단된 작업 때문에 무관한 준비 완료 작업까지 멈추지는 않는다.

## 진행 중 개선 요청

요청 원문은 즉시 보존할 수 있다. 새 기능처럼 승인 범위를 넓히는 요청이라면 영향을 보고하고 배치를 다시 논의·승인한 뒤 구현을 시작한다. 아래 예시는 CSV 추가가 승인된 범위에 들어간 뒤 다음 작업과 전달 상태를 기록하는 명령이다.

```text
python kit.py board --root PROJECT request --key U1 --text "계산이 끝나면 CSV 내보내기도 추가" --task T2 --title "계산 결과 내보내기" --scope backend/export.py --accept "실제 계산 결과와 내보낸 값 일치" --owner A --after T1
python kit.py board --root PROJECT outbox
```

원문과 대기 작업을 먼저 보존한 다음 실제 native 메시지 도구로 반환된 target에 전달한다. 메시지에는 `U1/T2`, 선행 작업, 수정 범위, 현재 작업은 계속하라는 지시를 넣는다. 도구가 성공을 반환한 뒤에만 전달 상태를 기록한다.

```text
python kit.py board --root PROJECT delivery --key U1 --status delivered --receipt "native tool acknowledgement identifier"
```

타임아웃으로 성공 여부를 모르면 `--status unknown`, 명시적 실패면 `--status failed`다. 같은 U1을 사용해 수신 상태를 조정하고 중복 생성하지 않는다. delivered는 도구가 전달을 수락했다는 뜻이며 작업자의 수신 확인/착수/완료와 다르다. 프로세스 실행 중 새 사용자 메시지는 다음 도구/메시지 경계에서 처리된다. 별도의 상시 감시 서비스는 없다.

담당자가 아직 없거나 여러 명이 일치하는 요청은 미배정으로 보존된다. 담당자를 등록·판단한 뒤 `board --root PROJECT route --key U1 --owner A`로 배정한다. 원래 U1의 원문·payload를 바꾸지 않고 유효한 담당과 실제 target을 연결하며, 이미 배정·착수·전달한 요청을 몰래 다른 담당에게 넘기지 않는다.

## native 에이전트 모델 라우팅

난이도 기본값은 basic Luna 6/low, standard Sol 6.1/medium, critical Sol 6.1/high다. 허용 모델은 정확히 Sol 6.1, Terra 5.6, Luna 6, Sol 6.0이며 Astra는 금지한다. Terra 5.6은 검증된 현재 native ID가 없어 선택할 수 없다. Terra 6.1이나 Sol 5.6으로 대신하지 않으며, Sol 6.0은 승인된 범위에서 명시적으로 선택할 수 있는 대안이다.

현재 호스트의 native 도구 메타데이터에서 관찰한 ID만 `--available`에 넣어 오프라인 계획을 확인한다. 소스 체크아웃에서는 해당 키트의 `kit.py`를 사용한다.

```text
python kit.py agent-plan --tier basic --available gpt-6-luna --available gpt-6.1-sol
```

이 예시 ID는 실제 도구에서 관찰된 경우에만 사용한다. `agent-plan`은 호출자 제공 목록과 정책을 대조할 뿐, 목록을 독립 검증하거나 에이전트를 dispatch하지 않는다. 승인 획득, 설정·매핑·부모 모델 변경도 하지 않는다. 계획 출력 뒤 실제 native 도구의 모델·effort 지원을 확인하고 해당 작업의 승인 범위에 맞춰 정확한 모델과 effort를 명시한다. 도구가 이를 지원하지 않으면 기본값을 물려받아 실행하지 말고 제약을 보고한다. 요청한 모델과 도구가 실제 적용한 모델은 구분한다. 자동 키트·모델·스킬·upstream·의존성·전역 설정 업데이트는 없다. 전체 제한은 [모델 라우팅 정책](../skills/taskflow-parallel/references/model-routing.md)에 있다.

## 완료·통합·검증

```text
python kit.py board --root PROJECT finish --task T1 --agent A --note "계산 모듈과 자체 확인 완료"
python kit.py board --root PROJECT integrate --task T1 --note "실제 제출 작업공간에 반영하고 연결 확인"
python kit.py board --root PROJECT ready
python kit.py check --root PROJECT --task T1 --watch backend --watch contracts --timeout 120 -- python -m unittest
python kit.py board --root PROJECT verify --task T1 --evidence ACTUAL_EVIDENCE_JSON
```

finish는 실행 슬롯을 비우지만 통합 전 수정 예약은 유지한다. integrate는 실제 통합 결과를 **기록**하며 Git 병합을 대신 실행하지 않는다. 선행 작업은 done이 아니라 integrated/verified 상태에서 다음 작업을 연다. 통합하지 않은 결과를 숨겨둔 채 다음 작업을 시작하지 않는다.

`check`의 명령은 인자 배열로 실행하고 셸을 사용하지 않는다. 셸 문법이 필요하면 제공 환경에서 사용자가 허용한 셸과 명령을 명시적으로 지정한다. 시간 초과 시 직접 자식 프로세스를 중지하지만 임의 명령이 만든 모든 손자 프로세스의 종료를 보장하지 않는다. 테스트 서버/DB/포트는 별도로 정리·분리해야 한다.

검사한 코드·계약·입력·테스트·의존성 선언을 충분히 watch에 포함한다. 검사 도중 변경되는 예상 산출물을 source watch에 섞지 않는다. 파일 추가·삭제도 변경으로 감지한다. 검사 이후 바뀐 소스의 예전 evidence는 다시 쓸 수 없다. board의 verified 표시는 과거 기록이므로 최종 보고 전에 `evidence --root PROJECT --task T1 --path EVIDENCE`로 현재성을 재확인한다.

## 제한된 개선 실험과 후보 채택

[개선 스킬](../skills/taskflow-improve/SKILL.md)은 기존 작업판과 검사 근거를 사용한다. `.taskflow/accepted.md`와 `.taskflow/experiments/C1.md` 같은 파일은 현재 채택 모델·후보·비교 결과를 남기는 일반 문서이며 새 CLI 상태나 자동 실행 명령이 아니다.

1. 현재 채택 모델의 버전·설정·검사 근거와 복구 지점을 보존하고, 승인된 분석 범위에서 실패·병목·약점을 찾아 실험 가설을 세운다.
2. 승인된 배치의 한도 안에서 별도 후보를 만든다. 방법 교체·병렬 후보·혼합 방식, 모듈 추가·삭제·순서 변경을 고려하되 의존성과 입력·출력 계약을 확인한다.
3. 같은 입력·기준과 비교 가능한 조건으로 현재 채택 모델과 후보의 결과·비용·실패를 비교한다. 독립 비평자에게 원문 요구와 실제 검사 결과를 제공하고 반례·회귀·불확실성을 검토하게 한다. 반복 선택용 평가와 최종 평가를 분리하고, 숨김·최종 평가를 다음 실험의 탐색 자료로 쓰지 않는다.
4. 정확한 후보 ID·기준 버전·실행 근거·대안·상충 관계·복구 대상과 권고를 보고한다. 우선순위 충돌은 사용자와 해결하며, 검사를 통과해도 **채택 승인 전 현재 채택 모델을 바꾸지 않는다.** 후보나 근거가 바뀌면 다시 비교하고 채택 승인을 갱신한다.
5. 명시적 채택 승인 뒤 반영·검증하고 실패하면 이전에 채택한 모델로 복구한다. 성공한 새로 채택한 모델의 실패·병목·약점을 승인된 범위에서 다시 진단해 다음 실험을 제안한다. 승인받지 않은 다음 배치는 시작하지 않는다.

통합·verified 기록만으로 후보 채택이나 배포가 승인되지는 않는다. 배치가 끝나거나 한도에 닿으면 결과와 남은 불확실성을 보고하며, 끝없이 실행되는 백그라운드 개선 작업을 만들지 않는다.

## 충돌과 중단

경쟁 후보를 한 작업판에서 관리하려면 승인된 공통 프로젝트 아래 실제로 분리된 작업 사본을 두고 `variants/C1/src/solver.py`, `variants/C2/src/solver.py`처럼 **작업판 root 기준의 실제 경로**를 예약한다. 작업자에게는 각 후보의 실제 cwd를 전달한다. 두 사본의 `src/solver.py`를 모두 같은 root의 `src/solver.py`로 등록하면 불필요한 충돌이 생긴다. 반대로 같은 실제 파일에 가짜 후보 접두사를 붙여 예약을 우회해서도 안 된다. 외부 DB·포트 등은 같은 작업판의 공통 자원으로 관리하고, 제출물에는 채택한 구현만 통합한다.

호스트가 허용한 공통 root 밖의 작업 사본만 지원하면 이 작업판은 여러 root의 예약을 통합하지 못한다. 그때는 조율 담당자가 명시적으로 소유 범위·공통 자원을 기록하거나 순차 실행한다. 별도 작업판 여러 개가 전체 충돌을 막아준다고 설명하지 않는다.

- 파일 범위는 `backend/calc.py`, 디렉터리 전체 범위는 끝에 `/`를 붙여 `backend/`로 지정한다. 같은 파일/상하위 폴더의 수정은 충돌이다. `backend/a`와 `backend/ab`는 다른 범위다. 경로는 상대 경로로 지정하며 와일드카드를 쓰지 않는다.
- 같은 공통 자원을 읽는 작업끼리는 가능하다. `--write contract:api`는 해당 자원을 읽거나 쓰는 다른 예약이 해제될 때까지 차단된다. 버전 이름을 다르게 적어 동일한 살아 있는 계약의 충돌을 우회하지 않는다.
- 중단 후 재배정은 native 작업자가 실제로 멈춘 것을 확인한 다음 `release --task T1 --agent A --stopped --reason ...`로 한다. 이 명령 자체는 작업자를 멈추지 않는다.
- status/ready/outbox를 확인하고 기존 target을 재사용한다. stale/unknown 상태에서 무조건 새 에이전트를 띄우지 않는다.
- 한 요청이 여러 담당 범위를 건드리면 원문을 보존한 작은 작업들로 나누고 ID 연결을 남긴다. 담당이 모호한 요청은 임의 에이전트에게 보냈다고 처리하지 않는다.

## 과적합 방지

산업·모델·웹 프레임워크·작업자 역할·고정 시간표를 강제하지 않는다. 과제에서 CLI만 요구하면 CLI를 먼저 완성하고 선택적 웹 UI는 뒤로 둔다. 예시 숫자를 정답으로 고정하지 않고, 원문 요구와 가정을 구분한다. 설치되는 8개 스킬을 한 번에 전부 읽을 필요 없이 공통 정책과 해당 단계의 내용만 읽는다.
