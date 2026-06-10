# 제안: ruff E501 라인 길이 위반 3건 — Quality Standards 미준수

**우선순위**: medium  
**작성 페르소나**: new-user  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ruff check 실행 결과 src/evonest/cli.py:182, src/evonest/core/claude_runner.py:133, 144줄에서 100자 제한을 넘는 라인이 발견되었다. pyproject.toml에 'line-length = 100'이 명시되어 있고, Project Identity의 Quality Standards에서 'Linting passes: uv run ruff check src/ tests/'를 요구하지만 실제로는 위반 사항이 있다.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*