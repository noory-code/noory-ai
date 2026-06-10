# 제안: ruff 린트 에러 수정 (라인 길이, import 정렬)

**우선순위**: medium  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

17개 ruff 에러 발견 (9개 자동 수정 가능). 주요 이슈: E501 라인 길이 초과 (100자 제한), I001 import 정렬 불일치, F401 미사용 import. 일관된 코드 스타일 유지 필요.

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