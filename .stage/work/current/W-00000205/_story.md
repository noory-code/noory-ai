---
id: W-00000205
title: 로드맵 결정이 처음부터 제자리에 쓰이게 한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-roadmap/, stage/hooks/stage_paths.py, stage/hooks/stage_runtime.py, stage/scripts/refresh_decision_index.py, stage/docs/, stage/CHANGELOG.md, .stage/decisions/, .stage/official/decisions/
promotes:
decision_refs:
---

# W-00000205 로드맵 결정이 처음부터 제자리에 쓰이게 한다

## Purpose

로드맵 명령이 만든 결정이 대기 서랍에 태어나 사람이 기억해서 공식으로 옮겨야 하므로, 옮기는 걸음 자체가 없어지도록 규칙을 정하고 명령이 처음부터 제자리에 쓰게 한다

## Actions

시작할 때 둘로 나눈다. 규칙을 정하는 것과 명령을 고치는 것은 실행하는 쪽이 다르다.

- 규칙을 정한다 — 로드맵 사슬 결정이 어디에 태어나고 누가 쓰는가 (design, claude)
- 명령과 게이트를 고친다 (development, codex)

## User value

마일스톤을 만들거나 닫은 뒤에 "이 결정 옮겼던가"를 기억할 일이 없다. 지금은 기억해야 하고,
안 하면 대기 서랍에 쌓인다.

## Scope

### Included

- **규칙을 정한다.** 로드맵 사슬 결정은 마일스톤의 상태를 계산하는 유일한 근거다. 태어날 때부터
  구속하므로 "정한 뒤 사람이 옮긴다"는 걸음이 필요 없다. 명령이 처음부터 공식 자리에 쓴다.
- 그러면 DE-00000030 의 모양이 하나 바뀐다 — 결정이 `decided` 를 거쳐 `promoted` 로 가는 것이
  모든 결정의 길은 아니게 된다. 그 예외를 결정으로 남긴다.
- **명령이 공식 자리에 쓸 수 있어야 한다.** 지금은 통행증 게이트가 막는다. W-00000201 이
  보관함 셋을 연 것과 같은 모양으로, 로드맵 사슬 결정 자리도 연다.
- 대기 결정 표가 사슬 결정을 안 세게 한다. 살아 있는 대기 결정만 남아야 표가 뜻을 가진다.
- 이미 대기 서랍에 있는 DE-00000056·58 을 공식으로 옮긴다.

### Excluded

- 마일스톤에 상태 칸을 만들지 않는다. 계산하는 상태는 이 프로젝트에서 한 번도 안 낡았고
  (O-00000029), 칸을 만들면 사슬과 칸이 둘 다 상태를 말하게 된다.
- 다른 프로젝트의 사슬 결정은 안 옮긴다.

## Risks

- **게이트를 여는 일이다.** 공식 영역을 지키는 잠금을 또 넓히므로, 로드맵 명령이 쓰는 자리만
  열려야 하고 다른 자리로 새면 안 된다.
- DE-00000030 을 고치려면 이 카드가 끝난 뒤에야 통행증이 통한다. 그 편집을 마지막 걸음으로 잡는다.
- 사슬 결정이 대기 서랍을 안 거치면 "결정했지만 아직 안 정착"인 중간 상태가 사라진다. 로드맵
  전이는 그 중간이 없다는 것이 맞는지 규칙에서 답해야 한다.

## Success criteria

- 마일스톤을 만들고 닫는 동안 사람이 결정을 옮기는 걸음이 한 번도 없다.
- 대기 결정 표에 살아 있는 대기 결정만 뜬다.
- 넓힌 게이트가 로드맵 사슬 자리 밖의 공식 자리는 여전히 막는다.
- DE-00000056·58 이 공식 자리에 있고 마일스톤 상태 계산이 그대로 나온다.

## Next action

규칙부터 정한다 — 사슬 결정에 "결정했지만 아직 안 정착"인 중간이 필요한가. 필요 없다면
명령이 처음부터 공식에 쓰는 것이 맞다.

## Related truth

## Progress

## Verification

## Retrospective

## Promotion decision
