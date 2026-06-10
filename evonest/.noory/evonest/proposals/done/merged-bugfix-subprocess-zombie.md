# 제안: subprocess 좀비 프로세스 버그 수정 — TimeoutExpired 핸들러에 kill/wait 추가

**우선순위**: medium
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/core/phases.py` 623, 648번 줄의 `subprocess.TimeoutExpired` 핸들러가 자식 프로세스를 종료하지 않아, 타임아웃 후 좀비 프로세스가 남는다.

## 구현 단계

1. `src/evonest/core/phases.py` 파일 열기
2. verify 함수 내 `except subprocess.TimeoutExpired` 블록 찾기 (623, 648번 줄 부근)
3. except 블록에 `process.kill()` 및 `process.wait()` 호출 추가
4. 적절한 정리 보장: `process.kill(); process.wait(); stdout, stderr = process.communicate()`
5. `tests/test_phases.py`에 테스트 추가: subprocess를 mock하여 `TimeoutExpired` 발생시키고, `kill()`이 호출되는지 검증

## 대상 파일

- src/evonest/core/phases.py
- tests/test_phases.py

## 검증

- `uv run pytest tests/test_phases.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
