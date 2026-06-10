# 제안: personas.py의 generic dict 타입 힌트 추가

**우선순위**: low  
**작성 페르소나**: monetization-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy strict 모드에서 src/evonest/tools/personas.py의 9, 10, 19번 줄에서 'Missing type parameters for generic type dict' 경고가 발생합니다. 이는 `dict` 대신 `dict[str, Any]` 또는 적절한 타입을 명시해야 합니다. 현재 품질 기준인 'Type checking passes: uv run mypy src/evonest/' 달성을 위해 수정이 필요합니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*