# 제안: personas.py의 generic dict 타입 힌트 명시

**우선순위**: medium  
**작성 페르소나**: performance-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9,10,19에서 dict 타입 파라미터가 누락되어 mypy strict 모드에서 에러 발생. dict[str, Any] 또는 TypedDict 정의로 타입 안전성을 확보해야 합니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*