# Proposal: MCP 도구 호출 시 에러 처리에 진단 컨텍스트 추가

**Priority**: high  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

tools/improve.py:19-24에서 OSError를 조용히 삼키고 있습니다. 로그 파일 읽기 실패 시 사용자가 문제를 진단할 수 없도록
합니다. 에러 발생 시 파일 경로, 권한 정보, 실패 이유를 로깅하여 프로덕션 문제 추적을 가능하게 해야 합니다.

## Related Files

- src/evonest/tools/improve.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*