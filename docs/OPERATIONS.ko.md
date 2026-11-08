# 조율 담당자 운영 안내

프로젝트에 설치했다면 `python .taskflow-kit/kit.py`를 사용한다. 소스 폴더에서 쓰면 해당 `kit.py`를 직접 지정한다. 명령은 모델을 실행하지 않으며 실제 하위 에이전트 도구는 조율 담당자가 호출한다. 아래 A/T1/U1은 연습용 식별자이고 실제 작업의 ID와 경로로 바꾼다.

## 시작과 작업 배정

```text
python kit.py board --root PROJECT init --workers 3 --mode shared
python kit.py board --root PROJECT agent --id A --target ACTUAL_NATIVE_TARGET --scope backend/
python kit.py board --root PROJECT add --id T1 --title "핵심 계산" --scope backend/calc.py --accept "작은 입력의 기대 결과와 일치" --owner A --read contract:api
python kit.py board --root PROJECT claim --task T1 --agent A
```

`--workers`는 조율 담당자를 제외한 실제 지원 작업자 수 이하다. 실제 병렬 도구가 없으면 `--mode serial --workers 1`로 시작하고 target에 `local-coordinator` 같은 정직한 로컬 표기를 쓴다. 도구가 없는 환경에서 명령만 실행했다고 병렬 작업이 시작되는 것은 아니다.

각 작업자는 명시된 cwd와 수정 범위에서만 일한다. 다른 작업이 맡은 공통 파일을 수정해야 하면 보고하고 범위를 다시 나눈다. 이 도구는 OS 권한을 제한하지 않으므로 지시를 어긴 직접 파일 수정을 막지는 못한다. 독립 작업 사본을 쓸 때는 실제로 각 작업자의 cwd를 바꿔 배정해야 한다.

작업의 `--priority`는 작은 정수가 먼저이며 기본값은 50이다. 우선순위가 높아도 선행 작업·수정 예약·작업자 실행 한도를 무시하지 않는다. 차단된 작업 때문에 무관한 준비 완료 작업까지 멈추지는 않는다.

## 진행 중 개선 요청

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

## 충돌과 중단

- 파일 범위는 `backend/calc.py`, 디렉터리 전체 범위는 끝에 `/`를 붙여 `backend/`로 지정한다. 같은 파일/상하위 폴더의 수정은 충돌이다. `backend/a`와 `backend/ab`는 다른 범위다. 경로는 상대 경로로 지정하며 와일드카드를 쓰지 않는다.
- 같은 공통 자원을 읽는 작업끼리는 가능하다. `--write contract:api`는 해당 자원을 읽거나 쓰는 다른 예약이 해제될 때까지 차단된다. 버전 이름을 다르게 적어 동일한 살아 있는 계약의 충돌을 우회하지 않는다.
- 중단 후 재배정은 native 작업자가 실제로 멈춘 것을 확인한 다음 `release --task T1 --agent A --stopped --reason ...`로 한다. 이 명령 자체는 작업자를 멈추지 않는다.
- status/ready/outbox를 확인하고 기존 target을 재사용한다. stale/unknown 상태에서 무조건 새 에이전트를 띄우지 않는다.
- 한 요청이 여러 담당 범위를 건드리면 원문을 보존한 작은 작업들로 나누고 ID 연결을 남긴다. 담당이 모호한 요청은 임의 에이전트에게 보냈다고 처리하지 않는다.

## 과적합 방지

산업·모델·웹 프레임워크·작업자 역할·고정 시간표를 강제하지 않는다. 과제에서 CLI만 요구하면 CLI를 먼저 완성하고 선택적 웹 UI는 뒤로 둔다. 예시 숫자를 정답으로 고정하지 않고, 원문 요구와 가정을 구분한다. 기본 스킬 다섯 개를 한 번에 전부 읽을 필요 없이 해당 단계의 내용만 읽는다.
