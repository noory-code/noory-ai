# 제안: Git 명령어 실행 로직 중복 제거

**우선순위**: medium  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py와 phases.py에서 subprocess.run을 통한 git 명령어 실행 패턴이 23회 반복됨. timeout, cwd, capture_output 설정이 동일한 패턴으로 반복. GitRepository 헬퍼 클래스나 유틸리티 함수로 추출 가능.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*