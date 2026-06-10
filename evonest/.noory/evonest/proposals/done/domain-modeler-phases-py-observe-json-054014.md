# 제안: phases.py의 observe JSON 파싱 실패 경로 테스트 추가

**우선순위**: low  
**작성 페르소나**: domain-modeler  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py의 _save_observations_from_output()와 _save_all_as_proposals()는 LLM 출력에서 JSON을 추출하지만, JSON이 손상되거나 구조적으로 유효하지만 의미론적으로 잘못된 경우(빈 improvements 배열, 필드 누락)에 대한 테스트가 부족합니다. 적대적 도전(Malicious Input Data)에 따라 다음을 테스트하세요: 1) JSON 블록이 없는 출력, 2) 중첩된 JSON 블록, 3) improvements 필드가 배열이 아닌 경우, 4) id 필드 중복.

## 관련 파일

- tests/test_phases.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*