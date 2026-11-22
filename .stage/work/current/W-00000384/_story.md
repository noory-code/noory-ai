---
id: W-00000384
title: 릴리스와 변경 기록 줄 추가가 겹칠 때 union 병합 결과를 확인한다
kind: qa
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/tests/test_changelog_union.py,stage/scripts/release_plugin.py,stage/CHANGELOG.md
promotes:
decision_refs:
reserved_ids: DE-00000096
---

# W-00000384 릴리스와 변경 기록 줄 추가가 겹칠 때 union 병합 결과를 확인한다

## Purpose

한 브랜치가 릴리스해서 Unreleased 를 버전 제목으로 바꾸고 다른 브랜치가 Unreleased 에 줄을 더한 뒤 합칠 때 변경 기록이 어떻게 되는지 안다

## Actions


## User value

W-00000377 서브세션이 남긴 질문이다. 루트 `.gitattributes` 가 모든 `CHANGELOG.md` 에 `merge=union` 을
건다. 릴리스는 `## Unreleased` 제목을 버전으로 바꾸고 새 `## Unreleased` 를 연다. 다른 브랜치가 같은 때 Unreleased 에
줄을 더하면 union 이 그 줄을 어느 절에 두는지 확인하지 않았다. GitHub 머지 버튼은 union 을 따르지 않는다(PR #90, #91).


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 두 브랜치를 git 으로 합친 결과가 시험으로 고정되어 있고, 줄이 잘못된 절에 들어가면 그 처리 방법이 카드에 적혀 있다

## Next action

## Related truth

## Progress

## Verification
