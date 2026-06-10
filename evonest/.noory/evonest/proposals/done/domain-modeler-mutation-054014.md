# 제안: Mutation 선택 로직을 도메인 서비스로 추출하여 비즈니스 규칙 명시화

**우선순위**: medium  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mutations.py의 select_mutation() 함수는 adversarial_probability, 페르소나 가중치, group 필터링 등 복잡한 비즈니스 규칙을 구현합니다. 하지만 이 함수는 단순 유틸리티로 작성되어 있고, 도메인 서비스나 전략 패턴으로 구조화되지 않았습니다. Mission("19 specialist personas... with adaptive learning")을 고려하면, "어떤 페르소나를 선택할 것인가"는 진화 엔진의 핵심 도메인 로직입니다. 현재는 가중치 기반 샘플링, 그룹 필터링, adversarial 주입 로직이 한 함수에 절차적으로 뭉쳐있어 확장이나 테스트가 어렵습니다. 제안: MutationSelectionStrategy 도메인 서비스를 정의하고, WeightedPersonaSelector, GroupFilter, AdversarialInjector를 독립 컴포넌트로 분리하세요. 이렇게 하면 향후 "multi-module orchestration"이나 사용자 정의 선택 전략 추가가 용이해집니다.

## 관련 파일

- src/evonest/core/mutations.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*