# 제안: orchestrator.py와 phases.py 간 순환 의존성 해소

**우선순위**: high  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py가 phases 모듈의 함수들을 호출하고, phases.py는 다시 backlog, history, progress 등을 직접 호출하는 구조입니다. orchestrator가 856줄의 거대 파일로 성장하면서 단일 책임 원칙을 위배하고 있습니다. cycle 오케스트레이션 로직을 별도 CycleCoordinator 클래스로 분리하고, git 작업은 GitCheckpoint 서비스로 추출하는 것을 제안합니다.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*