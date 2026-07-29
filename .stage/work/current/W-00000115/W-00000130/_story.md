---
id: W-00000130
title: 리뷰 계약을 설명하는 문서가 실제 동작과 같아진다
kind: documentation
venue: claude
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
scope: stage/operations/review.md, stage/docs/, stage/skills/stage-retrospective/SKILL.md, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000130 리뷰 계약을 설명하는 문서가 실제 동작과 같아진다

## Purpose

W-00000117 이 리뷰 판정을 JSON 파일로 옮기면서 문서 넷이 옛 계약을 그대로 말한다. 산문의 BLOCK: 표식으로 차단한다는 서술이 stage/operations/review.md:38, stage/docs/SCHEMA_V4.md:145·148·301, stage/skills/stage-retrospective/SKILL.md:76 에 남아 있는데, 이제 BLOCK: 을 찍고 0 으로 끝나면서 승인 판정을 쓴 명령은 카드를 닫는다. 그리고 stage-drive/SKILL.md:250-251 의 '리뷰어 인프라 실패는 시도를 안 쓴다'가 판정 파일이 없을 때만 참이다 — 파일이 있고 깨졌으면 타임아웃 문구가 섞여도 시도를 쓴다. 문서가 틀린 계약을 말하면 다음 사람이 그것을 믿고 리뷰 명령을 만든다.

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
