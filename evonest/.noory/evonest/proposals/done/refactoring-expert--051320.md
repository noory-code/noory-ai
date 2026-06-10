# 제안: 프롬프트 조립 로직 추상화

**우선순위**: medium  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py의 run_observe, run_plan, run_execute 함수들이 모두 유사한 parts 리스트 생성 및 조인 패턴 사용. PromptBuilder 클래스나 체인 패턴으로 추상화하여 중복 제거 및 일관성 향상 가능.

## 관련 파일

- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*