---
id: W-00000432
title: 리뷰를 요구하며 시작한 에픽의 스토리가 리뷰 없이 닫힌다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/start_work.py,stage/skills/stage-work/register_work.py,stage/scripts/tests,stage/operations/cloud-execution.md,stage/skills/stage-orchestrate/SKILL.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000432 리뷰를 요구하며 시작한 에픽의 스토리가 리뷰 없이 닫힌다

## Purpose

리뷰를 요구하며 시작한 에픽의 스토리가 닫힐 때 그 리뷰를 받는다

## Actions


## User value

2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 에픽 W-00000424 를 처리하다 본 것에서 등록했다(DE-00000102: 문서대로 하면
막히고 재현 명령이 있다).

- `stage/operations/cloud-execution.md` 의 "Close a PM session's card" 는 에픽의 스토리마다 3단계와 4단계(리뷰와 함께 닫기)를 하라고
  한다.
- PO 세션은 `start_work.py W-00000424 --scope ... --environment cloud --review` 로 에픽을 시작했다. 에픽은 `review: pending` 이 됐고
  스토리 여섯은 `review: not_required` 였다.
- `close_work.py --project-root . W-00000425 --review-commit 2b4bca6 ...` 는 이렇게 거절했다:
  `W-00000425: --review-commit names what a review reads, and this card runs no review at close (it is not autonomous and its `review` is not `pending`); work item unchanged`.
  스토리 다섯이 모두 같았다.
- 그래서 스토리 다섯(W-00000425 ~ W-00000429)은 리뷰 없이 검사만으로 닫혔고, 그 변경은 독립된 판정 없이 병합됐다(PR #138).

고치는 자리가 도구인지(에픽을 리뷰와 함께 시작하면 스토리도 `review: pending` 이 된다) 문서인지(스토리는 리뷰 없이 닫고 에픽이
닫힐 때 한 번 본다)는 정하지 않았다. PM 세션이 선택지를 올린다.

## Scope

### Included


### Excluded


## Risks


## Success criteria

- start_work.py <에픽> --environment cloud --review 로 시작한 에픽의 스토리에 close_work.py <스토리> --review-commit <커밋> 을 돌리면 거절되지 않고 리뷰가 돈다

## Next action

## Related truth

## Sessions

## Progress

## Verification
