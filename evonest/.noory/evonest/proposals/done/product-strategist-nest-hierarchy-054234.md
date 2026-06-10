# 제안: Nest Hierarchy 비전을 위한 멀티 프로젝트 구조 실험

**우선순위**: low  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ROADMAP Vision에서 'Medium nest: 멀티 모듈 오케스트레이션'을 장기 목표로 제시했으나, 현재 ProjectState는 단일 프로젝트만 지원합니다. 비전 실현 전에 아키텍처 검증이 필요합니다. 제안: (1) .evonest/modules.json 포맷 정의 (모듈 간 dependency graph), (2) 실험용 'workspace' 모드 추가 (evonest init --workspace), (3) 멀티 모듈 분석 프로토타입 (루트에서 analyze 실행 시 서브모듈 순회). 이는 대규모 비전의 기술적 타당성을 검증하고, 조기 피드백을 얻기 위한 최소 기능 구현(MVP)입니다. 단, Current Phase가 'v0.3.0 이후 depth levels 우선'이므로 우선순위는 낮음.

## 관련 파일

- src/evonest/core/state.py
- src/evonest/templates/modules.json
- docs/nest-hierarchy.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*