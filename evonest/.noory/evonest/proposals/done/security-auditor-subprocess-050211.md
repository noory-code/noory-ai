# 제안: subprocess 타임아웃이 없는 명령어 실행

**우선순위**: low  
**작성 페르소나**: security-auditor  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/core/phases.py의 여러 subprocess.run() 호출(48, 62번 줄 등)에 timeout 설정이 있지만, src/evonest/tools/improve.py:33의 subprocess.Popen() 호출에는 타임아웃이 없습니다. 백그라운드 프로세스지만 무한 대기 상태에 빠질 수 있는 시나리오를 고려해야 합니다. 프로세스 관리 메커니즘(PID 추적, 최대 실행 시간 모니터링)을 추가하거나 문서화가 필요합니다.

## 관련 파일

- src/evonest/tools/improve.py
- src/evonest/tools/evolve.py
- src/evonest/tools/analyze.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*