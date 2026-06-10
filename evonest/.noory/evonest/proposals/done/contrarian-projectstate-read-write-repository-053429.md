# 제안: ProjectState의 read/write 메서드를 Repository 패턴으로 분리

**우선순위**: medium  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ProjectState가 파일 I/O, JSON 직렬화, 비즈니스 로직을 모두 담당함. IdentityRepository, ProgressRepository, BacklogRepository로 분리하면 각 저장소의 책임이 명확해지고, 인메모리 구현으로 교체 가능해짐. 현재는 테스트 시 실제 파일 시스템에 의존하며, 파일 포맷 변경 시 여러 메서드를 동시에 수정해야 함.

## 관련 파일

- src/evonest/core/state.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*