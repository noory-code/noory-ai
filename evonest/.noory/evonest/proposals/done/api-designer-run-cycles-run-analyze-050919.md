# 제안: run_cycles와 run_analyze의 매개변수 순서 불일치

**우선순위**: low  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

run_cycles(orchestrator.py:151)와 run_analyze(orchestrator.py:53)가 동일한 persona_id, adversarial_id, group 파라미터를 받지만 파라미터 순서가 다름. API 일관성을 위해 공통 파라미터는 동일한 순서로 선언하는 것이 원칙.

## 관련 파일

- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*