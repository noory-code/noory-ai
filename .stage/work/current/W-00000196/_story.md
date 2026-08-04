---
id: W-00000196
title: 닫힌 상태 기록이 자기가 닫혔다고 말하게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/, stage/templates/, stage/hooks/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000196 닫힌 상태 기록이 자기가 닫혔다고 말하게 한다

## Purpose

닫힌 관측 아홉과 답이 나온 질문 하나가 파일만 보면 아직 살아 있는 것처럼 읽힌다.

## Actions

- W-00000197 — 답이 나온 질문을 세션 화면이 열린 것으로 안 세게 한다 (구현 · codex)

## User value

기록을 열면 그것이 아직 살아 있는지 그 자리에서 보인다. 지금은 목록을 따로 봐야 알 수 있고,
질문은 목록마저 틀리게 말한다.

## Scope

### Included

- 닫힌 관측 아홉의 첫머리에 무엇이 그것을 닫았는지 적는다.
- 답이 나온 질문 하나의 첫머리에 그렇게 적는다.
- 상태 기록에 닫힘을 어떻게 적는지 규칙으로 남긴다.

### Excluded

- 기록을 지우거나 옮기는 일. Q-00000001 은 보관된 기록 여럿이 가리킨다(확인함) — 지우면
  그 참조가 깨진다.
- 새 상태값(머리말 칸)을 만드는 일. 대체된 결정과 같은 방식으로 본문 첫머리에 적는다.
- 세션 화면이 그 표시를 읽게 하는 일. 코드라 W-00000197 이 맡는다.

## Risks

- **"닫혔다"고 적는 것이 짐작이면 기록이 거짓이 된다.** 아홉 다 무엇이 닫았는지를 현재 상태
  문서에서 확인하고 그 근거를 함께 적는다.

## Success criteria

- 닫힌 관측 아홉을 열면 첫머리에서 무엇이 그것을 닫았는지 보인다.
- Q-00000001 을 열면 첫머리에서 답이 나왔다는 것과 그 답이 어디 있는지 보인다.
- 상태 기록에 닫힘을 적는 규칙이 그 서랍의 규칙 문서에 있다.
- 감사 오류 0.

## Next action

W-00000197 이 화면 쪽을 맡는다. 기록 쪽은 이 카드가 끝냈다.

## Related truth

- **DE-00000030 · W-00000188** — 대체된 결정이 자기 첫머리에서 대체됐다고 말한다. 상태 기록도
  같은 이유로 같은 모양을 쓴다: 안 지우니까 남는 이상 지금 살아 있는지가 읽혀야 한다.
- **`stage_context.py`** — 질문 디렉터리에 있는 것은 다 열린 것으로 세고, 답이 나온 질문은
  거기서 나간다고 코드가 적고 있다. Q-00000001 은 2026-07-26 에 답이 나왔는데 아직 있다.


## Progress


## Verification


## Retrospective


## Promotion decision
