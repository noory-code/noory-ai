# 제안: tools/ 계층에서 core/ 계층으로의 직접 import 제거

**우선순위**: medium  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

tools/analyze.py, tools/evolve.py 등이 core/orchestrator를 직접 호출합니다. MCP 도구 계층(tools/)이 도메인 로직(core/)을 직접 알고 있는 것은 의존성 방향 위반입니다. 대신 tools/는 얇은 어댑터로 두고 핵심 로직은 core/에 두되, 공개 API를 별도 파사드(예: EvolutionService)로 노출하여 tools/가 그것만 의존하도록 해야 합니다.

## 관련 파일

- src/evonest/tools/analyze.py
- src/evonest/tools/evolve.py
- src/evonest/tools/improve.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*