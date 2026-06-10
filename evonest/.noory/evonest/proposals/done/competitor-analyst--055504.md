# 제안: 경쟁사 대비 차별화 지점을 명시적으로 문서화

**우선순위**: high  
**작성 페르소나**: competitor-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README.md에 비교표가 있지만 핵심 차별점이 묻혀있음. Aider/Cursor는 '단일 AI 에이전트 + 에디터 통합'으로 시장을 장악했고, GitHub Copilot Workspace는 '웹 UI + 사전 정의 워크플로'로 포지셔닝됨. Evonest의 진정한 차별점은 '적응형 다중 페르소나 시스템'과 'MCP 네이티브 통합'인데 이를 전면에 배치하지 않고 있음. 제안: (1) README 최상단에 '왜 19개 페르소나가 필요한가'를 구체적 시나리오로 설명 (예: security-auditor가 발견한 취약점을 chaos-engineer가 검증하고 performance-analyst가 최적화하는 사이클). (2) 'MCP-first' 아키텍처의 이점을 명시 (Claude Code 생태계 내 네이티브 툴 공유, 컨텍스트 연속성). (3) 경쟁사가 할 수 없는 것을 강조: Aider는 페르소나 전환 불가, Copilot Workspace는 자율 학습 불가.

## 관련 파일

- README.md
- docs/architecture.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*