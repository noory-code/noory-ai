# 제안: ruff E501 line-too-long 오류 수정 (8건)

**우선순위**: low  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/cli.py:182, claude_runner.py:133/144, config.py:53/58/63/259, phases.py:484에서 100자 제한을 초과합니다. 가독성을 위해 줄 길이를 100자 이내로 조정하거나 ruff format --fix 실행이 필요합니다.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*