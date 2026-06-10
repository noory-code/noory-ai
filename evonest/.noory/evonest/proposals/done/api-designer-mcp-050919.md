# 제안: MCP 툴 함수의 매개변수 타입 일관성 개선

**우선순위**: medium  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest_config의 settings 파라미터는 dict[str, object]이고, evonest_personas의 ids는 list[str] | None. 전반적으로 복합 타입 인자의 선택적 처리가 일관적이나, object 타입보다 구체적인 Union 타입(str | int | bool | float)이 API 문서 명확성에 유리함.

## 관련 파일

- src/evonest/tools/config.py
- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*