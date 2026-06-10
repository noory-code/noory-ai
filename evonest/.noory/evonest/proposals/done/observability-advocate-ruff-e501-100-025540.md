# Proposal: Ruff 린팅 경고 수정 (E501: 100자 제한 초과)

**Priority**: low  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

src/evonest/core/phases.py:375, 388, src/evonest/core/process_manager.py:54,
tests/test_phases.py:596, 607, tests/test_server.py:247에서 라인 길이가 100자를 초과합니다.
일관된 코드 포맷팅을 위해 ruff format으로 자동 수정하거나 라인을 분할해야 합니다.

## Related Files

- src/evonest/core/phases.py
- src/evonest/core/process_manager.py
- tests/test_phases.py
- tests/test_server.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*