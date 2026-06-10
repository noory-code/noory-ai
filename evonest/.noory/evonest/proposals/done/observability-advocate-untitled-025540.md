# Proposal: 전역 예외 핸들러에 실행 컨텍스트 추가

**Priority**: medium  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

cli.py:207-209와 _runner.py:135-137에서 Exception을 포괄적으로 잡아 단순히 str(exc)만 출력합니다. 스택
트레이스, 실행 중이던 명령, 프로젝트 경로, 설정 값 등의 컨텍스트가 없어 production 이슈 재현이 어렵습니다. 에러 발생 시 충분한
진단 정보를 로깅해야 합니다.

## Related Files

- src/evonest/cli.py
- src/evonest/_runner.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*