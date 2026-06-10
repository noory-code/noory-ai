# 제안: claude_runner.py의 악의적 프롬프트 인젝션 경계 테스트 추가

**우선순위**: low  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py는 사용자 제공 prompt를 subprocess 명령으로 전달하지만, 프롬프트 인젝션 공격(특수문자, 개행, 셸 이스케이프 시도)에 대한 명시적 테스트가 존재하지 않습니다. 현재 tests/test_claude_runner.py는 정상 입력과 타임아웃만 검증합니다. 제안: 적대적 도전(Malicious Input Data)에 따라 특수문자가 포함된 프롬프트, 극도로 긴 프롬프트(1MB+), 잘린 UTF-8 바이트, 널 문자, 셸 메타문자(
, &&, |, >, $())가 포함된 입력을 테스트하여 안전하게 처리되는지 확인하세요.

## 관련 파일

- tests/test_claude_runner.py
- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*