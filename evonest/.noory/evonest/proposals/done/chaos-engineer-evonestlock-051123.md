# 제안: EvonestLock 강제 종료 시 락 파일 정리 실패 처리 부재

**우선순위**: high  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

lock.py:32의 __exit__에서 unlink(missing_ok=True)를 사용하지만 프로세스가 SIGKILL로 강제 종료되면 __exit__가 호출되지 않아 락 파일이 남습니다. 이 경우 사용자가 수동으로 삭제해야 하는데, 시작 시 stale lock 감지 로직(PID 확인 후 자동 정리)이 없습니다.

## 관련 파일

- src/evonest/core/lock.py
- tests/test_lock.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*