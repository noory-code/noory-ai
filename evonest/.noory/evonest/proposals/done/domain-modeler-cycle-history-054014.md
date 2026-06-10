# 제안: Cycle과 History의 이중 책임 분리 — 이벤트 소싱 패턴 도입 검토

**우선순위**: medium  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py의 _record_cycle() 함수와 phases.py의 update_progress()는 각 사이클의 결과를 기록하지만, "진행 중인 상태(progress.json)"와 "불변 이력(history/)"이라는 두 가지 책임이 혼재되어 있습니다. 특히 _record_cycle()은 성공/실패 여부를 저장하고, update_progress()는 persona별 가중치를 재계산합니다. Core Values("Adaptive intelligence — successful personas run more often")에 따르면, 페르소나의 성공률은 도메인의 핵심 비즈니스 규칙입니다. 하지만 현재는 이 규칙이 orchestrator와 progress 모듈에 분산되어 있고, "왜 가중치가 변경되었는가"는 history에 기록되지 않습니다. 제안: Cycle을 도메인 이벤트(CycleCompleted, CycleReverted)로 모델링하고, 이벤트 소싱 패턴을 통해 모든 상태 변경을 재구성 가능하게 만드세요. 이렇게 하면 과거 어느 시점의 페르소나 가중치든 재현할 수 있고, "adaptive learning" 로직의 투명성이 높아집니다.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/progress.py
- src/evonest/core/history.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*