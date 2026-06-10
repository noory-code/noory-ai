# 제안: 하드코딩된 백로그 제한값을 설정으로 이동

**우선순위**: high  
**작성 페르소나**: future-proofer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

backlog.py의 MAX_ATTEMPTS=3, PRUNE_AGE_CYCLES=20이 모듈 레벨 상수로 하드코딩되어 있습니다. 대규모 프로젝트에서는 백로그 항목이 수천 개로 늘어날 수 있고, 프루닝 정책을 유연하게 조정해야 합니다. 이 값들을 EvonestConfig로 이동하고 프로젝트별로 설정 가능하게 만들어야 합니다.

## 관련 파일

- src/evonest/core/backlog.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*