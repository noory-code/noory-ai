# 제안: MCP 도구 파라미터 adversarial 테스트 추가

**우선순위**: high  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

공개 MCP 도구들(evonest_config, evonest_backlog, evonest_identity 등)이 빈 문자열, null, 10K+ 문자열, 유니코드, 개행 문자 등 adversarial 입력에 대한 테스트가 없음. project 경로에 '../../../etc/passwd' 같은 경로 탐색 공격, settings에 거대한 JSON, content에 null bytes 등을 테스트해야 함.

## 관련 파일

- tests/test_backlog.py
- tests/test_config.py
- src/evonest/tools/backlog.py
- src/evonest/tools/config.py
- src/evonest/tools/identity.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*