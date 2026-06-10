# 제안: 병렬 페르소나 실행을 위한 동시성 제한 설정 필요

**우선순위**: medium  
**작성 페르소나**: future-proofer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ROADMAP.md의 다음 마일스톤에 '병렬 페르소나 실행'이 명시되어 있습니다. 현재 코드는 순차 실행만 지원하며, 병렬 실행 시 claude -p 서브프로세스 폭증으로 인한 시스템 부하와 API rate limit 위험이 있습니다. 동시 실행 제한(예: max_parallel_personas=3)을 미리 설계해야 합니다.

## 관련 파일

- src/evonest/core/config.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*