# 제안: 첫 5분 경험 데모 영상 및 인터랙티브 튜토리얼 추가

**우선순위**: high  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README.md는 기능 나열 중심이지만, 신규 사용자가 'value proof'를 즉시 체감하기 어렵습니다. 'Why Evonest?' 섹션 이후에 2-3분 길이의 asciicast 또는 GIF 데모를 삽입하여 `/evonest:analyze` → proposals → `/evonest:improve` 흐름을 시각적으로 보여주면 전환율 상승이 예상됩니다. 또한 `/evonest:init` 실행 시 interactive wizard (프로젝트 유형 선택 → verify 명령 자동 제안 → identity.md 핵심 값 입력 가이드)를 제공하면 time-to-first-value를 30% 단축 가능합니다.

## 관련 파일

- README.md
- src/evonest/core/initializer.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*