# 제안: personas.py에서 dict 타입 파라미터 명시

**우선순위**: low  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy가 src/evonest/tools/personas.py:9-19에서 3건의 type-arg 오류를 보고합니다. Generic dict 타입에 파라미터가 누락되어 타입 안전성이 떨어집니다. dict[str, Any] 또는 적절한 TypedDict로 교체해야 합니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*