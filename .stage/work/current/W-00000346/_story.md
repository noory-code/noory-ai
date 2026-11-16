---
id: W-00000346
title: 게이트가 변수로 쓴 cd 와 && 로 이어진 cd 를 따라가서 쓰기 대상을 읽는다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_shell.py, stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, stage/hooks/README.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000346 게이트가 변수로 쓴 cd 와 && 로 이어진 cd 를 따라가서 쓰기 대상을 읽는다

## Purpose

같은 명령에서 정한 변수로 저장소 밖 폴더에 들어가 그 폴더의 파일을 고치는 명령을 열린 카드가 없다는 이유로 막지 않는다

## Actions

없음 — 셸 파서가 쓰기·지우기 대상을 셀 때 `cd` 를 따라가는 규칙 두 가지를 고친다.

## User value

2026-11-16 에 `S=스크래치 && … && cd $S/x && sed -i … f.md` 와 `for d in …; rm -rf "$d"` 같은
명령이 열린 카드가 없다는 이유로 막혔다. 게이트가 `f.md` 를 저장소 폴더의 파일로 읽었기 때문이다.
같은 명령에서 정한 변수로 폴더를 옮기는 명령은 흔하다. 고치면 이런 명령을 리터럴 경로로 다시 쓰지
않아도 되고, 범위 알림도 실제로 쓰는 경로를 가리킨다.

원인은 두 가지다. 확인 방법은 `shell_write_paths` 에 명령을 넣어 본 것이다.

- `cd $S` 의 변수를 풀지 않는다. `$S` 라는 폴더가 없으니 `cd` 가 실패했다고 보고 원래 폴더에
  남는다고 계산한다.
- 앞에 `&&` 가 붙은 `cd` 를 "일어나지 않았을 수도 있다"고 보고, 뒤 명령을 원래 폴더와 새 폴더
  두 곳에 모두 둔다. 하지만 `A && cd D && B` 에서 B 는 `cd D` 가 성공했을 때만 돈다.

## Scope

### Included

- 쓰기·지우기 대상을 셀 때 `cd`/`pushd` 인자 앞의 변수(`$S`, `${S}`)를 같은 명령의 `NAME=value`
  나 훅의 환경 변수로 푼다. 대상 경로 변수를 푸는 W-00000338 과 같은 규칙이다.
- 쓰기·지우기 대상을 셀 때, `&&` 로만 이어진 줄 안에서는 `cd` 뒤 명령을 그 `cd` 의 폴더에서만
  읽는다. 줄이 `;` 나 줄바꿈으로 끝나거나 `||`·`|` 가 끼면 그때까지 놓았던 원래 폴더를 다시 더한다.
- 훅 문서(`stage/operations/hooks.md`, `stage/hooks/README.md`)와 변경 기록에 적는다.

### Excluded

- `.stage` 삭제 검사(`command_deletes_stage`). 지금 방식, 곧 두 폴더를 모두 보는 방식을 그대로 둔다.
- `git_runs_outside_workspace` 의 `cd` 따라가기. 커밋 대상은 따로 다룬다.
- 루프 변수(`for d in …`). 훅이 값을 알 수 없으므로 막는 것이 맞다.

## Risks

- 두 고침 모두 허락하는 쪽으로 움직인다. `&&` 규칙을 잘못 세우면 저장소 쓰기를 놓칠 수 있다.
  그래서 `&&` 만으로 이어진 경우에만 적용하고, `||`·`|`·`&` 가 끼면 지금처럼 둔다.
- 환경 변수는 훅의 환경에서 읽는다. 셸의 환경과 다르면 틀린 폴더를 따라갈 수 있다. W-00000338 도
  같은 가정을 쓴다.


## Success criteria

- S=밖폴더 && mkdir -p $S && cd $S && sed -i 로 파일을 고치는 명령이 등록 게이트를 통과한다
- && 로만 이어진 줄에서 cd 뒤의 쓰기는 cd 한 폴더에서만 읽고, ; 뒤나 || 가 낀 줄에서는 지금처럼 두 폴더를 모두 본다
- 훅이 값을 모르는 변수로 cd 하면 지금처럼 원래 폴더에 남는다고 보고 막는다
- .stage 삭제 검사는 바뀌지 않는다
- 새 테스트가 고치기 전 코드에서 실패하고 고친 뒤 통과한다

## Next action

고치기 전 코드에서 실패하는 테스트를 `test_stage_guard.py` 에 먼저 쓴다.

## Related truth

- W-00000342 — 쓰기 대상을 훅의 `cwd` 에서 읽기 시작하게 했다(보관됨).
- W-00000338 — 대상 경로 앞의 같은 명령 변수를 풀게 했다(보관됨).
- DE-00000087 — 게이트를 바꾸는 카드는 닫기 전에 사용자 확인을 받는다.


## Progress


## Verification


## Retrospective


## Promotion decision
