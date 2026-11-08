# TaskFlow Kit 1.1

처음 보는 과제를 빠르게 파악하고, 여러 에이전트의 병렬 작업과 진행 중 개선 요청을 조율하는 범용 스킬팩입니다.

- **과제 요약:** 원문 근거를 유지하며 필수·선택·예시·가정을 구분합니다.
- **병렬 작업:** 백엔드 내부까지 독립 작업으로 나누고 파일 범위와 공통 자원을 예약합니다.
- **진행 중 요청:** 담당자의 다음 작업으로 기록하고 등록·전달 수락·착수·통합·검증을 구분합니다.
- **기본 흐름:** 요구사항 파악부터 최소 구현, 검증과 제출 준비까지 연결합니다.
- **최종 결과물 이해:** 검증 뒤 Understand Anything을 적용해 구조·동작·설계 이유를 한국어로 설명합니다.

TaskFlow 조율 도구는 Python 3.10+ 표준 라이브러리를 사용합니다. Understand Anything 그래프 실행은 별도로 Node.js ≥22, pnpm ≥10과 원본 코어 빌드가 필요합니다. 모델 실행·실제 메시지 전달은 제공 AI 환경의 native 에이전트 도구가 담당합니다. 해당 도구가 없으면 순차 모드로 사용할 수 있습니다.

## 가져오기와 등록

```sh
git clone https://github.com/arcturus0637-rgb/taskflow-kit.git
python taskflow-kit/kit.py verify-bundle
python taskflow-kit/kit.py install --project /path/to/actual-project --dry-run
python taskflow-kit/kit.py install --project /path/to/actual-project
```

`/path/to/actual-project`를 실제 과제 폴더로 바꾸세요. Python 실행 이름이 `python3`이면 명령도 바꾸세요. 기존 과제 파일과 `AGENTS.md`는 보존하며 다른 내용의 기존 설치 파일을 덮어쓰지 않습니다.

## 시작 요청

실제 과제 세션에서 다음과 같이 요청하세요.

```text
$taskflow-workflow을 사용해 이 과제를 진행해줘.
원문 요구사항과 제출 조건을 먼저 짧게 정리하고, 독립 작업을 병렬로 배정해줘.
작업 중 내가 개선 요청을 보내면 담당자의 다음 작업으로 기록하고 실제 전달 도구를 사용해줘.
최소 구현부터 끝까지 연결한 뒤 통합 결과와 검증 근거를 확인해줘.
그 뒤 완성된 결과물에 $understand를 적용하고, 구조·데이터 흐름·설계 이유·검증과 한계를 내가 이해하도록 한국어로 설명해줘.
```

## 문서와 공개 원본

- [설치·전체 사용 안내](README.ko.md)
- [작업판·요청 전달 운영 예시](docs/OPERATIONS.ko.md)
- [검증 결과와 실제 확인 범위](docs/VALIDATION.ko.md)
- [오픈소스 출처와 라이선스](docs/SOURCES.ko.md)
- [Understand Anything 적용·준비 안내](docs/UNDERSTAND-ANYTHING.ko.md)

기본 공개 참고 원문 26개에 더해 Egonex-AI/Understand-Anything의 고정 버전 소스 385개를 포함했습니다. 원본 스킬 9개·분석 에이전트·스크립트·코어·대시보드 소스와 라이선스가 함께 있습니다. 기본 설치는 TaskFlow 스킬 5개와 `$understand` 연결 스킬 1개입니다. 필요한 부분만 조건부로 참고하며 전체 실행 프레임워크를 활성화하지 않습니다.

자동 검사 **46개 통과** 및 깨끗한 폴더 설치·실행 확인을 마쳤습니다. 실제 대회 환경의 도구 지원과 사용 규정은 별도로 확인해야 합니다. 수정 예약은 협력 규칙이며 OS의 쓰기 권한 차단이나 모든 과제의 정답 보장은 아닙니다.
