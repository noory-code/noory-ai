# 제안: E501 라인 길이 제한 위반 수정

**우선순위**: low  
**작성 페르소나**: future-proofer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ruff 검사에서 4개 파일에서 라인 길이 100자 초과 발견. 코드 가독성 유지를 위해 수정 필요.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*