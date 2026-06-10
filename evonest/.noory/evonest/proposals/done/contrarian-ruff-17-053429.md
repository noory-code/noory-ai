# 제안: ruff 린팅 오류 17개 자동 수정

**우선순위**: low  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

대부분 line length 초과(E501)와 import 정렬(I001) 문제. ruff format --fix로 자동 해결 가능. 수동 개입이 필요한 케이스는 1개뿐(test_cli.py:200 unused import os).

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