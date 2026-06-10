# 제안: EvonestConfig._apply_dict의 public 인터페이스 부재

**우선순위**: low  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

config.py의 _apply_dict는 언더스코어 프리픽스로 내부 메서드이나, 실제로 MCP 툴에서 간접적으로 호출됨. public API로 노출할 의도가 있다면 update() 등 명시적 이름으로 변경하거나, 완전 private 의도라면 호출 경로 재검토 필요.

## 관련 파일

- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*