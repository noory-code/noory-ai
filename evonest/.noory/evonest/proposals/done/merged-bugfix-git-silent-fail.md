# 제안: git revert/stash 실패 무시 버그 수정 — 경고 로깅 추가

**우선순위**: low
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/core/orchestrator.py` 791번 줄에서 git revert 및 stash pop 실패가 `pass`로 조용히 무시된다. 사용자가 작업물 손실 사실을 알 수 없다.

## 구현 단계

1. `src/evonest/core/orchestrator.py` 파일 열기
2. `_git_revert()` 함수 찾기 (782번 줄 부근)
3. except 블록의 bare `pass`를 `logger.warning(f"git revert failed: {e}")`로 교체
4. `_git_stash()` 및 `_git_stash_drop()` 함수에도 동일하게 경고 로그 추가
5. `import logging` 및 logger 설정이 되어 있는지 확인

## 대상 파일

- src/evonest/core/orchestrator.py

## 검증

- `uv run pytest tests/test_orchestrator.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
