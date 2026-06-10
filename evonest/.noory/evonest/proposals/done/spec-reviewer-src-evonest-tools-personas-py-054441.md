# 제안: src/evonest/tools/personas.py의 타입 힌트 누락 수정

**우선순위**: high  
**작성 페르소나**: spec-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy 타입 체크에서 src/evonest/tools/personas.py:9-10, 19에서 generic type dict에 대한 타입 파라미터가 누락되었다는 오류가 발생합니다. Quality Standards에 명시된 'Type checking passes: uv run mypy src/evonest/ (strict mode)'를 충족하지 못하고 있습니다. dict → dict[str, bool] 등으로 명시적 타입 지정 필요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*