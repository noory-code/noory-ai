# 제안: mypy strict 모드 타입 에러 수정 필요

**우선순위**: high  
**작성 페르소나**: ecosystem-scanner  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9-19에서 3개의 타입 파라미터 누락 에러 발생. dict 제네릭 타입에 type-arg 명시 필요. strict 모드에서 빌드 실패.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*