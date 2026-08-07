---
id: W-00000232
title: 팀원 실행 절차가 실제로 되는 방법을 적게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000231
promotion: not_applicable
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

- `.stage/operations/claude-venue.md` 감독 모드 절차의 팀원 실행 걸음을 고쳤다. 격리 옵션을
  주지 말라는 금지와 무엇을 잃는지, 팀원이 스스로 워크트리를 만들어 그 안에서만 일하는
  방법(브랜치 확인·명령마다 경로 넘기기 포함)이 절차에 들어갔다.
- 판정 반려 뒤 문구를 좁혔다. 3번 걸음이 Agent 도구의 `isolation` 인자를 이름으로 부르고
  "다른 값이 아니라 인자가 없어야 한다"로 확인 가능해졌고, 창 관측은 각 팔 한 번씩임을 날짜와
  함께 밝히면서 갈라 재지 않은 변수도 같이 적었다. 시험되지 않은 "끼어들 수 없다"는 뺐다.
- 같은 문서 2번 걸음의 이유를 실측에 맞췄다. "기준점이 세션 HEAD 를 따라오지 않아"는 새
  방법에서 거짓이다 — 워크트리를 `HEAD` 에서 만들므로 기준점은 세션 HEAD 다. 카드 등록을
  먼저 커밋하라는 지시는 남되, 이유가 "새로 만든 워크트리는 본 체크아웃의 커밋 안 된 변경을
  안 가져온다"로 바뀌었다.


## Verification

인수는 감독이 팀원 워크트리에서 직접 돌렸다(감사 오류 0, 경고 32 — 기준선과 같음). 판정은
codex 가 두 바퀴 봤다.

기준 1 — 2바퀴에 통과. 도구와 인자를 이름으로 부르고 "다른 값이 아니라 인자가 없어야
한다"로 적어, 호출문만 보고 지켰는지 확인된다.

기준 2 — 두 바퀴에 걸쳐 좁혀 통과. 판정 지적 넷 중 셋을 받았다(도구 표면 명시, 관측을 날짜와
횟수로 한정, 2번 걸음 이유 축소). 마지막 한 줄("창이 없으면 못 본다" → "tmux 창에서 볼 수
없다")도 받아 좁혔다.

**기각 하나, 이유를 남긴다.** 판정자는 셸 디렉터리 문장의 감독 쪽 절반을 "지시를 관측으로
바꾼 것"으로 봤다. 그렇지 않다 — 감독 셸이 명령 사이에 본 체크아웃으로 되돌아가는 것은
감독 자신이 오늘 반복해서 본 것이고(이 워크트리를 확인하던 두 번 포함) 관측으로 전달했다.
팀원 쪽 절반은 팀원이 이번 실행에서 직접 봤다. 판정자는 감독의 기록을 볼 수 없어 그 절반의
근거에 닿지 못했다. **판정자가 못 보는 증거가 있고, 그때는 기각 이유를 기록에 남긴다.**

### Executed at close — 2026-08-07

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective

R-00000231 참조.

## Promotion decision

not_applicable — 결정 기록을 걸지 않았고 승격 경로도 없다. DE-00000062 본문은 안 건드렸다.
