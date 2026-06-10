# 제안: 페르소나와 개선 제안 간의 소유권 관계를 명시적 도메인 개념으로 분리

**우선순위**: high  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 코드에서 Persona는 mutations/ 안에 JSON으로 정의되고, Proposal은 .evonest/proposals/ 안에 마크다운으로 저장됩니다. 하지만 "어떤 페르소나가 어떤 제안을 만들었는가"라는 관계는 파일명과 메타데이터에 암시적으로 숨어있고, 명확한 도메인 엔티티로 표현되지 않습니다. Project Identity의 Mission("19 specialist personas at your codebase")과 Product Direction("persona community sharing")을 고려하면, Persona가 일급 도메인 객체여야 하고, Proposal과의 관계(authored_by, reviewed_by 등)가 명시적이어야 합니다. 현재는 repositories.py의 ProposalRepository가 파일 시스템 추상화에 가까울 뿐, Persona-Proposal 관계를 도메인 모델로 표현하지 않습니다. 이는 향후 "persona community sharing" 기능 구현 시 필연적으로 리팩토링이 필요해질 영역입니다. 추천: PersonaProposal이라는 도메인 엔티티를 정의하고, Repository 패턴에서 이 관계를 명시적으로 관리하도록 설계를 개선하세요.

## 관련 파일

- src/evonest/core/repositories.py
- src/evonest/core/state.py
- src/evonest/core/mutations.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*