# 제안: 대화형 프롬프트의 기본값 표시 개선

**우선순위**: low  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest init의 level 선택 프롬프트에서 기본값이 'standard'지만, 사용자가 Enter만 누르면 어떤 값이 선택되는지 명확하지 않을 수 있음. '[standard]' 같은 표시로 기본값 강조. 다른 대화형 프롬프트(identity refresh y/n 등)도 동일 패턴 적용.

## 관련 파일

- src/evonest/core/initializer.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*