# 제안: 문서-코드 불일치 수정 — configuration.md 기본값이 config.py와 다름

**우선순위**: high
**작성 페르소나**: merged
**사이클**: 0
**상태**: 실행 대기

## 문제

`docs/configuration.md`에 `observe_turns_min_quick=50`, `observe_turns_min_deep=100`으로 기재되어 있으나, `src/evonest/core/config.py`(97-98번 줄) 코드에서는 15와 30으로 정의되어 있다.

## 구현 단계

1. `docs/configuration.md` 파일 열기
2. `observe_turns_min_quick` 및 `observe_turns_min_deep` 값 찾기
3. 코드와 일치하도록 업데이트: quick=15, deep=30
4. config.py 기본값과 다른 다른 값도 확인하여 업데이트
5. `src/evonest/core/config.py`에 주석 추가: `# Defaults must match docs/configuration.md`

## 대상 파일

- docs/configuration.md
- src/evonest/core/config.py

## 검증

- 수동 검토 — docs 값과 config.py 기본값 diff 비교

---

*이 제안은 분석 단계에서 생성되었습니다. 아직 구현되지 않았습니다.*
*improve 명령으로 실행하거나, 팀에서 검토 후 처리하세요.*
