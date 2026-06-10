# 제안: phases.py의 prompt 조립 로직을 별도 PromptBuilder로 추출

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

각 phase 함수(run_observe, run_plan, run_execute)가 prompt 템플릿 로드, 변수 치환, context 주입을 직접 수행함. 이는 PromptBuilder 클래스로 분리하면 템플릿 로직이 명확해지고, 테스트 시 prompt 검증이 쉬워짐. 현재는 f-string과 파일 읽기가 혼재되어 있어 프롬프트 로직을 단독으로 테스트하기 어려움.

## 관련 파일

- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*