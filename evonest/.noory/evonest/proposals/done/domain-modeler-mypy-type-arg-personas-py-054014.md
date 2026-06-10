# 제안: mypy type-arg 오류 수정 (personas.py)

**우선순위**: low  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9, 10, 19에서 Missing type parameters for generic type "dict" 경고가 발생합니다. Quality Standards("Type checking passes: mypy strict mode")에 따라 dict를 dict[str, Any] 등으로 명시하여 타입 안전성을 강화하세요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*