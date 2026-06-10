# 제안: subprocess 예외 처리 패턴 일관화

**우선순위**: medium  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

Git 명령어 실행 시 일부는 subprocess.SubprocessError 캐치, 일부는 TimeoutExpired만 캐치, 일부는 bare except 사용. 일관된 예외 처리 전략 수립 및 로깅 패턴 통일 필요.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*