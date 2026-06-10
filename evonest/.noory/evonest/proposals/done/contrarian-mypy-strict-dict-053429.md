# 제안: mypy strict 모드의 dict 타입 파라미터 누락 수정

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9-19에서 dict 타입에 타입 파라미터 누락 (dict[str, Any]로 명시 필요). 현재 3개 타입 오류가 발생 중이며, strict mypy 설정에 맞춰 수정 필요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*