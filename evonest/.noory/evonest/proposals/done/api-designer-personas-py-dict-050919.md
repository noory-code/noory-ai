# 제안: personas.py에서 제네릭 dict 타입 힌트 완성

**우선순위**: high  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9,10,19에서 dict 타입에 타입 파라미터가 누락되어 mypy strict 모드 위반. _format_list 함수의 파라미터 personas_toggle, adversarials_toggle를 dict[str, bool]로 명시 필요.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*