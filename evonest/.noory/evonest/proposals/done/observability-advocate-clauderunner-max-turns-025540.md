# Proposal: ClaudeRunner의 max turns 도달 시 부분 출력 손실

**Priority**: medium  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

claude_runner.py:82-94에서 max turns 도달 시 output을 빈 문자열로 설정하여 부분 결과를 버립니다. 디버깅 시
어디까지 진행되었는지 알 수 없습니다. 부분 출력을 보존하고 메타데이터에 'truncated_reason: max_turns'를 추가하여 진단
가능성을 높여야 합니다.

## Related Files

- src/evonest/core/claude_runner.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*