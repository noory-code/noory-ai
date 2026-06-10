# 제안: 악의적 JSON 입력 테스트 — 프롬프트 인젝션, 극한 크기, 구조적 공격 시나리오 추가

**우선순위**: high  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

meta_observe.py:parse_meta_json(), scout.py:parse_scout_json(), phases.py:save_observations_from_output() 등 JSON 파싱 경로는 LLM 출력을 신뢰합니다. 하지만 LLM이 의도치 않게 또는 프롬프트 인젝션 공격으로 악성 JSON을 생성할 수 있습니다. 테스트 추가: 1) 10MB+ JSON (DoS 시도), 2) 깊이 1000+ 중첩 객체 (stack overflow), 3) 필드에 프롬프트 인젝션 문자열 포함 ('<|endoftext|>', 'IGNORE PREVIOUS INSTRUCTIONS'), 4) invalid unicode escape, 5) truncated JSON (연결 끊김 시뮬레이션). 기존 test_parse_meta_json_invalid_json은 기본 에러만 확인하므로 adversarial 케이스가 부족합니다.

## 관련 파일

- tests/test_meta_observe.py
- tests/test_scout.py
- tests/test_phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*