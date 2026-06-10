# 제안: ruff 린팅 오류 일괄 수정 — E501 줄 길이 초과 8건 + I001 import 정렬 9건

**우선순위**: medium
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

7개 파일에 걸쳐 ruff 린팅 오류 17건(E501 줄 길이 초과 8건, I001 import 정렬 9건)이 존재한다.

## 구현 단계

1. `uv run ruff check --fix src/ tests/` 실행하여 I001 import 정렬 자동 수정
2. `uv run ruff format src/ tests/` 실행하여 포맷팅 수정
3. 자동 수정 후 남은 E501 오류를 수동으로 수정:
   - `src/evonest/cli.py`: 긴 문자열/줄 분리
   - `src/evonest/core/claude_runner.py`: 긴 문자열/줄 분리
   - `src/evonest/core/config.py`: 긴 문자열/줄 분리
   - `src/evonest/core/phases.py`: 긴 문자열/줄 분리
4. `uv run ruff check src/ tests/` 실행하여 오류 0건 확인

## 대상 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py
- src/evonest/core/phases.py
- src/evonest/server.py
- tests/test_cli.py
- tests/test_server.py

## 검증

- `uv run ruff check src/ tests/`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
