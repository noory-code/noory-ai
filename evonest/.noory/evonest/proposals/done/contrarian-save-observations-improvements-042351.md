# 제안: save_observations에서 악의적인 improvements 입력 테스트

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

backlog.save_observations()가 improvements 리스트에서 title이 None이거나 극단적으로 긴 경우(10K+ 문자), files 필드에 경로 탐색 시도('../../sensitive'), category/priority에 임의 값 주입 등을 처리하는지 테스트 필요. 현재는 정상 입력만 테스트됨.

## 관련 파일

- tests/test_backlog.py
- src/evonest/core/backlog.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*