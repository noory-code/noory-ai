---
id: W-00000129
title: 병렬 정리가 리뷰어와 커밋 안 된 일까지 본다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000129 병렬 정리가 리뷰어와 커밋 안 된 일까지 본다

## Purpose

W-00000128 이 정리를 안전하게 만들었지만 두 자리가 남았다. 첫째, 시간이 다 됐을 때 도는 것이 리뷰어일 수 있는데 코드는 카드 venue 로 reaper 를 고르고 역할을 executor 로 박는다. 리뷰어는 계약상 다른 venue 이므로 살아 있는 리뷰어가 트리에 계속 쓴다 — 출력은 executor or reviewer 라고 말하지만 실제로는 한쪽만 거둔다. 둘째, 미병합 커밋 보호가 커밋된 것만 덮어서, 사람이 보라고 안내받은 커밋 안 된 실행자 산출물을 정리가 말없이 지운다. 함께 걷을 것 둘: 트리는 사라지고 브랜치만 남은 경우를 거둘 길이 없고 거절 메시지가 남은 브랜치가 아니라 없는 경로를 가리킨다. SKILL.md 의 '그 실행이 만든 트리와 브랜치가 모두 제거된다'가 좁게 거짓이다(브랜치를 만든 뒤 체크아웃에서 실패하면 브랜치가 남는다). W-00000126 이 남긴 것 둘도 함께 걷는다: 겹침 게이트의 CHANGELOG 예외가 '덧붙이기만 한다'는 성질이 아니라 파일 이름으로 걸려서 release_plugin.py 가 그 파일의 절 제목을 다시 쓰는 경우를 못 본다. 그리고 게이트가 이름으로 부른 카드의 scope 만 읽는데 드라이버는 후손 잎을 돌리므로, 선언이 안 겹치는 부모 둘이 겹치는 후손을 가질 수 있다.

## Actions

- 시간이 다 됐을 때 **무엇이 돌고 있었는지**에 맞는 reaper 를 부른다. 실행자면 카드 venue,
  리뷰어면 리뷰어 venue 다 — 리뷰어는 계약상 카드와 다른 venue 이므로 지금은 살아남는다.
  못 부르면 왜 못 부르는지 출력에 남긴다.
- 정리할 때 트리에 커밋 안 된 변경이 있으면 **경고하고 멈춘다**. 사람이 밝히면 지운다.
  안내가 "그 트리를 보라"고 하는데 정리가 말없이 지우면 안내와 동작이 어긋난다.
- 트리는 사라지고 브랜치만 남은 경우를 거둘 수 있게 한다. 지금은 없는 경로를 가리키며
  거절해서, 진짜 남아 있는 브랜치를 아무도 못 지운다.
- `SKILL.md` 의 "그 실행이 만든 트리와 브랜치가 모두 제거된다"를 사실에 맞게 고친다.
  브랜치를 만든 뒤 체크아웃에서 실패하면 브랜치가 남는다.
- 겹침 게이트의 CHANGELOG 예외를 **성질로** 건다. 지금은 파일 이름으로 빼서,
  `release_plugin.py` 가 그 파일의 절 제목을 다시 쓰는 경우를 못 본다. 미출시 절에 덧붙이는
  것만 예외이고 그 파일을 다시 쓰는 일은 예외가 아니다.
- 겹침 게이트가 **후손 카드의 scope 까지** 본다. 드라이버는 에픽·스토리를 받아 후손 잎을
  돌리는데, 게이트는 이름으로 부른 카드의 frontmatter 만 읽는다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## Scope

`stage/scripts/drive_parallel.py` 와 그 테스트, `stage/skills/stage-drive/SKILL.md`,
`stage/CHANGELOG.md` 의 미출시 절.

**안 하는 것**: `drive.py` 수정, 따로 띄운 드라이버 둘이 서로를 아는 일(W-00000126 이 안
하기로 적은 자리).

## Success criteria

- 시간이 다 됐을 때 리뷰어가 돌고 있었으면 리뷰어 venue 의 reaper 를 부른다. 실행자면 실행자
  venue 다. 두 경우를 각각 고정하는 테스트가 있다.
- reaper 를 못 부르면 그 이유가 출력에 남는다. 조용히 넘어가지 않는다. 테스트가 고정한다.
- 트리에 커밋 안 된 변경이 있으면 정리가 경고하고 멈춘다. 사람이 밝히면 지운다. 두 경우를
  각각 고정하는 테스트가 있다.
- 트리가 없고 브랜치만 남은 상태에서 그 브랜치를 거둘 수 있다. 메시지가 남아 있는 브랜치를
  가리킨다. 테스트가 고정한다.
- 겹침 게이트가 미출시 절 덧붙이기는 예외로 두되, 같은 CHANGELOG 를 **다시 쓰는** 일은
  겹침으로 본다. 테스트가 고정한다.
- 겹침 게이트가 후손 카드의 scope 를 함께 본다. 부모끼리는 안 겹치는데 후손이 겹치는 경우를
  거절하는 테스트가 있다.
- `stage/skills/stage-drive/SKILL.md` 가 위 동작들과 남을 수 있는 브랜치를 사실대로 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- [DE-00000040](../../../official/decisions/records/DE-00000040.md) §2·§3 — 병렬의 계약
- [R-00000119](../../../work/retrospectives/R-00000119.md) — 정리를 안전하게 만든 경위
- [R-00000120](../../../work/retrospectives/R-00000120.md) — 겹침 게이트가 남긴 둘
- [O-00000007](../../../state/observations/O-00000007.md) — 되돌리기가 명령이 아니면 사람이
  손으로 상태를 맞춘다


## Progress


## Verification


## Retrospective


## Promotion decision
