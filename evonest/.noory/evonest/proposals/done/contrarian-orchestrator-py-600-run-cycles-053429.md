# 제안: orchestrator.py의 600줄 run_cycles 함수를 단계별 객체로 분해

**우선순위**: high  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

run_cycles() 함수가 856줄에 달하며, Meta-observe, Scout, Mutation 선택, 4개 Phase, Git 체크포인트, Verify, PR 생성을 모두 처리함. 이는 단일 함수가 아니라 CycleOrchestrator 클래스로 리팩토링되어야 함. 각 단계(MetaObserveStep, ObserveStep, PlanStep, ExecuteStep, VerifyStep)를 전략 패턴으로 분리하면 테스트가 훨씬 쉬워지고, 새로운 Phase 추가 시 확장성이 높아짐. 현재는 --all-personas, --cautious, --dry-run 등의 모드가 중첩 if문으로 얽혀 있어 복잡도가 매우 높음.

## 관련 파일

- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*