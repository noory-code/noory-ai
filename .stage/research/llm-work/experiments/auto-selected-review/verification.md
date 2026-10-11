# 검증 기록

## 실패를 확인한 뒤 선택 코드를 연결했습니다

처음에는 `choose_source`가 원문 전체를 그대로 반환했습니다.
검사 여섯 개 중 `test_valid_selection_preserves_behavior_and_removes_irrelevant_function`이 실패했습니다.
실행 결과는 맞았지만 불필요한 함수의 `BODY_SECRET_SENTINEL`이 남았습니다.
기존 선택기를 연결한 뒤 여섯 검사가 모두 통과했습니다.
초기 실패는 이 세션의 명령 출력에서 관찰했습니다. 별도 원본 파일로 저장하지는 않았습니다.

실행 명령은 아래와 같습니다.

```text
python3 -m unittest discover -s .stage/research/llm-work/experiments/auto-selected-review -p 'test_*.py' -v
```

모델 호출 뒤 추가한 분석에서는 한국어 조사가 붙은 함수 이름을 놓치는 문제를 고쳤습니다.
해당 검사와 다른 식별자의 일부를 잘못 찾지 않는 검사를 더했습니다. 최종 검사 여덟 개가 통과했습니다.
실제 결함의 수정 전후와 회귀 결과는 [이전 실험 원본](../selected-review/regression-results.json)을 사용했습니다.
이번에는 기존 해시와 결과를 확인했으며 회귀 명령을 새로 실행하지 않았습니다.

## 원본 응답으로 다시 계산했습니다

```text
python3 .stage/research/llm-work/experiments/auto-selected-review/summarize.py
```

이 명령은 모델을 호출하지 않습니다. 저장한 응답으로 코드 선택과 입력을 재구성합니다.
입력·해시·호출 순서·선택 결과·기대값·채점·시간 구간을 대조했습니다.
요청 32번과 CLI 호출 48번에서 누락·추가 호출·서버 오류·불일치가 없었습니다.
최종 판정 32개가 행동과 대상 기준 ID에서 모두 기대값과 일치했습니다.
이는 설명 전체와 범위 밖의 결함을 채점한 결과는 아닙니다.

[실행 전에 고정한 파일](runs/manifest.json)과 [원본 응답·요청 파일 80개의 해시](summary.json)를 남겼습니다.
금액이 없는 Codex 호출은 `null`로 유지했습니다.
실험 뒤 수행한 [코드 검사](posthoc-probe.json)는 모델 비교와 구분했습니다.

최종 파일 검사 결과를 [verification.json](verification.json)에 저장했습니다.
실행 전에 고정한 파일 9개와 원본 기록 80개의 해시가 일치했습니다.
Python 파일 6개를 구문 검사했고 문서 6개의 로컬 링크 경로 151개를 확인했습니다.
링크의 문서 내부 앵커까지 확인한 결과는 아닙니다.
테스트 여덟 개와 `git diff --check`도 통과했습니다.
