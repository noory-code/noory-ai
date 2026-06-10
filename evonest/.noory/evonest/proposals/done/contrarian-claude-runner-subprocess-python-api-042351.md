# 제안: claude_runner의 subprocess 호출을 Python API로 대체 검토

**우선순위**: low  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 claude_runner.run()은 subprocess로 'claude -p' CLI를 호출. 최근 커밋 히스토리에서 Popen 블로킹, stderr 스트리밍, 타임아웃 등 subprocess 관리 이슈가 반복됨(5개 연속 fix 커밋). 만약 Claude SDK가 Python API를 제공한다면 subprocess 대신 직접 호출로 전환하면 에러 핸들링, 타임아웃, 스트리밍이 단순화됨. 검토 필요: Claude SDK Python API 존재 여부 및 stdio transport 대체 가능성.

## 관련 파일

- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*