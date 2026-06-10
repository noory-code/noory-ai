# 제안: ruff E501 위반 4건 수정 — 라인 길이 표준 준수

**우선순위**: low  
**작성 페르소나**: cto-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

4개 파일에서 라인 길이 100자 초과 (cli.py:182, claude_runner.py:133/144, config.py:53/58). 프로젝트 Quality Standards에서 ruff check 통과를 요구하지만 현재 위반 상태. 비즈니스 영향: 낮음 — 기능적 문제는 아니지만 자동화된 품질 게이트 통과 실패로 인한 개발 흐름 단절 가능. 제안: 해당 라인을 여러 줄로 분리하여 ruff format 표준 준수.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*