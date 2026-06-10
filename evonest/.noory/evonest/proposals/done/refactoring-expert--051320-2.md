# 제안: 라인 길이 제한 위반 수정

**우선순위**: low  
**작성 페르소나**: refactoring-expert  
**사이클**: 0  
**상태**: 검토 대기

## 설명

cli.py, claude_runner.py, config.py, phases.py에서 100자 제한 초과 라인 8개 발견. 대부분 help 문자열, 긴 딕셔너리 초기화, 로그 메시지 등. 적절히 개행하여 가독성 향상.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*