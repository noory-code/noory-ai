# 제안: server.py import 블록 정렬 및 E501 라인 길이 위반 수정

**우선순위**: low  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

server.py:11-26에서 import 블록이 정렬되지 않았고, 여러 파일에서 100자 라인 길이 제한을 초과합니다. `uv run ruff format src/ tests/`로 자동 수정 가능하며, 일부는 --fix 옵션으로 자동 해결됩니다.

## 관련 파일

- src/evonest/server.py
- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py
- tests/test_cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*