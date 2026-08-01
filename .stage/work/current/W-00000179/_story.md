---
id: W-00000179
title: 대기 결정 목록이 서랍과 같은 말을 하게 한다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/, stage/hooks/, stage/operations/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000179 대기 결정 목록이 서랍과 같은 말을 하게 한다

## Purpose

통행증이 아직 살아 있는지 목록만 봐서는 알 수 없고 그 목록마저 서랍과 어긋나 있다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

서랍을 안 열어도 무엇이 아직 나를 구속하는지 목록에서 보인다. 그리고 목록이 다시 낡지 않는다.

## Scope

### Included

- 대기 결정 목록을 **서랍에서 만들어 낸다.** 손으로 쓰는 자리를 없앤다.
- 줄마다 어느 카드 것인지, 그 카드가 끝났는지를 싣는다. 카드 하나만 허가하고 끝나는 결정은
  그 카드가 끝나면 효력이 없으므로, 그 한 칸이 살았는지 죽었는지를 답한다.
- 감사가 그 목록과 서랍이 어긋나는지 본다.
- 이 저장소의 목록을 다시 만든다.

### Excluded

- **공식 결정 목록**(`official/decisions/index.md`, 46줄). 어긋난 적이 없다 — 반복이 보이기
  전에 같이 손대지 않는다.
- 결정에 새 상태값을 주는 일. "이 카드가 끝났는가"는 카드가 이미 소유한다. 통행증에 도장을 또
  찍으면 같은 사실이 두 곳에 생겨 언젠가 한쪽만 바뀐다.
- 결정을 옮기거나 만드는 명령이 목록을 쓰게 하는 일. 만들어 내는 쪽이면 그 자리가 필요 없다.

## Risks

- **만들어 낸 목록이 사람이 적어 둔 것을 지울 수 있다.** 지금 목록에 손으로 쓴 설명이 있는지
  먼저 보고, 있으면 그 자리를 남긴다. 같은 사고가 이 프로젝트에 있었다(O-00000012).
- **감사가 새 오류를 내면 다른 프로젝트가 걸릴 수 있다.** 목록이 없거나 모양이 다른 프로젝트가
  어떻게 되는지 보고 정한다.

## Success criteria

- 목록을 만들어 내는 명령이 있고, 손으로 쓰는 자리가 없다.
- 줄마다 어느 카드 것인지와 그 카드가 끝났는지가 있어, 서랍을 안 열어도 살았는지 알 수 있다.
- 목록과 서랍이 어긋나면 감사가 잡는다.
- 이 저장소 목록이 실제 서랍과 같다 — 지금은 낡은 다섯 줄이 있고 실제 여섯 줄이 빠져 있다.
- 사람이 겪는 결과: 대기 서랍을 열었을 때 아직 살아 있는 것이 무엇인지 한눈에 보인다.

## Next action

먼저 지금 목록에 손으로 쓴 내용이 있는지 본다. 그다음 목록을 만들어 내는 명령을 쓰고, 감사에
어긋남 검사를 붙이고, 이 저장소 목록을 다시 만든다.

## Related truth

- **DE-00000030** — 카드 하나만 허가하고 끝나는 결정은 대기에 남고, 나머지는 공식으로 간다.
  그 결정은 서랍을 갈랐고, 이 카드는 **서랍 안에서 살았는지 죽었는지**를 보이게 한다.


## Progress


## Verification


## Retrospective


## Promotion decision
