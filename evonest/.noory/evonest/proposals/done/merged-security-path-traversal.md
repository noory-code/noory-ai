# 제안: path traversal 취약점 수정 — repositories.py _slugify() 경로 검증 추가

**우선순위**: medium
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/core/repositories.py`의 `_slugify()` 함수(21-29번 줄)가 제목을 파일명으로 변환할 때 경로 순회를 검증하지 않는다. `../../../etc/passwd` 같은 입력으로 `.evonest/proposals/` 외부에 파일을 쓸 수 있다.

## 구현 단계

1. `src/evonest/core/repositories.py` 파일 열기
2. `_slugify()` 함수에서 slug 생성 후 `..` 시퀀스와 경로 구분자(`/`, `\`)를 제거
3. `add_proposal()` 및 `add_stimuli()`에서 전체 경로 생성 후 `path.resolve().is_relative_to(self._dir)`로 대상 디렉토리 내에 있는지 검증
4. `tests/test_repositories.py`에 테스트 추가: `test_proposal_add_path_traversal_blocked()` — 제목이 `../../../etc/passwd`일 때 `.evonest/proposals/` 내의 안전한 파일명이 생성되는지 검증

## 대상 파일

- src/evonest/core/repositories.py
- tests/test_repositories.py

## 검증

- `uv run pytest tests/test_repositories.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
