# 제안: personas.py의 타입 힌트 누락 수정

**우선순위**: low  
**작성 페르소나**: competitor-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9,10,19에서 제네릭 타입 누락 (mypy strict 모드 실패). dict를 dict[str, Any] 또는 구체적 타입으로 수정 필요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*