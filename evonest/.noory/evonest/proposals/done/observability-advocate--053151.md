# 제안: 조용한 실패 패턴 제거 — 에러 정보 손실 방지

**우선순위**: high  
**작성 페르소나**: observability-advocate  
**사이클**: 0  
**상태**: 검토 대기

## 설명

phases.py, orchestrator.py, improve.py, initializer.py, proposals.py에서 except 블록이 pass로 에러를 삼키고 있습니다. 프로덕션 환경에서 문제가 발생해도 추적할 방법이 없습니다. 각 except 블록에 최소한 logger.debug() 또는 logger.warning()을 추가하여 에러 발생 사실과 컨텍스트를 기록해야 합니다. 특히 phases.py:57-58, 81-82에서 git 명령어 실패를 완전히 무시하고 있습니다.

## 관련 파일

- src/evonest/core/phases.py
- src/evonest/core/orchestrator.py
- src/evonest/core/improve.py
- src/evonest/core/initializer.py
- src/evonest/tools/proposals.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*