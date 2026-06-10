# 제안: shell injection 취약점 수정 — phases.py subprocess shell=True 제거

**우선순위**: high
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`src/evonest/core/phases.py` 608, 633번 줄에서 `subprocess.run(cmd, shell=True)`를 사용자 설정값(`config.verify.build`, `config.verify.test`)과 함께 호출하여, 악의적인 설정으로 shell injection 공격이 가능하다.

## 구현 단계

1. `src/evonest/core/phases.py` 파일 열기
2. 파일 상단에 `import shlex` 추가
3. verify 함수 내 `subprocess.run()` 호출 찾기 (608, 633번 줄 부근)
4. `shell=True`를 `shell=False`로 변경
5. 명령 문자열을 `shlex.split(cmd)`로 파싱하여 인수 리스트로 변환
6. `tests/test_phases.py`에서 변경된 호출 방식에 맞게 기존 테스트 업데이트
7. 새 테스트 추가: `verify.build = "echo ok && rm -rf /"`가 `rm -rf /`를 실행하지 않는지 검증

## 대상 파일

- src/evonest/core/phases.py
- tests/test_phases.py

## 검증

- `uv run pytest tests/test_phases.py -v && uv run mypy src/evonest/`

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
