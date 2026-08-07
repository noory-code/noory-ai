---
id: W-00000239
title: 들이는 커밋이 담을 것을 실측에 맞게 다시 정한다
kind: design
venue: claude
milestone: M-00000004
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/decisions/
promotes:
decision_refs:
---

# W-00000239 들이는 커밋이 담을 것을 실측에 맞게 다시 정한다

## Purpose

DE-00000065 가 들이는 커밋의 허용 목록을 셋으로 못박았는데 카드를 닫으면 반드시 바뀌는 인덱스 둘이 그 밖이라 그 명세대로는 명령을 만들 수 없으므로, 실제 종료 커밋이 담는 것을 세어 허용 목록을 다시 정한다

## Actions

없음 — 앞선 결정을 잇는 결정 하나를 세우는 한 덩어리다.

## User value

들이는 명령을 실제로 만들 수 있게 된다. 지금 명세로는 못 만든다 — W-00000238 이 만들어 보다
부딪혀 물렸다.

## Scope

### Included

**감독이 이미 세어 둔 것.** 오늘 드라이버가 낸 종료 커밋 넷을 열어 보니 담는 것이 매번
같은 넷이었다:

| 담기는 것 | DE-00000065 조건 3 |
|---|---|
| `.stage/work/active.md` (줄 빠짐) | **금지** |
| 닫힌 카드 파일 | 허용 |
| 그 카드의 회고 파일 | 허용 |
| `.stage/work/review.md` (줄 붙음) | **금지** |

- **허용 목록을 실측에 맞게 다시 정한다.** 위 넷을 전부 덮어야 한다.
- **단수를 복수로 고친다.** 조건 3은 "카드 파일"과 "회고 파일"을 하나씩으로 못박는데, 계층
  실행은 여럿이다 — 액션을 닫고 부모를 닫으면 카드 둘, 회고 둘이다(`driver: W-00000237
  ancestor aggregation (lifecycle)` 이 부모 카드와 부모 회고를 따로 담는다).
- **어느 커밋을 세어 이 목록이 나왔는지 결정에 적는다.** 다음에 이 목록을 의심하는 사람이
  같은 방법으로 다시 셀 수 있어야 한다.
- **넓힌 목록이 여전히 막는 것을 적는다.** 넓히는 결정이므로, 무엇이 아직 못 들어오는지가
  없으면 목록이 아니라 백지수표가 된다.

### Excluded

- DE-00000065 의 나머지는 안 건드린다. 거절 조건 여덟 중 일곱, 커밋 메시지 기록,
  `--no-ff --no-commit` 순서, 훅 무변경은 그대로 유효하다. **고칠 것은 조건 3의 허용 목록
  하나다.**
- 승격된 결정을 고쳐 쓰지 않는다. 잇는 결정을 세우고 앞 결정을 `supersedes` 한다.
- 명령을 만들지 않는다. 그건 이 결정 뒤에 W-00000238 을 다시 세워서 한다.

## Risks

- **넓히는 결정이다.** 허용 목록이 커질수록 "이 명령이 무엇을 담을 수 있나"의 답이 흐려진다.
  실측에서 나온 넷과 계층에서 나오는 복수만 넣고, 그 밖은 넣지 않는다.
- 실측이 오늘 하루의 커밋 넷이다. 다른 모양의 종료(예: 거절된 카드, 보관까지 한 번에)가 다른
  파일을 담는지 안 세 봤다면 그 사실을 결정에 적는다 — 안 센 것을 센 것처럼 쓰지 않는다.


## Success criteria

- 허용 목록이 실제 종료 커밋이 담는 것을 전부 덮고, 그 목록이 어느 커밋을 세어 나왔는지가 결정에 적혀 있다
- 넓힌 목록이 무엇을 여전히 막는지가 결정에 적혀 있다

## Next action

감독이 센 것을 그대로 믿지 말고 직접 다시 센다 — `git log --all --grep="driver: W-000002"`
로 종료 커밋을 찾아 `git show <커밋> --stat` 으로 담긴 파일을 본다. 그다음
`.stage/official/decisions/records/DE-00000065.md` 의 조건 3을 읽고 잇는 결정을 세운다.

## Related truth

- DE-00000065 — 이어받을 결정. 조건 3의 허용 목록만 고치고 나머지는 그대로 둔다.
- O-00000040 — 이 모순의 실측. 판정 다섯 바퀴가 못 잡은 것을 구현 시도가 잡았다.
- W-00000238(물림, R-00000237) — 만들어 보다 부딪힌 카드. 이 결정이 서면 다시 세운다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
