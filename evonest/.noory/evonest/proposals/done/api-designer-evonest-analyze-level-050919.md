# 제안: evonest_analyze의 level 파라미터 이름 모호성

**우선순위**: medium  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest_analyze와 run_analyze 모두 level 파라미터를 사용하나, config.active_level과 혼동 가능. 파라미터 이름을 analysis_depth 또는 depth_preset으로 변경하여 의도를 명확히 표현하는 것이 바람직함.

## 관련 파일

- src/evonest/tools/analyze.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*