# 제안: Quick Start에 전제조건 명시 누락 — Git 레포, Claude Code, Python 버전 요구사항 불명확

**우선순위**: medium  
**작성 페르소나**: new-user  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README.md 54-71줄의 Quick Start 섹션에서 바로 'evonest_init()'부터 시작하지만, 사용자가 1) Git 레포지토리가 필요한지, 2) Claude Code가 이미 설치되어 있어야 하는지, 3) Python 3.11+가 필요한지 전혀 안내하지 않는다. pyproject.toml에는 'requires-python = ">=3.11"'이 명시되어 있지만 README에는 없다. 초보자는 왜 명령이 실패하는지 이해하지 못할 것이다.

## 관련 파일

- README.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*