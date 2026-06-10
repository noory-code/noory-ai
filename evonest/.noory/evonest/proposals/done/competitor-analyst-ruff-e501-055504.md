# 제안: 라인 길이 제한 초과 수정 (ruff E501)

**우선순위**: low  
**작성 페르소나**: competitor-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/cli.py:182와 src/evonest/core/claude_runner.py:133에서 100자 제한 초과. 가독성을 위해 줄바꿈 적용 필요.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*