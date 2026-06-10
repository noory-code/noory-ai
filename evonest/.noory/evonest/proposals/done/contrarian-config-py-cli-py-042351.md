# 제안: config.py와 cli.py의 라인 길이 초과 수정

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ruff에서 라인 길이 100자 초과 경고 4건 발생. Quality Standards에 'ruff format' 필수 명시되어 있으나 현재 통과하지 못함. 자동 포맷팅으로 해결 가능.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*