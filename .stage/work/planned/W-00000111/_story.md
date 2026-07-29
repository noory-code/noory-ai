---
id: W-00000111
title: 계층 보관의 인덱스 계약을 한쪽으로 정한다
kind: fix
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/skills/stage-archive/, stage/scripts/audit_stage.py, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
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


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
