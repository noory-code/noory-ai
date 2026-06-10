# 제안: claude_runner.py의 rate limit 재시도 무한 루프 가능성

**우선순위**: low  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py:121, 149에서 _retry=False로 한 번만 재시도하지만, API가 지속적으로 429를 반환하면 30초 대기 후 한 번만 재시도하고 실패합니다. exponential backoff나 최대 재시도 횟수 제한이 명시적이지 않습니다. (현재는 안전하나 향후 로직 변경 시 위험)

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*