# 제안: subprocess 타임아웃 시 자식 프로세스 좀비화 위험

**우선순위**: medium  
**작성 페르소나**: chaos-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py:623, 648에서 subprocess.TimeoutExpired 발생 시 프로세스가 여전히 실행 중일 수 있지만 kill/terminate 호출 없이 예외만 처리합니다. 장시간 실행되는 빌드/테스트가 타임아웃되면 좀비 프로세스가 남을 수 있습니다.

## 관련 파일

- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*