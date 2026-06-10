# 제안: ruff 린트 오류 수정 — 줄 길이 및 import 정렬

**우선순위**: medium  
**작성 페르소나**: spec-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ruff check에서 17개의 오류가 발견되었습니다: (1) E501 줄 길이 제한 초과 8건 (src/evonest/cli.py, claude_runner.py, config.py, phases.py), (2) I001 import 블록 정렬 오류 9건 (src/evonest/server.py, tests/test_cli.py, tests/test_server.py). Quality Standards에 'Linting passes: uv run ruff check src/ tests/'가 명시되어 있으므로 이를 모두 수정해야 합니다. ruff format --fix로 자동 수정 가능한 항목 9건 포함.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py
- src/evonest/core/phases.py
- src/evonest/server.py
- tests/test_cli.py
- tests/test_server.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*