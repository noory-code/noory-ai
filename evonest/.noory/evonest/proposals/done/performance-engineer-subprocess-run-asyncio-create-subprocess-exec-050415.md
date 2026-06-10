# 제안: subprocess.run 동기 블로킹 호출을 asyncio.create_subprocess_exec으로 대체

**우선순위**: high  
**작성 페르소나**: performance-engineer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py:86 및 phases.py:48,62,91의 subprocess.run()은 동기 블로킹 호출로 600초까지 메인 스레드를 점유합니다. orchestrator.py의 run_analyze와 run_improve는 이미 async 함수이지만 내부에서 동기 subprocess를 호출하여 병렬성을 활용하지 못합니다. --all-personas 모드에서 19개 페르소나를 순차 실행하면 19×평균실행시간만큼 지연됩니다. asyncio.create_subprocess_exec으로 전환하면 여러 페르소나를 동시에 실행하여 총 실행 시간을 크게 단축할 수 있습니다.

## 관련 파일

- src/evonest/core/claude_runner.py
- src/evonest/core/phases.py
- src/evonest/core/orchestrator.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*