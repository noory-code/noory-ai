---
id: W-00000125
title: 카드마다 자기 작업 트리에서 드라이버가 돈다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/skills/stage-drive/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000125 카드마다 자기 작업 트리에서 드라이버가 돈다

## Purpose

DE-00000040 §2. 드라이버는 실행자 호출 전후로 저장소를 스냅샷 떠서 관측하므로(W-00000121), 둘이 같은 체크아웃에 있으면 서로의 변경을 자기 실행자 것으로 본다. git worktree 로 카드마다 트리와 브랜치를 주고 드라이버를 거기에 건다. 드라이버는 이미 --project-root 를 받으므로 가리키기만 하면 된다. 끝나면 어디를 병합하면 되는지 알려준다. 시도 기록은 .gitignore 라 트리마다 저절로 따로 논다.

## Actions

- 병렬 실행 명령을 만든다(`stage/scripts/` 아래, 파이썬). 카드 ID 를 여럿 받아 각각
  `git worktree` 와 브랜치를 만들고, 그 트리를 `--project-root` 로 삼아 드라이버를 건다.
- 트리와 브랜치 이름을 카드 ID 로 정한다. 사람이 나중에 보고 어느 카드의 것인지 알아야 한다.
- 끝나면 카드마다 결과와 **어느 브랜치를 병합하면 되는지** 알려준다. 병합은 사람이 한다 —
  드라이버가 커밋·닫기를 안 하는 것과 같은 이유다.
- 만들기에 실패하면 이미 만든 트리를 거둔다. 반쯤 만들어진 트리가 남으면 다음 실행이 그
  이름에 걸린다.
- `stage/skills/stage-drive/SKILL.md` 에 병렬로 도는 법과 그 한계를 적는다.
- `stage/CHANGELOG.md` 의 미출시 절에 적는다. **매니페스트 버전은 안 건드린다** —
  W-00000124 가 세운 새 규칙이다.

## User value

겹치지 않는 카드 여럿이 동시에 돈다. 지금은 하나가 끝나야 다음이 시작하므로, 카드마다
실행자가 6~10분 걸리는 것이 그대로 벽시계 시간이 된다.

## Scope

### Included


### Excluded


## Risks

- **worktree 안에서 훅이 다르게 동작할 수 있다.** Stage 훅은 작업 공간 뿌리에서 `.stage` 를
  찾는데, worktree 는 자기 `.stage` 사본을 갖는다. 실제로 worktree 에서 드라이버를 한 바퀴
  돌려 훅이 그 트리의 `.stage` 를 보는지 확인한다 — 코드를 읽어 추론하지 말고 돌려서 본다.
- 트리마다 카드 사본이 있으므로, 두 실행이 같은 카드를 집으면 둘 다 자기 사본을 고친다.
  겹침 거절은 W-00000126 이 하므로 이 카드는 **같은 카드를 두 번 걸면 어떻게 되는지**만
  밝혀 둔다.
- 병합에서 `.stage/work/active.md`·`review.md` 의 행이 부딪친다. 사람이 푸는 값이고 이
  카드가 없애지 않는다. 알려 주기만 한다.

## Success criteria

- 명령이 카드 여럿을 받아 각각 worktree·브랜치를 만들고 드라이버를 건다. 그 동작을 고정하는
  테스트가 있다.
- **worktree 에서 드라이버가 실제로 한 바퀴 돈 증거가 작업 로그에 있다** — 훅이 그 트리의
  `.stage` 를 보고, 실행자가 그 트리에서 일하고, 관측이 그 트리 기준으로 나온다. 코드 추론이
  아니라 실행 결과로 보인다.
- 만들기 중간에 실패하면 이미 만든 트리를 거둔다. 그 경우를 고정하는 테스트가 있다.
- 끝난 뒤 카드마다 병합할 브랜치 이름이 출력에 나온다.
- `stage/skills/stage-drive/SKILL.md` 가 병렬 실행법과 한계(같은 카드 중복, 인덱스 병합
  충돌)를 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 **매니페스트 버전은 그대로다**.

## Next action

끝나면 사람이 겹치지 않는 카드 둘을 실제로 동시에 걸어 본다. 그것이 이 에픽의 목적이
섰는지 보는 유일한 확인이다.

## Progress

## Verification

## Retrospective

## Promotion decision
