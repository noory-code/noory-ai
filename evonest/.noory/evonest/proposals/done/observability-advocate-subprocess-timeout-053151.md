# 제안: subprocess timeout 발생 시 진행 상태 정보 출력

**우선순위**: medium  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py:157에서 timeout 발생 시 'timeout after 600s' 메시지만 남기고 어떤 phase에서, 몇 번째 turn에서 멈췄는지 알 수 없습니다. claude -p의 --output-format text는 중간 진행 상황을 보여주지 않아 디버깅이 어렵습니다. timeout 발생 시 마지막으로 성공한 tool call이나 진행 상태를 로그에 남겨야 합니다.

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*