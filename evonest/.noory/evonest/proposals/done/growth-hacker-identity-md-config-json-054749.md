# 제안: 빈 또는 손상된 파일 복원력 테스트 — identity.md, config.json 제로바이트 상황 대응

**우선순위**: medium  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

사용자가 실수로 identity.md를 삭제하거나, 디스크 공간 부족으로 config.json이 제로바이트가 될 수 있습니다. repositories.py의 _read_json()은 JSONDecodeError를 잡아 빈 dict를 반환하지만, identity.md가 빈 문자열일 때 observe 단계에서 어떤 동작을 하는지 명확하지 않습니다. test_identity_read_missing은 파일 부재만 확인하고, '파일은 존재하지만 내용이 비어있음' 케이스가 누락되었습니다. 이 경우 기본 템플릿으로 자동 복구하거나 명확한 에러 메시지를 제공해야 합니다.

## 관련 파일

- tests/test_repositories.py
- tests/test_phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*