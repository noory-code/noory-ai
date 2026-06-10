# 제안: _count_source_files의 Path.rglob 순회를 git ls-files로 대체

**우선순위**: low  
**작성 페르소나**: performance-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py:620의 _count_source_files()는 Path.rglob('*.py')로 전체 디렉토리를 순회합니다. 대규모 monorepo에서 .venv, node_modules 등 제외 디렉토리가 많을 경우 I/O 오버헤드가 큽니다. 이미 phases.py:63에서 git ls-files --cached --others --exclude-standard를 사용하여 .gitignore를 존중하는 파일 목록을 얻고 있으므로, 동일한 방식으로 전환하면 더 빠릅니다.

## 관련 파일

- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*