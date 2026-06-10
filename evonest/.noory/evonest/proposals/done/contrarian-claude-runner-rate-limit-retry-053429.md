# 제안: claude_runner의 rate limit retry 로직 테스트 추가

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py:146-150에 rate limit 감지 및 재시도 로직이 있으나, 이를 테스트하는 케이스가 없음. 429 응답 시나리오를 mock하여 retry가 정상 작동하는지 검증 필요.

## 관련 파일

- tests/test_claude_runner.py
- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*