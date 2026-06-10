# Proposal: improve 도구의 비동기 subprocess 실패 시 진단 정보 부족

**Priority**: high  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

tools/improve.py:42-47에서 subprocess가 stdout/stderr을 DEVNULL로 리디렉션하여 실패 시 아무런 진단
정보가 남지 않습니다. 프로세스가 실패해도 사용자는 왜 실패했는지 알 수 없습니다. stderr을 캡처하고 exit code가 0이 아닐 때
로깅하여 실패 원인 추적을 가능하게 해야 합니다.

## Related Files

- src/evonest/tools/improve.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*