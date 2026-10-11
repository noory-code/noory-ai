**판정: PASS** (A와 B 두 가지 수리에 한정)

테스트와 모델 호출은 하지 않았고, 아래 판단은 모두 코드를 읽고 예상한 결과입니다.

**A. CLI가 `null` envelope를 돌려줄 때 → 네 실행이 모두 기록됩니다**
- **실패 처리:** `json.loads('null')` 결과가 `None`이라 `isinstance(envelope, dict)` 검사에 걸리고 `ValueError`가 납니다. 이 예외는 except에서 잡히고, `finally`가 `status: failed`와 `error` 문자열을 담은 `process.json`을 씁니다. `run_one`이 False를 돌려주므로 `run_batch`는 다음 실행으로 넘어갑니다. `[]`나 문자열 envelope도 같은 경로를 탑니다.
- **다른 잘못된 envelope도 잡힙니다:**
  - `structured_output`이 리스트나 문자열이면 `TypeError`
  - `result`가 없거나 JSON이 아니면 `JSONDecodeError`(`ValueError`의 하위 클래스)
  - `result`가 `"null"`이면 `TypeError`
  - `items`가 없으면 `KeyError`
- **요약기:** 폴더 4개가 모두 생기고 `model-comparison.json`은 없습니다. 그래서 `runs=4`, `accepted_runs=0`, `scored_labels=0`이 나옵니다. `target_labels=12`는 사례당 구간이 3개라는 전제에서 나온 값입니다.

**B. 형식은 맞지만 참조가 틀린 경우 → 모델 원본 라벨로 채점됩니다**
- **채점 순서:** `check_label_shape`를 통과하면 `shape_passed=True`가 됩니다. 이어서 `compare_model_labels`가 원본 act·ref를 gold와 비교해 `model-comparison.json`에 먼저 기록합니다. 그다음 `merge_labels`의 `check_labels`가 `ValueError`를 내면 상태가 `invalid_reference`가 됩니다.
- **뜻 오류만 이 상태가 됩니다:** `check_labels`가 내는 예외는 참조 규칙이나 act와 ref의 짝이 맞지 않을 때뿐입니다. 따라서 `invalid_reference`는 항상 형식은 맞고 뜻이 틀린 경우이고, 원본 라벨 기준으로 채점됩니다.
- **요약기:** 실패한 실행이어도 비교 파일이 있으면 그 행을 집계에 넣습니다. 테스트가 확인하는 2 일치 / 4 불일치는 뜻 오류가 다시 숨으면 실패하는 판별력 있는 단언입니다.
- **거짓 점수 경로:** 찾지 못했습니다.

**남은 한계** (이번 수리 판정은 바꾸지 않습니다)
1. **`RecursionError`가 나면 배치가 다시 멈춥니다.** 아주 깊게 중첩된 JSON(예: `'['*100000`)을 읽으면 CPython `json.loads`가 `RecursionError`를 내는데, 이 예외는 except 목록에 없습니다. `process.json`은 `error` 없이 기록되고, 예외가 바깥으로 나가 남은 실행이 생기지 않습니다. 그러면 요약기는 없는 폴더를 읽다가 `FileNotFoundError`로 멈춥니다. 원래 결함 A와 같은 종류입니다. 이번 수리는 특정 형태 하나를 막았을 뿐, "실패가 나도 배치가 끝까지 돈다"를 보장하지는 않습니다.
2. **비용 값이 숫자가 아니면 요약기가 멈춥니다.** `total_cost_usd`가 문자열이면 요약기의 `sum(... or 0)`에서 `TypeError`가 납니다. envelope가 객체인 경우라 A의 범위 밖입니다.
3. **테스트가 덮는 범위에 한계가 있습니다.**
   - A 테스트는 `subprocess.run`을 패치하고 `run_batch`를 직접 부릅니다. 그래서 `main()`과 PATH 위의 가짜 `claude`를 거치지 않습니다. 게다가 제공된 `main()`은 F/G/H 세 사례만 받아들여 HP/HC 배치를 실행할 수 없습니다. 앞 검토가 제안한 끝단 테스트는 비슷하게 흉내 낸 것이지 그대로 재현한 것은 아닙니다. envelope 처리 로직만 보면 결과는 같습니다.
   - B 테스트는 앞 검토의 HP/HC 예시가 아니라 F/G/H의 H 사례를 씁니다. 로직은 같습니다.
   - `reference-colleague-fixture.json`은 제공된 자료에 없습니다.
   - "40개 통과"라는 주장은 확인하지 않았습니다. 제공된 테스트 파일에는 테스트가 8개뿐이어서, 이 주장을 근거로 쓸 수 없습니다.
