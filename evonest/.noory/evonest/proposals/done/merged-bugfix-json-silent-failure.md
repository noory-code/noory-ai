# 제안: JSON 파싱 실패 시 무시 버그 수정 — 경고 로깅 및 백업 추가

**우선순위**: medium
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`repositories.py`(37-45번 줄)와 `state.py`(263번 줄)에서 `JSONDecodeError` 발생 시 빈 dict/list를 조용히 반환한다. 손상된 설정 또는 진행 파일이 경고 없이 무시되어 디버깅이 불가능하다.

## 구현 단계

1. `src/evonest/core/repositories.py` 및 `src/evonest/core/state.py` 파일 열기
2. 빈 컨테이너를 반환하는 모든 `except JSONDecodeError` 블록 찾기
3. 반환 전에 `logger.warning(f"Failed to parse {path}: {e}")` 추가
4. 핵심 파일(config.json, progress.json)의 경우: 덮어쓰기 전에 `.bak` 백업 생성
5. 테스트 실행하여 회귀 없음 확인

## 대상 파일

- src/evonest/core/repositories.py
- src/evonest/core/state.py

## 검증

- `uv run pytest && uv run mypy src/evonest/`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
