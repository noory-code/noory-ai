# 제안: claude_runner 모듈을 독립 서비스 계층으로 추상화

**우선순위**: medium  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

claude_runner.py가 subprocess 호출을 직접 수행하며 phases.py, orchestrator.py에서 직접 import됩니다. 향후 Claude API 호출 방식 변경 시 여러 곳을 수정해야 합니다. IClaudeExecutor 인터페이스를 정의하고 SubprocessClaudeExecutor 구현체로 분리하면, 테스트 시 mock executor 주입이 가능해지며 확장성이 향상됩니다.

## 관련 파일

- src/evonest/core/claude_runner.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*