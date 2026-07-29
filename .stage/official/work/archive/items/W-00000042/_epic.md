---
id: W-00000042
title: 자율 실행 드라이버 — 계약 설계
kind: design
venue: claude
source:
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000046
promotion: approved
review: not_required
scope: .stage/decisions/pending/
promotes:
decision_refs: DE-00000013, DE-00000014, DE-00000015, DE-00000016, DE-00000017
---

# W-00000042 자율 실행 드라이버 — 계약 설계

## Purpose

Stage에 자율 실행 루프(드라이버)를 도입하기 위한 계약(드라이버 경계·기계 판정 종료·상위 집계·독립 판정·에스컬레이션/폭주 상한)을 결정 기록으로 확정한다. 구현은 자식 항목으로 분리한다.

## Scope


## Success criteria

- 자율 실행 계약의 다섯 결정(드라이버 경계·말단 종료·상위 집계·독립 판정·에스컬레이션/폭주)이 결정 기록으로 확정(decided)된다.
- 구현은 이 결정들을 참조하는 자식 항목으로 분리된다(본 항목 범위 밖).

## Related truth

- 현행 근거: 게이트 훅은 "deny/allow만, 드라이버 아님" 명시 채택(`stage/hooks/README.md`); `close_work`가 `--check` 셸 명령 실행(exit 0); opt-in `review` 훅이 유일한 독립 검증; `parent`는 재귀·강제(`hierarchy_blocker`), 상위 집계는 역제약만 존재; 자율 실행 개념은 현재 전무.

## Progress

- DE-00000013~17 확정(status: decided). 드라이버 경계 / 말단 종료 스키마 / 실행 트리+집계 / 독립 판정 필수 / 에스컬레이션·폭주 상한.
- 구현 자식 5건 planned 등록(venue=codex, parent=W-00000042): W-00000043 acceptance(DE-14) · W-00000044 독립 판정(DE-16) · W-00000045 집계 롤업(DE-15) · W-00000046 에스컬레이션·예산(DE-17) · W-00000047 드라이버(DE-13).
- umbrella 유지: 구현이 계약을 검증한 뒤 결정 official 승격 + 본 항목 아카이브. 다음: Codex 창 핸드오프.

## Verification


### Executed at close — 2026-07-23

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 321 tests in 0.927s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
WARNING KIND001 [.stage/official/work/archive/items/W-00000040.md]: Work kind `bug` has no `passed` criterion in operations/verification.md.
Summary: errors=0, warnings=1
```

## Retrospective


## Promotion decision

