# 제안: git ls-files 호출을 캐싱하여 중복 subprocess 제거

**우선순위**: medium  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py:593, phases.py:48-67에서 매 사이클마다 git ls-files를 반복 실행합니다. 100x 워크로드에서는 수천 번의 불필요한 git 프로세스 생성이 발생합니다. 프로젝트 파일 목록을 메모리에 캐싱하고 파일 시스템 변경 시에만 갱신하도록 수정해야 합니다.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*