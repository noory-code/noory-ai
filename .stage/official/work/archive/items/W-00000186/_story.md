---
id: W-00000186
title: 실행자마다 체크아웃을 따로 둘지 정한다
kind: design
venue: claude
milestone: M-00000001
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000186
promotion: promoted
review: not_required
scope: .stage/, stage/docs/
promotes: .stage/official/decisions/records/DE-00000055.md, .stage/official/decisions/index.md
decision_refs: DE-00000055
---

# W-00000186 실행자마다 체크아웃을 따로 둘지 정한다

## Purpose

사람이 만진 변경과 실행자가 만든 변경을 지금 구조로는 가를 수 없다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

드라이버를 걸어 두고 그 옆에서 일할 수 있게 되거나, 아니면 왜 못 하는지가 결정으로 남는다.
지금은 "만지지 마세요"가 아무 데도 안 적힌 채 사람이 알아서 참고 있다.

## Scope

### Included

- 실행자마다 체크아웃을 따로 둘 것인가를 정하고 결정 기록으로 남긴다.
- 안 두기로 하면 O-00000013 을 그 근거로 닫는다. 두기로 하면 무엇을 만들지 적는다.

### Excluded

- 만드는 일 자체. 이 카드는 정하기만 한다.
- 작성 주체를 기록하는 채널을 새로 만드는 일. W-00000185 가 그런 게 지금 없다는 것까지만 쟀다.

## Risks

- **값이 크다.** 체크아웃을 따로 두면 드라이버가 어디서 도는지, 커밋을 누가 어디로 하는지가
  다 바뀐다. 무인 실행은 이미 격리된 가지에서 도는데 감독 실행은 안 그렇다 — 그 차이부터 본다.
- **안 두기로 하면 O-00000013 이 약속으로 남는다.** 장치가 아니라 사람이 안 만지기로 하는 것이
  되고, 그건 O-00000021 과 같은 모양이다.

## Success criteria

- 정한 방향과 그 이유가 결정 기록에 있다. 무엇을 재고 무엇을 버렸는지가 함께 있다.
- 안 두기로 하면 O-00000013 이 그 근거로 닫힌다. 두기로 하면 구현 카드가 잡혀 있다.
- 사람이 겪는 결과: 드라이버가 도는 동안 무엇을 해도 되는지 알 수 있다.

## Next action

없다. DE-00000055 가 정했다.

## Progress

### 실측 — 2026-08-03

**무인 실행의 "격리"는 가지만 가른다. 작업 디렉터리는 같다.** `--unattended` 는 새 가지를 만들어
거기에 커밋할 뿐이고, 파일이 놓이는 자리는 사람이 쓰는 그 자리다(`drive.py:2040`).

그리고 **실행자 시도가 실패하면 커밋 안 된 변경을 전부 되돌리고 지운다** —
`git checkout -- .` 과 `git clean -fdq`(`drive.py:1934`, 호출은 `2354`·`2357`·`2395`).
셋 다 무인 경로 안에만 있다. 감독 실행에는 이 동작이 없다.

| | 사람이 도중에 파일을 만지면 |
|---|---|
| 감독 실행 | 실행자 몫으로 **섞인다** (O-00000013) |
| 무인 실행 | **지워진다** |

**O-00000013 의 피해 문장이 무인 실행에 대해서는 약하게 적혀 있었다.** 섞이는 것이 아니라
없어진다.

무인 실행은 시작할 때 작업 디렉터리가 깨끗할 것을 요구한다(`2031`). 그래서 "시작할 때는
깨끗했는데 도중에 사람이 만졌다"가 정확히 그 상황이다.

## Related truth

- **W-00000185(반려)** — 사람이 만진 변경과 실행자가 만든 변경을 지금 구조로는 못 가른다는
  것을 재서 카드에 남겼다. 스냅샷에 작성자가 없고, 실행자의 자기 신고를 기준으로 삼으면
  신고 안 된 변경을 놓친다. 가능해지려면 격리된 체크아웃이거나 작성 주체를 기록하는 채널이
  필요하고, 뒤엣것은 지금 계약에도 표준 라이브러리에도 없다.
- **O-00000013** — 사람이 드라이버를 걸어 두고 다른 일을 하는 것이 이 프로젝트의 기본 사용
  방식이다. 이 카드가 그것을 받는다.


## Progress


## Verification


### Executed at close — 2026-08-03

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
