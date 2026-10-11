# 실험 자료와 실행 방법

가장 최근에는 Codex CLI를 업데이트한 뒤 남은 비교 16번을 모두 마쳤습니다.
새 실행 오류는 없었고 실제 작업 인계 두 조건은 각각 전체 테스트 94개를 통과했습니다.
[최신 결과](../findings/2026-10-05-stage-after-update.md)와 [업데이트 전후를 구별한 집계](stage-followup/after-update/summary.json)에 정리했습니다.

그전에는 출처 단위를 명시한 Codex 기준 추출과 판단 네 번을 마쳤습니다.
간격을 둔 재시도에서도 서버 오류가 반복됐습니다. 실패를 보존하고 정상 응답과 구별했습니다.
[당시 결과](../findings/2026-10-05-stage-criteria-resume.md)와 [그때까지의 시도 집계](stage-followup/retry-3/summary.json)에 남았던 비교를 정리했습니다.

그전에는 중단된 비교를 다시 시도했습니다. Codex는 기준 추출에 응답한 뒤 다음 호출에서 서버 혼잡 오류를 반환했습니다.
기준 추출에서는 출처 형식이 검사 규칙과 맞지 않는 문제도 확인했습니다.
[재시도 결과](../findings/2026-10-05-stage-retry.md)와 [별도 집계](stage-followup/retry-1/summary.json)에 남겼습니다.

그전에는 목표와 검사를 맞춰 실제 CLI 파일 도구로 일을 이어받게 했습니다.
정상 완료 네 번과 Codex 서버 오류 한 번을 기록했습니다. 예정한 인계 여덟 번 중 세 번은 미실행입니다.
기준 추출·적용, 관찰 시점 비교와 실제 로그 조사도 함께 진행했습니다.
[실행 계획](stage-followup/README.md)과 [중간 결과](../findings/2026-10-05-stage-followup.md)에 남은 항목을 적었습니다.

그전에는 과거 결함 두 개의 실제 수정을 다른 AI가 이어받는 실험을 여덟 번 수행했습니다.
첫 구간까지 포함한 모델 호출은 34번입니다.
[실행 방법](cross-session/README.md)과 [결과](../findings/2026-10-05-cross-session.md)에 정리했습니다.
이어받기의 호출은 줄었지만 전체 시간은 줄지 않았습니다. 목표와 전체 검사의 범위가 달랐던 문제도 기록했습니다.

그전에는 실제 작업 여섯 건의 인계 자료를 확인하고, 작업 한 건의 질문 두 개를 Claude·Codex에서 24번 비교했습니다.
[실행 방법](context-handoff/README.md)과 [결과](../findings/2026-10-05-context-handoff.md)에 정리했습니다.
입력 토큰은 줄었지만 전체 작업 인계의 효과를 입증한 시험은 아닙니다.

그전에는 실제 과거 결함 두 개의 코드 리뷰를 반복했습니다.
요청 64번 중 모델을 48번 호출하고 판정을 16번 재사용했습니다.
[실행 방법](review-reuse/README.md)과 [결과](../findings/2026-10-05-review-reuse.md)에 정리했습니다.

최근에는 아이디어 여섯 가지를 시제품으로 만들고 Claude·Codex에서 96번 비교했습니다.
연결 확인 두 번과 로컬 테스트 54개는 별도로 셌습니다.
[시제품 실행 안내](ideas-lab/README.md)와 [결과 보고서](../findings/2026-10-05-ideas-lab.md)에서 확인할 수 있습니다.
아래 280건은 그보다 앞선 Claude 연구 기록입니다.

2026-10-05에 관찰 경로를 확인하는 실행 2건과 근거 판단을 비교하는 실행 8건을 수행했습니다.
그 뒤 합성 문제 30개로 174건을 반복했습니다.
평가 문제의 모호함을 발견해 목적·기억 문제를 보완하고 96건을 더 실행했습니다.
총 280건을 마쳤습니다. 모델을 쓰지 않는 로컬 검사 18개 항목은 별도로 셌습니다.
결론과 한계는 [예비 실험 보고서](../findings/2026-10-05-pilot.md)와 [반복 실험 보고서](../findings/2026-10-05-followup.md)에 적었습니다.
[목적 해석 실험](01-purpose-and-evidence.md)의 정식 비교 72회는 실행하지 않았습니다.

## 자료

