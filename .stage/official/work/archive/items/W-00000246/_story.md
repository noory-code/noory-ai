---
id: W-00000246
title: 세션 시작이 프로젝트 규칙을 싣게 한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000246
promotion: promoted
review: not_required
scope: stage/hooks/, stage/hooks/tests/, .stage/operations/, .stage/decisions/, stage/CHANGELOG.md
promotes: .stage/official/decisions/records/DE-00000069.md
decision_refs: DE-00000069
---

# W-00000246 세션 시작이 프로젝트 규칙을 싣게 한다

## Purpose

프로젝트가 스스로 세운 규칙을 세션이 못 봐서 적어 두는 일이 값을 잃으므로, 세션이 그 규칙에 닿게 한다

## Actions

없음 — 결정 하나다. 만드는 것은 그 뒤 카드가 잇는다.

## User value

규칙을 적어 두면 지켜진다. 지금은 적어 둬도 다음 사람이 그런 게 있다는 것조차 모른다.

## Scope

### Included

**시작한 뒤 잰 것.** 세션 시작 훅을 직접 돌려 확인했다.

| 잰 것 | 값 |
|---|---|
| 세션 시작 전체 길이 | 6,125자 |
| `.stage/operations/` 파일 | 넷 — `claude-venue.md`, `discovery.md`, `session-hooks.md`, `verification.md` |
| **그중 이름이라도 세션에 들어온 것** | **0개.** "operations" 라는 낱말이 두 번 나오는데 둘 다 구역 이름을 나열하는 자리다 |
| 본문을 다 실으면 | 17,492자 — 지금 페이로드의 **2.9배** |
| 호스트 지시(`CLAUDE.md` 등) | 파일 이름 목록과 "읽어라" 한 줄로 실린다. `.stage/operations/` 만 그 자리에서 빠져 있다 |

**두 사례의 원인이 다르다. 이것이 이 카드의 핵심이다.**

| 사례 | 무슨 일이 있었나 | 이름을 실어 주면 고쳐지나 |
|---|---|---|
| 2026-08-07 (O-00000042 원문) | `claude-venue.md` 가 있다는 것을 세션이 아예 몰랐다. 팀원 실행을 한 번도 고려 안 했다 | **고쳐진다** |
| 2026-08-09 | 감독이 세션 초반에 `claude-venue.md` 를 다 읽었다. 그 파일이 14:59 에 바뀌었고(W-00000252 가 팀원 내리는 걸음을 더했다), 감독은 낡은 기억으로 움직였다 | **안 고쳐진다** — 이미 읽은 파일이다 |

O-00000042 가 적어 둔 고칠 길 셋은 첫 사례만 겨눈다. 둘째는 **세션 도중에 규칙이 바뀌었는데
아무도 안 알려 주는 것**이라 다른 문제다.

- **첫 사례를 고친다.** 호스트 지시를 싣는 그 자리에 `.stage/operations/` 파일 목록을 더한다.
  이름만 싣고 본문은 안 싣는다.
- **둘째 사례를 어떻게 할지 정한다.** 고칠지, 안 고칠지, 고친다면 어디서 고칠지. 세션 시작은
  이 자리를 못 잡는다 — 시작한 뒤에 바뀌기 때문이다.

### Excluded

- 규칙 본문을 세션에 싣지 않는다. 지금 넷이 17,492자이고 파일이 늘면 더 는다.
- 어느 규칙이 어느 카드에 걸리는지 파일이 스스로 말하게 하는 것은 안 한다. 그 방법이 지금
  없고, 만들면 이 카드보다 크다.
- 플러그인이 소유한 `stage/operations/` 는 안 건드린다. 이 카드는 프로젝트가 자기 규칙에
  닿는 문제다.

## Risks

- **이름만 실으면 첫 사례만 고쳐진다.** 그것으로 이 카드를 닫으면 오늘 겪은 두 번째 모양이
  그대로 남는다. 결정이 둘 다 답해야 한다.
- 세션 시작이 무거워진다. 이름 넷은 200자 안쪽이라 지금은 문제가 아닌데, 파일이 스무 개가
  되면 다시 본다.
- **읽으라고 실어도 안 읽을 수 있다.** 호스트 지시는 이미 그렇게 실리는데 그것을 매번 여는지
  안 쟀다.

## Success criteria

- 새 세션에 `.stage/operations/` 의 파일 이름이 다 들어오고, 그중 하나를 보고 그대로 따르는
  것이 한 번 관측된다
- 세션 도중에 규칙이 바뀌었을 때 어떻게 할지가 결정에 적혀 있다 — 고치기로 했으면 그 자리가,
  안 고치기로 했으면 그 근거가
- 규칙 파일이 늘 때 세션 시작이 얼마나 무거워지는지가 잰 값으로 남는다

## Next action

결정을 쓴다. 실측은 위 표에 있다. 둘째 사례를 어디서 잡을지가 안 정해진 부분이다.

## Related truth

## Progress

## Verification

### Executed at close — 2026-08-10

```
$ python3 stage/scripts/audit_stage.py
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

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 373 tests in 1.532s

OK
```

## Retrospective

## Promotion decision
