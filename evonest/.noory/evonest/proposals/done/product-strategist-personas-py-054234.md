# 제안: 타입 체크 오류 수정 (personas.py)

**우선순위**: high  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py의 3개 타입 체크 오류 수정 필요. dict 타입에 제네릭 파라미터 누락 (dict[str, Any]로 명시 필요). Quality Standards에서 'Type checking passes: mypy strict mode' 요구사항 위반.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*