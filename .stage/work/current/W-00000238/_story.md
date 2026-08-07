---
id: W-00000238
title: 실행 결과를 들이는 명령을 만든다
kind: development
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_land_run.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/land_run.py, stage/scripts/tests/test_land_run.py, stage/CHANGELOG.md, .stage/operations/claude-venue.md, stage/skills/stage-drive/SKILL.md
promotes:
decision_refs:
---

# W-00000238 실행 결과를 들이는 명령을 만든다

## Purpose

실행이 끝난 결과를 본 가지로 들이는 일이 아직 전부 사람 손이고 그 손이 실행을 늘릴수록 같이 늘어나므로, DE-00000065 가 정한 조건대로 그 일을 하는 명령을 만든다

## Actions

없음 — 명령 하나와 그 시험, 그리고 그 명령을 가리키게 되는 절차 문구를 함께 고치는 한 덩어리다.

## User value

실행이 끝나면 명령 한 번으로 결과가 본 가지에 들어간다. 지금은 로그를 손으로 옮기고, 워크트리
에서 커밋하고, 병합하고, **병합을 커밋하려고 작업 항목을 새로 등록하고**, 워크트리와 가지를
치우는 다섯 걸음을 사람이 한다. 2026-08-06·07 실행 일곱 판에서 매번 그랬다.

## Scope

### Included

**DE-00000065 가 이 카드의 명세다.** 그 결정이 명령이 하는 일 넷과 거절 조건을 이미 못 박았다
— 새로 정할 것이 아니라 그대로 싣는다. 아래는 그 결정이 명령 카드 몫으로 남긴 것들이다.

- **명령을 만든다.** `stage/scripts/land_run.py`. 하는 일 넷: 워크트리 로그를 본 저장소로
  옮기기, 카드 선언 범위와 두 생애주기 기록만 담아 워크트리에서 커밋하기, `--no-ff
  --no-commit` 으로 병합해 충돌을 먼저 보고 남은 조건까지 통과한 뒤 병합 커밋 만들기,
  워크트리와 가지 치우기.
- **커밋 메시지의 형태를 정한다.** 결정은 "메시지가 그 기록의 자리"와 "두 커밋 다 담는다"를
  정했고, 카드 id 와 원본 가지를 **어떤 키로** 적는지는 이 카드가 정한다. 사람이
  `git log --grep` 으로 찾을 수 있는 형태로 한다.
- **팀원 가지 접두사를 선언한다.** 지금 저장소 어디에도 없다 — 명령이 가지를 알아보려면
  이름 규칙이 있어야 한다. `.stage/operations/claude-venue.md` 에 적는다.
- **치우기를 두 벌로 두지 않는다.** `stage/scripts/drive_parallel.py` 의 `cleanup_worktree`
  가 이미 같은 계약을 진다. 부르거나 옮기거나 하나를 고르고 복제하지 않는다.
- **손 병합을 시키던 산문을 이 명령으로 바꾼다** — `.stage/operations/claude-venue.md` 와
  `stage/skills/stage-drive/SKILL.md` 의 해당 걸음.
- **절차의 마지막 걸음에 팀원 내리기를 넣는다.** 카드를 닫고 보관한 뒤 팀원을 실제로 내린다.
  지금 절차에 그 걸음이 없어서 2026-08-07 에 팀원 넷이 일이 끝난 뒤에도 계속 떠 있었다.
  이것은 명령이 하는 일이 아니라 **감독이 하는 걸음**이다 — 명령은 스크립트라 팀원에게 메시지를
  못 보낸다. 그렇게 갈라 적는다.
- 회귀 시험을 `stage/scripts/tests/test_land_run.py` 에 만든다.

### Excluded

- **훅을 안 고친다.** DE-00000065 의 핵심이 그것이다 — 명령이 스스로 거절할 뿐, 커밋 게이트도
  승격 게이트도 그대로다.
- 충돌을 자동으로 풀지 않는다. 충돌이 나면 되돌리고 사람에게 넘긴다.
- 감사가 커밋 메시지 기록의 누락을 세게 만들지 않는다. 결정이 그 값을 알고 물었고 별도 카드다.

## Risks

- **게이트를 지나는 커밋을 만드는 명령이다.** 거절 조건을 하나라도 빠뜨리면 그 자리가 조용한
  우회가 된다. 조건은 결정에 번호로 있고, 시험이 조건마다 하나씩 있어야 한다.
- 순서가 보장을 만든다 — 검사 → 워크트리 커밋 → `--no-commit` 병합 → 남은 검사 → 병합 커밋.
  순서를 바꾸면 미검사 병합이 본 가지에 닿는다.
- `drive_parallel.py` 의 치우기와 겹친다. 두 벌이 되면 한쪽만 고쳐지는 날이 온다.


## Success criteria

- 명령 하나가 워크트리 로그 옮기기·커밋·병합·정리를 끝까지 하고, 사람이 병합용 작업 항목을 등록하지 않아도 커밋 게이트에 안 막힌다
- DE-00000065 의 거절 조건을 하나라도 못 맞추면 본 가지에 아무것도 안 닿고 명령이 실패로 알린다
- 워크트리 커밋과 병합 커밋 둘 다 메시지에 카드와 원본 가지를 담는다
- 손 병합을 시키던 절차 산문이 이 명령을 가리키고, 팀원 가지 접두사가 선언돼 있다

## Next action

`.stage/official/decisions/records/DE-00000065.md` 를 먼저 읽는다 — 명령이 하는 일 넷과 거절
조건이 거기 번호로 있다. 그다음 `drive.py` 의 `commit_item`(가지 자기거절, 범위 담기)과
`drive_parallel.py` 의 `cleanup_worktree` 를 읽고, 새로 쓸 것과 부를 것을 가른다.

## Related truth

- DE-00000065 — 이 카드의 명세. 명령이 하는 일과 거절 조건, 그리고 명령 카드 몫으로 남긴
  것들(커밋 메시지 형태, 가지 접두사 선언, 치우기 중복 금지)이 Follow-up 에 있다.
- O-00000035 — 병합 때 커밋 게이트가 막은 실측. **이 명령이 생기고 실행 한 판을 끝에서 끝까지
  돌린 뒤에** 닫는다(결정의 Follow-up 이 그렇게 정했다).
- W-00000236(보관됨) — 드라이버가 카드 파일을 선언 범위와 함께 담게 한 카드. 이 명령은 그
  목록에 회고 파일을 하나 더 얹는다.
- M-00000004 완료 기준 첫째의 뒤쪽 절반이 이 카드다. 앞쪽 절반(자격 결정)은 W-00000234 가 했다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
