# 제안: tools/personas.py의 Generic 타입 누락 수정

**우선순위**: high  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9, 10, 19 라인에서 dict 타입에 대한 타입 파라미터가 누락되어 mypy strict 모드 검사를 통과하지 못합니다. dict[str, Any]로 명시해야 합니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*