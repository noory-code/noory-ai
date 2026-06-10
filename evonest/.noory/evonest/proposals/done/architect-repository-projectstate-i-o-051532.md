# 제안: Repository 패턴의 불완전한 적용 — ProjectState가 여전히 직접 I/O 수행

**우선순위**: high  
**작성 페르소나**: architect  
**사이클**: 0  
**상태**: 검토 대기

## 설명

repositories.py에 Repository 클래스들이 정의되어 있지만, ProjectState가 여전히 write_text, read_progress 같은 레거시 메서드를 직접 보유하고 있습니다. state.py의 80줄 이후를 확인하면 paths 프로퍼티와 레거시 메서드들이 혼재되어 있을 것으로 추정됩니다. 모든 파일 접근은 repository를 통해 이루어져야 하며, ProjectState는 순수하게 repository 컨테이너 역할만 해야 합니다.

## 관련 파일

- src/evonest/core/state.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*