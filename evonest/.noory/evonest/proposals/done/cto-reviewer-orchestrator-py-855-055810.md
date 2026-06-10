# 제안: orchestrator.py 복잡도 완화 — 855줄 대형 모듈 분해 필요

**우선순위**: high  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py가 855줄로 단일 모듈 중 가장 크며, run_cycles/run_analyze/run_improve 등 여러 진입점을 포함하고 있습니다. 이는 신규 기여자 온보딩을 어렵게 만들고, 유지보수 시 변경 영향 범위 파악을 지연시킵니다. 비즈니스 영향: (1) 새로운 모드 추가 시 회귀 위험 증가 (2) 병렬 페르소나 실행 등 ROADMAP 항목 구현 시 기존 로직과 얽혀 개발 속도 저하. 제안: CycleOrchestrator 클래스로 상태를 캡슐화하고, 각 모드(analyze/improve/evolve)를 별도 전략 객체로 분리하여 orchestrator.py를 진입점 라우터로만 유지. 이를 통해 신규 모드 추가 시 기존 코드 수정 최소화 가능.

## 관련 파일

- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*