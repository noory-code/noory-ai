# 검증 기록

## 선택기의 실패와 통과

실행 명령은 `python3 -m unittest discover -s .stage/research/llm-work/experiments/selected-review -p 'test_selector.py' -v`입니다.

처음에는 `select_source`가 원문 전체를 그대로 반환했습니다.
검사 여덟 개 중 아래 두 개가 실패했습니다. 함수 동작은 같았지만 불필요한 함수까지 남아 있었습니다.

- `test_trim_preserves_transitive_calls_and_global_values`: `IRRELEVANT_SENTINEL`이 선택한 소스에 남았습니다.
- `test_recursive_dependencies_terminate_and_keep_behavior`: `unused` 함수가 선택한 소스에 남았습니다.

관찰한 첫 명령의 종료 코드는 1이었고 `FAILED (failures=2)`를 반환했습니다.
정적 참조를 따라 선택하도록 구현한 뒤 같은 명령은 종료 코드 0과 `Ran 8 tests`, `OK`를 반환했습니다.
초기 실패는 이 세션의 명령 출력에서 확인했습니다. 초기 실패 출력을 별도 원본 파일로 저장하지는 않았습니다.

## 실제 결함의 동작

[회귀 실행 원본](regression-results.json)에 네 실행의 명령·수정 파일 해시·출력·종료 코드가 있습니다.
결함 두 개 모두 수정 전 코드에서 같은 회귀 검사가 실패했고 수정 후 코드에서 통과했습니다.
테스트가 대상 소스 트리를 바꾸지 않았다는 해시 검사도 통과했습니다.

## 모델 결과

`python3 .stage/research/llm-work/experiments/selected-review/summarize.py`로 다시 계산했습니다.
입력과 선택 규칙, 원본 해시, 기대값과 응답의 대조에서 불일치가 없었습니다.
계획한 36번을 모두 실행했고 36번 모두 행동과 대상 기준 ID가 기대값과 일치했습니다.
서버 오류와 누락 호출은 없었습니다. 설명 전체의 정확도를 채점한 결과는 아닙니다.

자료가 없는 네 번은 별도로 집계했고, 입력을 줄이지 않은 비교는 동일한 입력임을 해시로 확인했습니다.
금액을 반환하지 않은 Codex 호출은 `null`로 유지했습니다.
