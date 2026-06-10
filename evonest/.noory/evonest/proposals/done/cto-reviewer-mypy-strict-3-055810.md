# 제안: 타입 안전성 강화 — mypy strict 모드 위반 3건 해결

**우선순위**: medium  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/tools/personas.py에서 generic type 'dict' 사용 시 타입 파라미터 누락으로 mypy strict 모드 위반 3건 발생. 프로젝트 정체성 문서의 'Quality Standards'에서 mypy strict 모드 통과를 명시했으나 현재 위반 상태. 비즈니스 영향: (1) CI에서 타입 체킹 실패 시 배포 차단 가능 (2) 커뮤니티 기여자에게 품질 표준 불일치 신호 전달. 제안: personas.py 9~19번째 줄의 dict → dict[str, Any] 또는 적절한 TypedDict로 변경하여 strict 모드 준수.

## 관련 파일

- src/evonest/tools/personas.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*