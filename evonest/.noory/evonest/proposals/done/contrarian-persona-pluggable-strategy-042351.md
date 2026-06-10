# 제안: Persona 가중치 선택 알고리즘을 pluggable strategy로 추출

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 persona 선택 로직이 hardcoded되어 있을 가능성 높음(mutations.py 또는 orchestrator.py). adaptive learning(성공한 페르소나가 더 자주 실행)이 핵심 가치인데, 다양한 선택 전략(epsilon-greedy, UCB, Thompson sampling 등)을 실험하려면 전략 패턴으로 추상화 필요. 현재는 알고리즘 변경이 코드 전체 수정을 요구할 것으로 예상.

## 관련 파일

- src/evonest/core/mutations.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*