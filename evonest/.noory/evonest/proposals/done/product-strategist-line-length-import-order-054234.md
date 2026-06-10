# 제안: 린트 오류 수정 (line length, import order)

**우선순위**: medium  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

17개 ruff 경고 중 9개는 자동 수정 가능. E501(line too long) 8건, I001(import order) 8건, F401(unused import) 1건. ruff format --fix로 대부분 해결 가능. Quality Standards 준수 필요.

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