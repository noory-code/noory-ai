---
id: W-00000126
title: 도는 작업과 겹치는 카드는 시작을 거절한다
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
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/skills/stage-drive/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000126 도는 작업과 겹치는 카드는 시작을 거절한다

## Purpose

DE-00000040 §3. 카드가 선언한 scope 가 이미 도는 작업의 scope 와 겹치면 시작하지 않는다. 겹침 판단을 사람의 기억에 맡기면 언젠가 틀리고, 그때 나는 실패는 대조 불일치라는 엉뚱한 모양으로 온다. 카드가 이미 scope 를 선언하므로 새 개념을 만들지 않고 그것을 쓴다.

## Actions

- 병렬 실행이 시작하기 전에 카드들의 `scope` 를 비교해, 겹치면 **하나도 시작하지 않고**
  멈춘다. 반쯤 띄우고 나서 알리면 트리가 남는다.
- 무엇과 무엇이 어느 경로에서 겹치는지 출력이 말한다. 사람이 그 다음에 할 일(scope 를 좁힌다,
  다른 카드를 고른다, 순서대로 돌린다)을 고를 수 있어야 한다.
- **CHANGELOG 의 미출시 절은 겹침에서 뺀다.** DE-00000040 이 그 절을 고른 이유가 바로
  덧붙이기만 해서 병합이 되기 때문이다. 그것을 겹침으로 세면 모든 플러그인 카드가 서로
  겹친다.
- 사람이 판단해 넘길 수 있는 길을 둔다(`--allow-overlap` 같은 것). 겹침 판정은 도움이지
  판결이 아니다 — 두 카드가 같은 폴더를 선언했어도 실제로 다른 파일만 만질 수 있다.
- `stage/skills/stage-drive/SKILL.md` 에 겹침 판정 기준과 넘기는 법을 적는다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

겹치는 카드를 동시에 걸어 서로의 변경을 자기 것으로 오인하는 사고를 사람이 기억하지 않아도
막는다. 겹쳐서 나는 실패는 "주장과 관측이 다르다"라는 엉뚱한 모양으로 오므로 원인을 찾기가
어렵다.

## Scope

겹침 판정은 **병렬 실행 명령**(`stage/scripts/drive_parallel.py`)이 쥔다. 한 번의 실행이
카드 여럿을 알고 있으므로 비교할 수 있는 자리가 거기다.

**안 하는 것**: 따로따로 띄운 드라이버 둘이 서로를 아는 일. 그것은 실행 등록부가 필요해
축이 다르고, 지금은 사람이 명령 하나로 여럿을 거는 흐름뿐이다. 실제로 따로 띄워 부딪히는
것을 겪으면 그때 연다(AHA).

### Included


### Excluded


## Risks

- **판정이 너무 넓으면 병렬이 무의미해진다.** 지금 열린 카드 다섯이 전부
  `stage/scripts/tests/` 와 `stage/CHANGELOG.md` 를 선언하고 넷이 `stage/scripts/drive.py` 를
  선언한다. 순진하게 세면 모든 쌍이 거절된다. 미출시 절을 빼고, 넘기는 길을 두는 것이 그
  대응이다.
- 판정이 너무 좁으면 진짜 겹침을 놓친다. 같은 파일을 선언한 것은 언제나 겹침이다 — 그 자리는
  넓히지 않는다.

## Success criteria

- 같은 파일을 선언한 카드 둘을 같이 걸면 **트리를 하나도 안 만들고** 멈춘다. 어느 경로에서
  겹치는지 출력이 말한다. 테스트가 고정한다.
- 겹치지 않는 카드 둘은 그대로 돈다. 테스트가 고정한다.
- `stage/CHANGELOG.md` 만 공유하는 카드 둘은 겹침으로 안 본다. 테스트가 고정한다.
- 사람이 판정을 넘길 수 있고, 넘겼다는 사실이 출력에 남는다. 테스트가 고정한다.
- `stage/skills/stage-drive/SKILL.md` 가 판정 기준과 넘기는 법을 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

끝나면 사람이 겹치지 않는 카드 둘을 실제로 동시에 걸어 본다. 지금 백로그에서 그런 쌍은
드라이버를 만지는 카드(W-00000117·118·119·129)와 보관 인덱스를 만지는 W-00000111 이다 —
드라이버 카드끼리는 `drive.py` 에서 진짜로 겹치므로 순서대로 돌 수밖에 없다.

## Progress

## Verification

## Retrospective

## Promotion decision
