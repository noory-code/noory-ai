# 제안: phase 실행 시간 측정 및 로깅 추가

**우선순위**: medium  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 orchestrator.py에서 전체 cycle 시간만 측정합니다 (257: cycle_start). 각 phase(observe, plan, execute, verify)별 실행 시간을 측정하지 않아 병목 지점을 파악할 수 없습니다. 각 phase 시작/종료 시점에 타임스탬프를 로깅하고 PhaseResult에 duration_seconds 필드를 추가해야 합니다.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*