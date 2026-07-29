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

W-00000128 이 정리를 안전하게 만들었지만 두 자리가 남았다. 첫째, 시간이 다 됐을 때 도는 것이 리뷰어일 수 있는데 코드는 카드 venue 로 reaper 를 고르고 역할을 executor 로 박는다. 리뷰어는 계약상 다른 venue 이므로 살아 있는 리뷰어가 트리에 계속 쓴다 — 출력은 executor or reviewer 라고 말하지만 실제로는 한쪽만 거둔다. 둘째, 미병합 커밋 보호가 커밋된 것만 덮어서, 사람이 보라고 안내받은 커밋 안 된 실행자 산출물을 정리가 말없이 지운다. 함께 걷을 것 둘: 트리는 사라지고 브랜치만 남은 경우를 거둘 길이 없고 거절 메시지가 남은 브랜치가 아니라 없는 경로를 가리킨다. SKILL.md 의 '그 실행이 만든 트리와 브랜치가 모두 제거된다'가 좁게 거짓이다(브랜치를 만든 뒤 체크아웃에서 실패하면 브랜치가 남는다).

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
