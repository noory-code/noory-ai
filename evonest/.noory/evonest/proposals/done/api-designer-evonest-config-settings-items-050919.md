# 제안: evonest_config의 settings.items() 키 검증 부재

**우선순위**: medium  
**작성 페르소나**: api-designer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest_config(config.py:9)는 settings dict를 받아 cfg.set()으로 전달하지만, 잘못된 키가 있을 경우 ValueError가 발생하여 일부 설정만 적용되고 중단될 수 있음. 전체 키 유효성 선검증 또는 오류 누적 후 보고 로직 추가 필요.

## 관련 파일

- src/evonest/tools/config.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*