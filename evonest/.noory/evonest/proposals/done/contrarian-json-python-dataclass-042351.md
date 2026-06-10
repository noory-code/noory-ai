# 제안: JSON 설정 파일 대신 Python dataclass로 전환 고려

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 .evonest/config.json, backlog.json, progress.json 등 여러 JSON 파일을 수동 파싱/직렬화. EvonestConfig는 dataclass지만 저장은 수동 to_dict/from_dict. 제안: pydantic 또는 dataclass-based 설정 시스템으로 통합하여 타입 안정성 향상 + 검증 자동화. 또는 SQLite 같은 embedded DB로 전환해서 atomic write, 트랜잭션, 쿼리 성능 개선. JSON 파일이 커질수록 전체 read-modify-write는 race condition 및 성능 저하 위험.

## 관련 파일

- src/evonest/core/config.py
- src/evonest/core/backlog.py
- src/evonest/core/progress.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*