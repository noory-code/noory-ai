# 제안: time.sleep(30) 동기 블로킹을 비동기 백오프로 교체

**우선순위**: high  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py:120, 148에서 rate limit 발생 시 time.sleep(30)으로 30초간 전체 프로세스를 블로킹합니다. 100x 워크로드에서 rate limit이 자주 발생하면 대부분의 시간을 sleep에서 낭비하게 됩니다. asyncio.sleep()으로 교체하고 exponential backoff + jitter 패턴을 적용하여 여러 요청이 동시에 재시도되지 않도록 해야 합니다.

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*