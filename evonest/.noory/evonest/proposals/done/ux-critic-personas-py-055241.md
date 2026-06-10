# 제안: personas.py의 제네릭 타입 파라미터 추가

**우선순위**: high  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy strict 모드에서 3개 에러 발생: dict → dict[str, Any] 명시 필요. 타입 안전성 보장을 위해 수정.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*