# 제안: subprocess 기반 claude -p 호출을 Python SDK 직접 호출로 대체 검토

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 모든 LLM 호출이 subprocess로 'claude -p'를 실행함. 이는 (1) 프로세스 생성 오버헤드, (2) stdout/stderr 파싱 복잡도, (3) 최근 5개 커밋이 모두 subprocess 버그 수정인 점에서 근본적인 설계 문제로 보임. Anthropic Python SDK를 직접 사용하면 이러한 복잡도가 사라지고, 스트리밍, 토큰 카운팅, 더 정교한 에러 처리가 가능해짐. 단, Claude Code CLI가 제공하는 도구 실행 컨텍스트를 재구현해야 하는 비용이 있음. 프로젝트 아이덴티티는 'MCP-native'를 강조하지만, MCP 서버는 이미 FastMCP로 구현되어 있으므로, LLM 호출만 직접 처리해도 아이덴티티에 어긋나지 않음.

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*