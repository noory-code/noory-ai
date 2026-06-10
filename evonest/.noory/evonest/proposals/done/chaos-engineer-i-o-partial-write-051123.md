# 제안: 파일 I/O 실패 시 부분 쓰기(partial write) 보호 부재

**우선순위**: high  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

repositories.py:50, state.py:271, state.py:282 등에서 write_text()를 직접 사용합니다. 디스크 풀이나 권한 문제로 쓰기 도중 실패하면 파일이 손상됩니다. atomic write 패턴(임시 파일 생성 후 rename)이 필요합니다. 특히 config.json, progress.json, backlog.json처럼 중요한 상태 파일에 치명적입니다.

## 관련 파일

- src/evonest/core/repositories.py
- src/evonest/core/state.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*