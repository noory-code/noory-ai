# 제안: backlog.json 전체 파일 read/write를 incremental 업데이트로 변경

**우선순위**: medium  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

backlog.py에서 매번 전체 JSON 파일을 읽고 쓰는 방식입니다. 100x 워크로드에서 backlog에 수천 개 항목이 쌓이면 매 cycle마다 수 MB 파일을 파싱/직렬화하게 됩니다. 파일 기반 append-only 로그 형식이나 SQLite로 전환하여 O(1) 쓰기 성능을 확보해야 합니다.

## 관련 파일

- src/evonest/core/backlog.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*