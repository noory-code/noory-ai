# 제안: 에러 메시지에 실행 가능한 해결책 추가

**우선순위**: high  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 ProjectState.__init__에서 'Project not initialized' 에러는 사실만 알려줌. 사용자가 다음에 무엇을 해야 하는지 명확히 제시하지만, 다른 많은 FileNotFoundError, ValueError는 그렇지 않음. 일관성 있게 모든 에러 메시지에 '다음 단계' 또는 '해결 방법'을 포함하도록 개선 필요. 예: config.py의 'Unknown config key' 에러는 유효한 키 목록을 표시해야 함.

## 관련 파일

- src/evonest/core/state.py
- src/evonest/core/config.py
- src/evonest/core/improve.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*