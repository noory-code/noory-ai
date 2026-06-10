# 제안: docs/configuration.md의 observe_turns_min 기본값 불일치 수정

**우선순위**: high  
**작성 페르소나**: spec-reviewer  
**사이클**: 0  
**상태**: 검토 대기

## 설명

configuration.md 문서에는 observe_turns_min_quick의 기본값이 50이고 observe_turns_min_deep이 100이라고 명시되어 있지만, 실제 코드(src/evonest/core/config.py:97-98)에서는 각각 15와 30으로 설정되어 있습니다. 문서가 약속한 것과 실제 동작이 다릅니다. 권장사항: 문서를 코드에 맞춰 수정 (15, 30으로 업데이트)하거나, 코드를 문서에 맞춰 수정 (50, 100으로 업데이트). Project Identity의 Quality Standards에 따라 정확성을 우선하므로, 먼저 어느 쪽이 올바른 값인지 확인한 후 일치시켜야 합니다.

## 관련 파일

- docs/configuration.md
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*