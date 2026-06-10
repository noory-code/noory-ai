# 제안: max_turns 값의 동적 스케일링 로직 강화

**우선순위**: medium  
**작성 페르소나**: future-proofer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py:79-86에서 파일 수 기반으로 max_turns를 계산하지만, 파일 크기나 복잡도는 고려하지 않습니다. 10,000개의 작은 설정 파일과 100개의 복잡한 소스 파일은 다르게 처리되어야 합니다. LOC(Lines of Code) 또는 AST 복잡도 기반 스케일링을 고려해야 합니다.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*