# 제안: 프로젝트 경로 해석 로직의 멘탈 모델 단순화

**우선순위**: medium  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

CLI의 _resolve_project는 환경변수 → cwd 상향 탐색 순서로 동작. 하지만 commands/analyze.md는 '사용자가 evonest라고 말하면 monorepo의 evonest/ 디렉토리 사용' 같은 특수 규칙 포함. 이는 컨텍스트 의존적이며 예측 불가능. 사용자는 '명시적 경로 > 환경변수 > cwd 탐색' 규칙만 기억하면 되도록 단순화 필요. 특수 케이스는 Claude Code 플러그인 명령어 내부 로직으로 격리.

## 관련 파일

- src/evonest/cli.py
- commands/analyze.md
- commands/evolve.md
- commands/improve.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*