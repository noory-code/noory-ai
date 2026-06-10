# 제안: ProjectState의 양방향 종속성 제거 — Repository 패턴 재설계

**우선순위**: high  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ProjectState가 12개의 Repository를 생성자에서 주입하고, 각 Repository는 EvonestPaths에 의존. 그런데 ProposalRepository만 ProgressRepository도 추가로 의존(state.proposals = ProposalRepository(paths, progress)). 이는 Repository 간 결합도를 높이고 단위 테스트를 복잡하게 만듦. 제안: ProposalRepository가 progress 데이터가 필요하면 paths를 통해 직접 읽거나, 상위 레이어에서 coordination 로직을 처리하도록 분리. Repository는 순수하게 파일 I/O만 담당하고 도메인 로직은 service layer로 이동.

## 관련 파일

- src/evonest/core/state.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*