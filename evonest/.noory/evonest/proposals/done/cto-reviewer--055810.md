# 제안: 테스트 커버리지 격차 — 통합 테스트 부재로 인한 회귀 위험

**우선순위**: medium  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

355개 테스트 모두 단위 테스트이며, orchestrator.py의 run_cycles 전체 흐름을 검증하는 통합 테스트가 없습니다. tests/test_orchestrator.py는 모킹된 단위 테스트만 포함하고, 실제 git stash/commit/revert 시나리오는 미검증. 비즈니스 영향: 최근 5개 커밋이 모두 claude_runner.py 수정 관련이며 (Popen 블로킹, 재시도 로직 등), 실제 프로덕션 환경에서만 발견되는 버그로 인한 핫픽스 반복. 사용자 신뢰 저하 및 개발팀 수면 시간 감소. 제안: tests/integration/ 디렉토리를 추가하고, 임시 git 저장소에서 전체 사이클을 실행하는 E2E 테스트 작성. git stash 충돌, verify 실패 시 revert, PR 모드 브랜치 생성 등 크리티컬 경로 커버.

## 관련 파일

- tests/test_orchestrator.py
- tests/integration/

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*