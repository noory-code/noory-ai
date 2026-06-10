# 제안: 명령어 출력 형식 통일 및 machine-readable 옵션 추가

**우선순위**: medium  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 CLI는 print 기반 출력 사용 (cli.py에서 확인). 하지만 MCP 도구는 구조화된 JSON/dict 반환. 사용자가 CLI와 MCP 도구 출력을 파싱하려면 서로 다른 방식 필요. --json 플래그로 CLI도 구조화된 출력 제공하면 CI/CD 파이프라인 통합 용이. 또한 성공/실패 상태를 일관되게 전달하는 표준 형식 필요.

## 관련 파일

- src/evonest/cli.py
- src/evonest/_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*