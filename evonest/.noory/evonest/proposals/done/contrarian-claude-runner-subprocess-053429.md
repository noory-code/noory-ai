# 제안: claude_runner의 subprocess 호출을 추상화 레이어로 분리

**우선순위**: high  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.run()이 직접 subprocess를 호출하는데, 최근 5개 커밋이 모두 subprocess 블로킹/타임아웃/stderr 처리 버그 수정임. 이는 subprocess 통신을 직접 다루는 것이 근본적으로 복잡함을 의미함. AsyncIO 기반 프로세스 추상화 또는 별도 ProcessManager 클래스로 분리하면 테스트 가능성과 안정성이 대폭 개선될 것임. 현재는 단일 함수에 retry 로직, stderr 캡처, timeout 처리가 혼재되어 있음.

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*