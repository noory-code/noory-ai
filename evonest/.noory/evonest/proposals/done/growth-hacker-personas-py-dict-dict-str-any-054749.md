# 제안: personas.py 타입 힌트 수정 — dict → dict[str, Any]

**우선순위**: low  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py:9, 10, 19에서 제네릭 타입 힌트가 누락되어 mypy strict mode에서 에러가 발생합니다. 이는 CI/CD에서 빌드 실패를 유발할 수 있으며, 타입 안정성을 저해합니다. dict를 dict[str, Any]로 수정하면 즉시 해결됩니다.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*