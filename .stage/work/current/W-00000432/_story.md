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
retrospective: completed
retrospective_ref: R-00000432
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

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6QxH1occgTRY9kC2uH — pm — 2026-11-26 — opened from the index: none

## Progress

- 2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 에픽 W-00000424 를 닫다가 본 고장이고 증거는 `## User value` 에 있다(DE-00000102).
- 2026-11-26 PM 세션 session_018VXR6QxH1occgTRY9kC2uH 가 만들기 전에 결정 넷을 올렸다. 에픽의 닫기 리뷰는 에픽 카드의 성공 기준만 판정하고 스토리의 성공 기준은 판정하지 않는다고 알렸다.
  - 결정 1(고치는 자리): A 도구, 리뷰가 pending 인 에픽을 시작하면 스토리도 pending 이 된다. 리뷰가 스토리 수 + 1 번 돈다 / B 문서, 스토리는 리뷰 없이 닫고 에픽을 닫을 때 한 번 본다. 사용자가 A 를 골랐다("권장으로 진행").
  - PO 세션이 사용자의 위임으로 정한 셋: 스토리는 리뷰 표시와 에픽의 환경, 그 환경의 venue 를 물려받고, 스토리가 다른 venue 를 적어 두었으면 시작을 거절한다. 에픽 바로 아래 스토리까지만 적용한다. `register_work.py --parent` 도 같은 표시를 준다.
- 이 카드는 도구를 고치므로 절차를 바꾸는 카드가 아니다. W-00000430 의 시험이 되지 않는다.
- 2026-11-26 PM 세션이 117558c2 를 보고했다. `start_work.py` 와 `register_work.py` 가 리뷰가 pending 인 에픽의 스토리에 리뷰 표시와 환경과 venue 를 준다. 새 시험 파일의 13개 가운데 하나는 실제로 에픽을 `--environment cloud --review` 로 시작하고 스토리에 `close_work.py --review-commit HEAD` 를 돌려 거절되지 않고 리뷰어가 실행되는 것을 본다고 했다. 범위 밖 변경은 없다고 했다.
- 2026-11-26 PO 세션이 squash 커밋 1629091f 에서 훅 시험, 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0

## Verification

2026-11-26 PO 세션이 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `1629091f` 의 것이다.
