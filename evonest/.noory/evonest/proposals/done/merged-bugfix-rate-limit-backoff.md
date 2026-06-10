# 제안: rate limit 재시도 개선 — exponential backoff 및 로깅 추가

**우선순위**: low
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/core/claude_runner.py` 121, 149번 줄에서 rate limit 재시도가 고정 30초 대기를 사용하고, `_retry=False`로 인해 1회만 재시도한다. exponential backoff가 없다.

## 구현 단계

1. `src/evonest/core/claude_runner.py` 파일 열기
2. rate limit 재시도 로직 찾기 (429 핸들러)
3. 로깅 추가: `logger.warning(f"Rate limited (429). Retry {attempt}/{max_retries} after {delay}s")`
4. 현재 동작을 설명하는 주석 추가하여 재시도 전략 문서화
5. exponential backoff 적용 검토: 30초, 60초, 120초로 최대 3회 재시도

## 대상 파일

- src/evonest/core/claude_runner.py

## 검증

- `uv run pytest tests/test_claude_runner.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
