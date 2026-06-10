# 제안: JSON 파싱 실패 시 빈 dict 반환으로 데이터 손실 은폐

**우선순위**: medium  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

repositories.py:44, state.py:263에서 JSONDecodeError 발생 시 빈 dict/list를 반환합니다. 이는 손상된 파일이 있을 때 경고만 로깅하고 조용히 실패합니다. 중요 파일(config, progress)의 경우 백업(.bak) 생성 후 복구 시도하거나 명시적으로 실패해야 합니다.

## 관련 파일

- src/evonest/core/repositories.py
- src/evonest/core/state.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*