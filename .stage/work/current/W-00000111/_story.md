---
id: W-00000111
title: 계층 보관의 인덱스 계약을 한쪽으로 정한다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-archive/, stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000111 계층 보관의 인덱스 계약을 한쪽으로 정한다

## Purpose

계층 보관의 첫 실사용(에픽 W-00000104, 7 레코드)에서 보관 도구와 감사가 인덱스 계약을 서로
다르게 알고 있는 것이 드러났다. 도구는 최상위 행 하나만 적었고, 감사(ARCHIVE001)는 안쪽 스토리
여섯도 각자 행을 요구해 오류 6이 났다. 그 자리에서는 여섯 행을 손으로 채워 넘겼다.

계약을 한쪽으로 정하고 도구·감사·테스트를 그쪽으로 맞춘다. 갈림은 둘이다 — 인덱스가 이동
단위(최상위)만 적는가(계층은 폴더가 쥐므로 SSOT 에 맞음), 레코드 전부를 적는가(찾기가 한 번에
됨). 정하면 반대쪽을 고치고, 손 채움 행들도 계약에 맞게 정리한다.

**2026-07-29 재발.** 에픽 W-00000123(스토리 여섯)을 보관하며 같은 오류 여섯이 다시 났고 다시
손으로 채웠다. 계층 보관을 쓸 때마다 나므로 우연이 아니다. 손 채움 대상은 이제 두 에픽
(W-00000104, W-00000123)의 열두 행이다.


## Actions

- 계약을 한쪽으로 정한다. **이동 단위(최상위)만 적는 쪽을 권한다** — 계층의 진실은 폴더가
  쥔다는 DE-00000035 와 같은 방향이고, 안쪽 행은 폴더를 보면 나오는 것을 베껴 적는 일이다.
  다른 쪽을 고르면 그 근거를 카드에 적는다.
- 정한 쪽으로 보관 도구(`archive_work.py`)와 감사(`audit_stage.py` 의 ARCHIVE001)를 맞춘다.
  지금 둘이 서로 다르게 알고 있어서 계층을 보관할 때마다 오류가 난다.
- 손으로 채운 행들을 계약에 맞게 정리한다. 두 에픽(W-00000104, W-00000123)의 열두 행이다.
- 테스트로 고정한다 — 계층을 보관하면 감사가 오류 0 이다.

## User value

계층을 보관할 때마다 사람이 인덱스 행을 손으로 채우지 않는다. 오늘 두 번 그랬고, 그때마다
보관 직후 감사가 오류 여섯을 냈다.

## Scope

### Included

`stage/skills/stage-archive/` 의 보관 도구, `stage/scripts/audit_stage.py` 의 ARCHIVE001,
그 둘의 테스트, CHANGELOG 미출시 절.

### Excluded

이미 보관된 기록의 본문. 인덱스 행만 정리한다. 매니페스트 버전은 안 건드린다(W-00000124 가
정한 새 규칙).

## Risks

- 최상위만 적는 쪽으로 정하면 ID 로 보관 기록을 찾을 때 폴더를 뒤져야 한다. 감사와 도구가
  이미 폴더를 뒤지므로 사람만 불편해지는데, 인덱스가 최상위 링크를 주므로 한 단계다.

## Success criteria

- 계약이 한쪽으로 정해져 카드에 근거와 함께 적혀 있다.
- 보관 도구와 감사가 같은 계약을 쓴다. 계층(에픽 + 스토리 여럿)을 보관하고 감사하면 오류가
  0 이다. 테스트가 고정한다.
- 두 에픽의 손 채움 행이 계약에 맞게 정리돼 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

## Verification

## Retrospective

## Promotion decision