| 경로 | 내용 |
|---|---|
| [run_pilot.py](scripts/run_pilot.py) | 임시 폴더에서 Claude CLI를 호출하고 결과를 저장합니다. |
| [문제](evidence-cases.json) | 실제 제품과 무관하게 만든 자료 4개입니다. |
| [채점 기준](evidence-rubric.json) | 모델에 보내지 않았습니다. 아직 사람이 검토하지 않았습니다. |
| [집계 스크립트](scripts/summarize_pilot.py) | 저장한 기록에서 상태값과 사용량을 모읍니다. 모델을 다시 호출하지 않습니다. |
| [집계 결과](runs/2026-10-05-summary.json) | 10건의 결과 경로, 사용량, 파일 해시를 연결합니다. |
| [후속 문제](followup-cases.json), [별도 기준](followup-rubric.json) | 실행 전에 고정한 합성 문제와 기대값입니다. |
| [후속 실행기](scripts/run_followup.py) | 설정과 순서를 기록하고 두 실행씩 수행합니다. |
| [후속 집계](runs/2026-10-05-followup-summary.json) | 원래 기대값, 응답, 비용, 문제별 반복 결과를 연결합니다. |
| [보완 시험 집계](runs/2026-10-05-repaired-summary.json) | 자료를 보완한 뒤의 결과를 별도로 모읍니다. |
| [보완한 문제](repaired-cases.json), [별도 기준](repaired-rubric.json) | 앞선 응답을 본 뒤 자료 누락과 버전 표현을 바로잡았습니다. |
| [보완 실행기](scripts/run_repaired.py) | 원래 기록을 유지하며 새 폴더에 결과를 저장합니다. |
| [로컬 규칙 검사](scripts/check_local_rules.py) | 모델 호출 없이 18개 항목을 검사합니다. |

## 다시 실행할 때

Python 3.11 이상과 로그인된 Claude Code CLI가 필요합니다.
이번 실행은 임시 가상 환경에 [고정한 SDK 소스](../sources.md#s15)를 설치해서 수행했습니다.
전역 패키지와 저장소의 제품 의존성은 바꾸지 않았습니다.
같은 결과를 보장하려면 CLI 버전과 서버의 모델 변경 가능성도 고려해야 합니다.
전이 의존성을 고정한 lock 파일은 만들지 않았으므로 완전히 같은 환경을 복원한다고 주장하지 않습니다.

아래 명령의 `python`은 해당 SDK를 설치한 가상 환경의 Python을 뜻합니다.
Windows에서는 `Scripts/python.exe`, macOS와 Linux에서는 `bin/python`을 사용합니다.
저장소 루트에서 한 줄씩 실행합니다. 새 모델 호출에는 사용량이 발생합니다.
`--output`은 기존 JSON 기록이 없는 새 폴더를 지정해야 합니다.

```text
python .stage/research/llm-work/experiments/scripts/run_pilot.py hooks --output .stage/research/llm-work/experiments/runs/new-hooks --sdk-revision 9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b
python .stage/research/llm-work/experiments/scripts/run_pilot.py evidence --output .stage/research/llm-work/experiments/runs/new-evidence --cases .stage/research/llm-work/experiments/evidence-cases.json --model claude-sonnet-5-5 --sdk-revision 9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b
```

`--sdk-revision`은 실행자가 기록하는 값입니다. 설치된 패키지의 커밋을 자동으로 검증하지는 않습니다.
이번에는 별도로 소스의 Git 커밋을 확인했습니다.
집계 스크립트는 2026-10-05 기록 전용입니다. 새 실행의 폴더를 자동 선택하지 않습니다.

## 기록에 없는 것

- 모델 서버가 받은 요청 전체와 비공개 지침은 없습니다.
- 공개 응답과 도구 사건만 남겼습니다. 숨겨진 추론은 수집 대상에서 제외했습니다.
- CLI가 보고한 추가 모델의 입력과 출력은 없습니다.
- SDK가 보고한 비용을 저장했습니다. 청구서를 조회하지 않았습니다.
- 모든 예외와 운영체제 조합을 시험하지 않았습니다. 이번 실행 환경은 macOS입니다.

입력과 원본 결과는 보존합니다. 새로운 평가나 집계는 별도 파일에 남깁니다.

## 반복 실험을 다시 실행할 때

`run_followup.py`는 `followup-cases.json`과 실행 전 해시를 검사합니다.
이미 기록한 실행은 다시 호출하지 않으며, 설정이 달라지면 중단합니다.
`run_repaired.py`는 보완한 목적·기억 문제에 같은 호출 함수를 사용합니다.
이 스크립트들은 고정한 연구 기록용입니다. 새 모델의 비교 평가용으로 자동 갱신되지 않습니다.

모델을 다시 부르지 않고 기록만 집계하려면 다음 명령을 사용합니다.

```text
python .stage/research/llm-work/experiments/scripts/summarize_followup.py
python .stage/research/llm-work/experiments/scripts/summarize_followup.py --repaired
python .stage/research/llm-work/experiments/scripts/check_local_rules.py
python .stage/research/llm-work/experiments/scripts/verify_research.py
```

추가 호출에는 기존 로그인 계정의 사용량이 발생합니다.
원본 실행 기록과 평가 결과의 모델별 사용량을 보존했습니다. 특정 출력 모델 하나의 비용으로 단순화하지 않습니다.
