# 제안: evonest_personas의 응답 포맷 표준화

**우선순위**: low  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest_personas는 마크다운 형식 문자열을 반환하지만 다른 MCP 툴들(status, progress)은 JSON 또는 플레인 텍스트. 일관된 응답 포맷 전략(모두 markdown, 모두 JSON, 또는 명시적 구분) 수립 필요.

## 관련 파일

- src/evonest/tools/personas.py
- src/evonest/tools/status.py
- src/evonest/tools/progress.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*