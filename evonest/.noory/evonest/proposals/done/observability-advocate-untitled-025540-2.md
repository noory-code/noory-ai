# Proposal: 로깅 레벨 설정 및 구조화된 로그 포맷 부재

**Priority**: low  
**Author Persona**: observability-advocate  
**Cycle**: 0  
**Status**: Pending Review

## Description

프로젝트 전체에서 logger를 사용하지만(51회 호출), 로깅 레벨 설정, 포맷터, 핸들러 구성이 명시적으로 보이지 않습니다. 사용자가 디버그
레벨 로그를 활성화하거나 JSON 형식으로 로그를 출력할 방법이 없습니다. 설정 가능한 로깅 설정(레벨, 포맷, 출력 대상)을
config.json에 추가하여 운영 환경 진단을 용이하게 해야 합니다.

## Related Files

- src/evonest/core/config.py
- src/evonest/__init__.py

---

*This proposal was generated during the analysis phase. It has not been implemented yet.*  
*Run it with the improve command, or have the team review and action it.*