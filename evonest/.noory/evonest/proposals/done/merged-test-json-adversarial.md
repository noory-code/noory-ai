# 제안: JSON 파싱 adversarial 테스트 추가 — LLM 출력 신뢰 문제

**우선순위**: high
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

meta_observe.py, scout.py, phases.py의 JSON 파싱이 LLM 출력을 무조건 신뢰하며, 비정상/과대/깊은 중첩 JSON에 대한 adversarial 테스트가 없다.

## 구현 단계

1. `tests/test_phases.py`에 테스트 추가:
   - 1MB JSON 문자열 (DoS 경계 검사)
   - 100단계 깊이의 중첩 객체
   - 개선 제목에 프롬프트 인젝션 문자열: `IGNORE PREVIOUS INSTRUCTIONS`
   - 잘린 JSON (닫히지 않은 중괄호)
   - 잘못된 유니코드 이스케이프
2. `tests/test_meta_observe.py`에 테스트 추가:
   - meta-observe JSON 파싱에 동일한 adversarial 패턴 적용
3. `tests/test_scout.py`에 테스트 추가:
   - scout JSON 파싱에 동일한 패턴 적용
4. 모든 테스트는 graceful failure 검증 (크래시 없음, 빈값/기본값 반환)

## 대상 파일

- tests/test_phases.py
- tests/test_meta_observe.py
- tests/test_scout.py

## 검증

- `uv run pytest tests/test_phases.py tests/test_meta_observe.py tests/test_scout.py -v`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
