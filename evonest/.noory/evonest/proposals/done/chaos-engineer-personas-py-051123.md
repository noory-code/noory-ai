# 제안: personas.py에서 제네릭 타입 인자 누락

**우선순위**: low  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy 검사 결과 personas.py:9, 10, 19에서 dict 타입에 타입 인자가 누락되어 타입 안전성이 떨어집니다. dict[str, Any]로 명시 필요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*