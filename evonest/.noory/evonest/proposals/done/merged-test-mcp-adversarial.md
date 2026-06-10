# 제안: MCP 공개 도구 adversarial 입력 테스트 추가

**우선순위**: high
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

공개 MCP 도구(evonest_config, evonest_backlog, evonest_identity, save_observations)에 adversarial 입력 테스트가 없다.

## 구현 단계

1. `tests/test_config.py`에 parametrized 테스트 추가:
   - 빈 문자열 설정 키
   - 매우 긴 문자열 값 (10K 문자)
   - 프로젝트 경로에 path traversal: `../../../etc/passwd`
   - 설정값에 null 바이트
2. `tests/test_backlog.py`에 테스트 추가:
   - save_observations에 None 제목, 10K 문자 제목
   - `../../sensitive`를 포함하는 파일 목록
   - 주입 값이 포함된 category/priority
3. `tests/test_server.py` 또는 적절한 파일에 테스트 추가:
   - 손상된 identity.md로 identity 도구 테스트

## 대상 파일

- tests/test_config.py
- tests/test_backlog.py
- tests/test_server.py

## 검증

- `uv run pytest tests/test_config.py tests/test_backlog.py tests/test_server.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
