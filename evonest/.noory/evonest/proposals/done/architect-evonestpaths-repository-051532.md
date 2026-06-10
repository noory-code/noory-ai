# 제안: EvonestPaths와 Repository 간 결합도 낮추기

**우선순위**: low  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

repositories.py의 모든 Repository가 EvonestPaths 인스턴스를 받습니다. 그러나 각 Repository는 실제로 하나의 경로만 필요합니다(예: IdentityRepository는 identity_path만). 생성자에서 구체적인 Path만 받도록 변경하면 Repository 단위 테스트 시 EvonestPaths 전체를 mock할 필요가 없어집니다.

## 관련 파일

- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*