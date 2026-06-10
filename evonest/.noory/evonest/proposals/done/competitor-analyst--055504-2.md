# 제안: 코드 검토 자동화 기능 부재를 해결하여 팀 워크플로 커버리지 확대

**우선순위**: medium  
**작성 페르소나**: competitor-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 Evonest는 `code_output: pr` 모드를 지원하지만, PR에 대한 자동 리뷰 기능이 없음. GitHub Copilot은 PR 코멘트 자동 생성, Aider는 diff 리뷰 모드 제공. Evonest의 19개 페르소나는 이상적인 멀티 에이전트 코드 리뷰 시스템이 될 수 있음 (security-auditor가 취약점 체크, spec-reviewer가 요구사항 준수 확인, performance-analyst가 병목 분석 등). 제안: (1) 새로운 모드 `evonest review <pr-number>` 추가 — PR diff를 읽고 3-5개 페르소나가 병렬 분석 후 통합 코멘트 생성. (2) GitHub Actions 통합 예시 제공 (PR 생성 시 자동 트리거). (3) 팀 워크플로 문서에 '사람 리뷰 전 Evonest 리뷰' 패턴 추가. 이는 개인 개발자 도구에서 팀 협업 도구로 확장하는 핵심 기능.

## 관련 파일

- docs/configuration.md
- src/evonest/tools/

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*