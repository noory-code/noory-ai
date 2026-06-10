# 제안: mypy strict 오류 수정 — personas.py 제네릭 dict 타입 파라미터 누락

**우선순위**: high
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/tools/personas.py` 9, 10, 19번 줄에서 타입 파라미터 없이 bare `dict`를 사용하여 mypy strict 모드에서 3건의 오류가 발생한다.

## 구현 단계

1. `src/evonest/tools/personas.py` 파일 열기
2. 파일 상단에 `from typing import Any` import가 없으면 추가
3. 9번 줄: `dict` -> `dict[str, Any]`로 변경
4. 10번 줄: `dict` -> `dict[str, Any]`로 변경
5. 19번 줄: 실제 사용 패턴에 따라 `dict[str, bool]` 또는 `dict[str, Any]`로 변경
6. `uv run mypy src/evonest/` 실행하여 오류 0건 확인

## 대상 파일

- src/evonest/tools/personas.py

## 검증

- `uv run mypy src/evonest/`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
