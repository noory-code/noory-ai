# 제안: ruff 린팅 에러 17건 해결 필요

**우선순위**: medium  
**작성 페르소나**: ecosystem-scanner  
**사이클**: 0  
**상태**: 검토 대기

## 설명

line-length 초과 7건, import 정렬 오류 9건, 미사용 import 1건. 대부분 자동 수정 가능 (--fix). 코드 품질 기준 준수를 위해 수정 권장.

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