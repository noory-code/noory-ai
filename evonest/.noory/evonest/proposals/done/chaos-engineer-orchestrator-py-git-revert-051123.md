# 제안: orchestrator.py git revert 실패 시 조용히 무시

**우선순위**: low  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py:791에서 git revert 실패 시 pass로 무시합니다. git stash pop 실패(conflict 등)가 발생해도 사용자에게 알리지 않아 작업 내용을 잃을 수 있습니다. 최소한 경고 로그 필요.

## 관련 파일

- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*