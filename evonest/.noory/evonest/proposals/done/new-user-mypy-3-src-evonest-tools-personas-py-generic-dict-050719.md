# 제안: mypy 타입 오류 3건 방치 — src/evonest/tools/personas.py의 generic dict 타입 누락

**우선순위**: high  
**작성 페르소나**: new-user  
**사이클**: 0  
**상태**: 검토 대기

## 설명

mypy 실행 결과 src/evonest/tools/personas.py:9, 10, 19줄에서 'Missing type parameters for generic type "dict"' 오류가 발생한다. Quality Standards에서 'mypy --strict' 통과를 명시했지만 실제로는 3건의 오류가 존재한다. 신규 사용자가 'uv run mypy src/evonest/'를 실행했을 때 프로젝트 품질에 의문을 가질 수 있다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*