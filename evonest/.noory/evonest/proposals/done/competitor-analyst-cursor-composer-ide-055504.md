# 제안: 경쟁사 테이블에 Cursor Composer 추가 및 IDE 통합 격차 명시

**우선순위**: medium  
**작성 페르소나**: competitor-analyst  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README 비교표에 Cursor가 있지만 최신 Cursor Composer (멀티 파일 에이전트 모드) 특징이 반영되지 않음. Cursor Composer는 IDE 내 네이티브 멀티 파일 편집으로 개발자 경험(UX) 우위. Evonest는 CLI/MCP 기반이라 별도 컨텍스트 전환 필요. 이는 약점이지만 동시에 강점 — IDE 독립적이므로 VSCode/Zed/Neovim 모두 지원 가능. 제안: (1) 비교표에 'IDE Integration' 행 추가하여 트레이드오프 명시 (Cursor = 네이티브 UX vs Evonest = IDE 불가지론). (2) Claude Code 플러그인 경험 강조 — 이미 IDE 내에서 작동하므로 Cursor와 UX 격차 작음. (3) 향후 Zed/Neovim MCP 클라이언트 지원 가능성 언급.

## 관련 파일

- README.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*