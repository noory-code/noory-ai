# 제안: import 정렬 및 미사용 import 제거

**우선순위**: low  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

server.py와 여러 테스트 파일에서 import 순서가 뒤섞여 있고 test_cli.py:200에 미사용 os import 존재. ruff format --fix로 자동 수정 가능.

## 관련 파일

- src/evonest/server.py
- tests/test_cli.py
- tests/test_server.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*