# 제안: Evonest가 정말 자율 진화인가, 아니면 복잡한 배치 실행기인가?

**우선순위**: high  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

코드베이스를 분석한 결과, Evonest는 '자율 진화'라기보다는 사전 정의된 19개 페르소나를 순차 실행하는 배치 오케스트레이터에 가까움. 진정한 자율성은 시스템이 자신의 목표를 설정하고, 실패에서 학습하여 접근법을 근본적으로 변경할 수 있어야 하는데, 현재는 weighted random selection과 hard-coded phase sequence만 있음. Meta-observe가 새 페르소나를 동적 생성하긴 하지만, 이는 여전히 사전 정의된 템플릿 내에서 작동함. Project Identity의 Mission은 '적응형 지능'을 강조하지만, 실제 구현은 성공률 기반 가중치 조정에 불과함. 제안: (1) reinforcement learning 기반 Phase 순서 변경 가능성, (2) 실패 패턴 분석 후 새로운 mutation 전략 자동 합성, (3) 장기 목표(예: test coverage 90%)를 설정하고 이를 달성하기 위한 하위 목표를 스스로 분해하는 메커니즘 추가를 검토해야 함.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/mutations.py
- src/evonest/core/progress.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*