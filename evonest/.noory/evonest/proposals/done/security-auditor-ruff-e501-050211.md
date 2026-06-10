# 제안: ruff 린팅 규칙 위반 (E501 라인 길이 초과)

**우선순위**: low  
**작성 페르소나**: security-auditor  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/cli.py, src/evonest/core/claude_runner.py, src/evonest/core/config.py에서 100자 제한을 초과하는 라인들이 있습니다. 코드 품질 표준 준수를 위해 라인 분할이 필요합니다. 직접적인 보안 이슈는 아니지만, 코드 리뷰 가독성 향상은 보안 결함 발견에 도움이 됩니다.

## 관련 파일

- src/evonest/cli.py
- src/evonest/core/claude_runner.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*