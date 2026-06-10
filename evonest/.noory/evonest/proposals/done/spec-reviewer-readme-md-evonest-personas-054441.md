# 제안: README.md에 evonest_personas 도구 추가 누락

**우선순위**: medium  
**작성 페르소나**: spec-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README.md의 MCP Tools 섹션(라인 179-198)에는 16개의 도구가 나열되어 있지만, 실제 구현된 evonest_personas 도구는 목록에 포함되지 않았습니다. evonest_personas는 src/evonest/tools/personas.py에 구현되어 있으며 personas와 adversarials를 리스트/활성화/비활성화하는 중요한 기능입니다. 또한 .claude-plugin/commands/personas.md에도 별도의 slash command로 정의되어 있습니다. 권장사항: README.md의 MCP Tools 표에 evonest_personas 항목 추가.

## 관련 파일

- README.md
- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*