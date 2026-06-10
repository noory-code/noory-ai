# 제안: 병렬 페르소나 실행 인프라 사전 설계 — ROADMAP 다음 항목 구현 준비

**우선순위**: high  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ROADMAP 'Next' 섹션에서 '병렬 분석 (여러 페르소나 동시 실행)' 명시. 현재 orchestrator.py는 순차 실행 구조로 설계되어 있으며 (run_analyze에서 for loop로 persona_queue 순회), 병렬 실행 추가 시 git stash 충돌, backlog 동시 쓰기 등 경합 조건 발생 가능. 비즈니스 영향: 큰 프로젝트에서 19개 페르소나 순차 실행 시 30분+ 소요되어 사용자 이탈 가능성 높음. 병렬 실행 도입 시 5~10분으로 단축 가능하나, 현재 구조에선 리팩토링 부채 큼. 제안: (1) 병렬 실행 전략 문서 작성 (lock granularity, backlog merge 방식) (2) ProjectState에 thread-safe write 메서드 추가 (3) orchestrator.py를 async/await 기반으로 마이그레이션하여 향후 asyncio.gather 사용 가능 구조로 전환.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/state.py
- src/evonest/core/lock.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*