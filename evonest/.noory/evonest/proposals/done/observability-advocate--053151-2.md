# 제안: 동기식 페르소나 순회를 병렬 실행으로 전환

**우선순위**: high  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

orchestrator.py:106, 255에서 여러 페르소나를 순차적으로 실행합니다 (for i in range(total)). 19개 페르소나를 모두 실행하면 각 페르소나당 평균 2-5분이 소요되므로 총 38-95분이 걸립니다. claude -p 호출은 I/O 바운드 작업이므로 asyncio.gather()를 사용한 병렬 실행으로 전환하면 100x 워크로드에서도 처리 시간이 선형 증가하지 않습니다. config.max_concurrent_personas 옵션 추가 필요.

## 관련 파일

- src/evonest/core/orchestrator.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*