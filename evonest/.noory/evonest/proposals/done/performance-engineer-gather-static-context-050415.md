# 제안: 정적 컨텍스트 수집(_gather_static_context) 결과를 캐싱

**우선순위**: medium  
**작성 페르소나**: performance-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py:35의 _gather_static_context()는 git log, git ls-files, pytest --collect-only를 매 observe 호출마다 실행합니다. orchestrator.py:106, 255에서 반복문 내부에서 여러 페르소나 실행 시 동일한 git 상태를 반복 조회합니다. 단일 analyze/improve 실행 내에서는 파일 트리와 git 히스토리가 변경되지 않으므로 첫 호출 시 캐싱하고 재사용하면 불필요한 subprocess 호출을 제거할 수 있습니다.

## 관련 파일

- src/evonest/core/phases.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*