# 제안: ruff E501 라인 길이 위반 수정 (4개 파일)

**우선순위**: low  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

cli.py:182, claude_runner.py:133, 144, config.py:53, 58에서 라인 길이 100자 제한 초과. Quality Standards("Linting passes")에 따라 자동 포맷팅 또는 수동 줄바꿈으로 수정 필요.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*