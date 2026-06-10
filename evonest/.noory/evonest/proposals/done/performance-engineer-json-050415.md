# 제안: JSON 직렬화/역직렬화 반복 호출 최소화

**우선순위**: medium  
**작성 페르소나**: performance-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

config.py, state.py, repositories.py에서 config.save(), state.write_json() 등이 매번 전체 딕셔너리를 json.dumps()로 직렬화합니다. mutations.py, backlog.py에서 load → 수정 → save 패턴이 반복되며, 특히 orchestrator.py:106 루프에서 매 페르소나마다 동일한 config/state를 다시 읽습니다. 변경 감지(dirty flag)를 추가하고, 메모리 내 객체를 재사용하면 I/O와 직렬화 오버헤드를 줄일 수 있습니다.

## 관련 파일

- src/evonest/core/config.py
- src/evonest/core/state.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*