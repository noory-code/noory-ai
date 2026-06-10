# 제안: tools/personas.py의 타입 힌트 누락 수정

**우선순위**: high  
**작성 페르소나**: future-proofer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy strict 모드에서 3개의 타입 에러 발생: tools/personas.py:9-19의 dict 타입에 제네릭 파라미터가 누락되었습니다. 타입 안정성 확보를 위해 dict[str, Any] 등으로 명시해야 합니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*