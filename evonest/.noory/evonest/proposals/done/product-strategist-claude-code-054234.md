# 제안: Claude Code 플러그인 우선 전략 강화 - 독립 실행 경로 축소

**우선순위**: medium  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

Product Direction에서 'Claude Code의 일급 참여자로 설계, 독립 도구가 아님'을 명시했으나, README.md와 문서는 여전히 CLI 사용법을 동등하게 강조합니다 (Quick Start에서 CLI 명령 먼저 등장). 이는 사용자에게 혼란을 주고 제품 포지셔닝을 약화시킵니다. 제안: (1) README 재구성 - Plugin 설치를 첫 번째 경로로, CLI는 'Advanced / Self-hosting' 섹션으로 이동, (2) CLI 명령어 deprecation 경고 추가 (단, 플러그인 개발자와 self-evolution 워크플로우는 유지), (3) 플러그인 전용 기능 추가 고려 (예: Claude 대화 컨텍스트 연동).

## 관련 파일

- README.md
- CLAUDE.md
- src/evonest/cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*