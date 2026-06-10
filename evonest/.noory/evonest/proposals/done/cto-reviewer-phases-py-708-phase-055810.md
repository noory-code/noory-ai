# 제안: phases.py 책임 분리 — 708줄 모듈에서 phase별 모듈로 재구성

**우선순위**: medium  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py가 708줄이며 observe/plan/execute/verify 4개 페이즈 + 12개 함수를 모두 포함하고 있습니다. 각 페이즈는 독립적인 관심사(도구 권한, 출력 파싱 로직, 에러 처리)를 가지지만 단일 파일에 혼재되어 있어, 특정 페이즈 수정 시 다른 페이즈 코드까지 검토해야 합니다. 비즈니스 영향: ROADMAP의 'analysis depth levels' 구현 시 observe 로직만 수정하면 되지만 현재 구조에선 708줄 전체를 파악해야 하므로 개발 지연 발생. 제안: core/phases/ 디렉토리를 만들고 observe.py/plan.py/execute.py/verify.py로 분리. 각 모듈은 run_X 함수와 관련 헬퍼만 포함하여 변경 영향 범위를 명확히 격리.

## 관련 파일

- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*