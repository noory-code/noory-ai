---
id: W-00000416
title: 닫기 리뷰어가 저장소 밖을 읽거나 고친 것을 되돌려 숨기지 못한다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/claude_review_companion.py,stage/scripts/run_review.py,stage/scripts/tests,stage/skills/stage-retrospective,stage/operations/review.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000416 닫기 리뷰어가 저장소 밖을 읽거나 고친 것을 되돌려 숨기지 못한다

## Purpose

리뷰어에게 셸을 열어 준 뒤에도, 리뷰어가 프로젝트 파일을 고쳤다가 되돌리거나 저장소 밖의 기록을 읽어 판정에 쓰는 일이 닫기에서 드러난다 (DE-00000101, W-00000414)

## Actions


## User value


## Scope

### Included


### Excluded

- 리뷰어를 다른 venue(codex)나 검증 세션에 견주는 일.
- 리뷰어의 셸 권한을 다시 좁히는 일. DE-00000101 이 넓히기로 했다. 좁혀야만 기준을 채울 수 있으면 그렇다고 보고한다.


## Risks


## Success criteria

- 리뷰어가 추적되는 파일을 고친 뒤 git checkout 이나 git restore 로 되돌려도 닫기가 그 리뷰를 실패시킨다
- 리뷰어가 git 이 무시하는 파일에 쓴 것도 닫기의 앞뒤 비교에 걸린다
- 리뷰어가 세션 기록 폴더(~/.claude)와 GitHub API 를 읽지 못하거나, 읽으면 닫기가 그것을 알린다
- 막은 것과 여전히 막지 못하는 것이 리뷰 절차 문서에 적혀 있다

## Next action


## Related truth

- W-00000413 의 실제 리뷰어 탐침: 리뷰어가 시험이 쓴 파일을 보고 스스로 `git checkout -- tracked.txt` 로 되돌리고 `__pycache__` 를 지웠다. 트리를 되돌린 리뷰어는 앞뒤 비교를 통과한다.
- W-00000414 의 재기(`.stage/research/review-judgment/measurement.md`, `runs/`): 리뷰어가 GitHub API 로 PR 의 지금 상태를 한 번, 이 컨테이너의 `~/.claude/projects/` 세션 기록을 두 번 읽었다. 무시되는 파일과 저장소 밖 파일에 쓰는 시험 코드는 걸리지 않는다(W-00000309 의 기준 3).
- W-00000408 이 넣은 거부 규칙은 접두어 규칙이라 `sh -c` 나 스크립트 안의 명령은 보지 못한다.
- 사용자가 2026-11-23 에 실기기에서 해야 할 일만 두고 나머지를 진행하라고 했다("실기기에서 해야할 일은 두고 나머지는 합시다"). 목적과 성공 기준은 지휘 세션이 옮겨 적었다.


## Sessions


## Progress


## Verification
