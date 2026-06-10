# Proposal: 에러 메시지 품질에 대한 테스트 커버리지 추가

**Priority**: low  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

tests/test_claude_runner.py, tests/test_orchestrator.py, tests/test_phases.py에서
stderr를 테스트하지만, 에러 메시지가 실제로 actionable한지(파일 경로, 명령어, 해결 방법 포함)는 검증하지 않습니다. 에러
메시지가 사용자 친화적이고 디버깅에 충분한 정보를 제공하는지 테스트하는 케이스를 추가해야 합니다.

## Related Files

- tests/test_claude_runner.py
- tests/test_orchestrator.py
- tests/test_phases.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*