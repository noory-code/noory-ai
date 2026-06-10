# 제안: config 객체 접근 방식 통일

**우선순위**: medium  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mutations.py의 select_mutation 함수에서 config를 object 타입으로 받아 getattr로 동적 접근. disabled_persona_ids와 disabled_personas 두 가지 이름을 모두 체크하는 레거시 호환 로직 존재. EvonestConfig 타입으로 명시하고 단일 속성명으로 통일 필요.

## 관련 파일

- src/evonest/core/mutations.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*