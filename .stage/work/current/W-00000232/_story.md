---
id: W-00000232
title: 팀원 실행 절차가 실제로 되는 방법을 적게 한다
kind: documentation
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
scope: .stage/operations/claude-venue.md
promotes:
decision_refs:
---

# W-00000232 팀원 실행 절차가 실제로 되는 방법을 적게 한다

## Purpose

절차가 시키는 대로 도구의 워크트리 격리 옵션으로 팀원을 띄우면 tmux 창이 안 생겨 사람이 옆에서 볼 수 없는데 절차는 그것을 모르고 그 방법을 시키므로, 실측으로 확인된 방법을 절차가 적게 한다

## Actions

없음 — 절차 문서의 한 걸음을 고치고 왜 그런지를 붙이는 한 덩어리다.

## User value

절차를 따라 한 사람이 사람이 볼 수 있는 팀원을 얻는다. 지금 절차대로 하면 팀원이 배경에서
조용히 돌고, 끝나야 결과를 본다 — DE-00000062 가 정한 "사람이 옆에서 보고 팀원이 중간에
묻는다"의 절반이 실현되지 않는다.

## Scope

### Included

- 절차의 "팀원을 워크트리 격리로 띄우고" 걸음을 실측된 방법으로 고친다:
  - 에이전트 도구의 **워크트리 격리 옵션을 주지 않는다.**
  - 대신 지시문에서 팀원이 **스스로 워크트리를 만들고 거기서 일하게** 한다.
- 격리 옵션을 쓰면 무엇을 잃는지 한 문장으로 붙인다 — tmux 창이 안 생겨 사람이 실시간으로
  보거나 끼어들 수 없다.

### Excluded

- DE-00000062 자체는 안 고친다. 그 결정의 본체(팀원 실행, 계약 상속, 중간 질문 허용, 무인은
  codex 전용)는 그대로 유효하고, 틀린 것은 격리를 어떻게 얻느냐는 방법뿐이다. 방법은 이
  절차 문서가 소유한다. 결정문의 괄호 한 구절을 손댈지는 감독이 따로 판단한다.
- 팀원이 감독에게 되말하는 통로는 안 적는다. 아직 실측이 없다(아래 Risks).

## Risks

- **안 재 본 것 하나** — 어제와 오늘 팀원의 보고가 감독에게 글로 돌아오지 않았다. 두 번 다
  "일 없음" 알림만 왔고 감독이 파일을 직접 봐서 확인했다. 절차에 "팀원이 보고한다"를 단정해
  적으면 안 된다. 이 카드는 그 자리를 안 건드린다.

## Success criteria

- 절차대로 따라 하면 팀원이 tmux 창에 뜨고 자기 워크트리에서 일한다
- 도구의 격리 옵션을 쓰면 무엇을 잃는지가 절차에 적혀 있다

## Next action

`.stage/operations/claude-venue.md` 의 감독 모드 절차에서 팀원을 띄우는 걸음을 고친다.

## Related truth

- DE-00000062 — 감독 모드 claude venue 는 세션 팀원이 실행한다. 이 카드는 그 결정의 방법
  한 줄을 실측에 맞춘다.
- 2026-08-07 실측: 격리 옵션을 준 실행은 tmux 창을 안 잡았고 배경 실행으로 갔다. 옵션 없이
  띄운 탐침은 창을 잡았고(`--agent-name pane-probe --team-name session-...`), 그 창 안에서
  `git worktree add` 로 자기 워크트리를 만들어 파일을 쓰는 것까지 됐다.


## Progress


## Verification


## Retrospective


## Promotion decision
