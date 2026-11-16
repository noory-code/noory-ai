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
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000346
promotion: not_applicable
review: passed
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

`stage_shell.py` 의 `_command_groups` 에 두 선택을 더했다. `assignments` 를 주면 `cd`·`pushd`·`mkdir`
인자 앞의 변수를 `expand_leading_variable` 로 푼다. `follow_and_chains` 를 켜면 앞에 `&&` 가 붙은
`cd` 를 그 줄의 나머지에서는 일어난 것으로 보고, 그 전 폴더는 따로 잡아 두었다가 줄이 끝나거나
`||`·`|`·`&` 를 만나면 다시 더한다. `shell_write_paths`·`shell_delete_paths` 가 두 선택을 받고,
`mutation_targets` 만 둘 다 켠다. `.stage` 삭제 검사(`command_deletes_stage`)는 아무것도 넘기지
않으므로 그대로다. 변수 정규식은 `stage_shell.py` 한 곳에 두고 `stage_guard.py` 가 가져다 쓴다.
문서 두 곳과 변경 기록에 적었다. 커밋 `3e193051`.

`mkdir` 인자도 풀어야 했다. `mkdir -p $S/sub && cd $S/sub` 에서 만들 폴더를 풀지 않으면 그 폴더로
들어가는 `cd` 가 실패한 것으로 읽힌다. 처음 고친 뒤 이 경우만 남아서 알았다.

## Verification

- `S=밖폴더 && mkdir -p $S/sub && cd $S/sub && sed -i` 가 등록 게이트를 통과한다 — 통과. 새 테스트
  `test_registration_gate_follows_cd_through_variables_and_and_chains` 의 허락 네 경우(변수 `cd` 가
  있는 `&&` 줄, `;` 뒤의 따옴표 변수, 중괄호 변수와 `rm`, 리터럴 `cd` 가 있는 `&&` 줄).
- `&&` 로만 이어진 줄에서만 `cd` 폴더만 보고, `;` 뒤나 `||`·`|` 가 낀 줄에서는 두 폴더를 모두
  본다 — 통과. 같은 테스트의 거절 경우 `false && cd 밖 ; echo > f.md`, `true || cd 밖 && echo`,
  `true | cd $S && echo`.
- 훅이 값을 모르는 변수로 `cd` 하면 막는다 — 통과. 같은 테스트의 `cd "$STAGE_TEST_UNSET_CD"`.
- `.stage` 삭제 검사는 바뀌지 않는다 — 통과. 같은 테스트의 `true && cd src && rm -rf .stage` 가
  삭제 검사 메시지로 막힌다. `&&` 규칙이 이 검사에도 적용됐다면 `src/.stage` 로만 읽혀 통과했을
  경우다.
- 새 테스트가 고치기 전 코드에서 실패하고 고친 뒤 통과한다 — 통과. 고치기 전에는 허락 네 경우가
  모두 실패했다. 거절 경우와 `.stage` 경우는 고치기 전에도 막혔다(바뀌면 안 되는 경우다).
- 전체 테스트: 훅 448개 통과, 스크립트 758개 통과(건너뜀 2개). 감사 오류 0개.
- 확인하지 않은 것: 실제 세션에서의 동작. 지금은 이 카드가 열려 있어 등록 게이트가 걸리지 않는다.
  머지한 뒤 열린 카드가 없을 때 확인할 수 있다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).
- 사용자 확인 — 2026-11-17: 게이트를 바꾼 카드라 닫기 전에 사용자에게 보였다(DE-00000087). 보인
  것은 바뀐 파일과 두 선택의 동작, `.stage` 삭제 검사를 그대로 둔 것, 새 테스트가 고치기 전에 네
  경우 실패한 것, 막혀야 할 경우들, 전체 테스트와 감사 결과, 실제 세션은 확인하지 못한 것이다. 닫기
  리뷰는 이 확인 뒤에 돌렸다. 사용자가 "확인, 닫기"로 답했다.


### Executed at close — 2026-11-17

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 268 tests in 1.014s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 448 tests in 5.368s

OK

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

### Review at close — 2026-11-17

```
Review report: .stage/.runtime/driver/logs/W-00000346.md
Criteria:
- PASS: S=밖폴더 && mkdir -p $S && cd $S && sed -i 로 파일을 고치는 명령이 등록 게이트를 통과한다
  Reason: Ran test_stage_guard.py (268 OK); its allow subtests (variable cd in an && chain, quoted/braced variable, literal cd) pass, and I ran shell_write_paths on the exact `S=/private/tmp/x346 && mkdir -p $S && cd $S && sed -i` form with mutation_targets' options, which returned only /private/tmp/x346/f.md versus project-root paths without them.
- PASS: && 로만 이어진 줄에서 cd 뒤의 쓰기는 cd 한 폴더에서만 읽고, ; 뒤나 || 가 낀 줄에서는 지금처럼 두 폴더를 모두 본다
  Reason: Test refuse subtests (chain ends at ;, cd after ||, cd fed by a pipe) pass; my probe of shell_write_paths showed `true && cd X && echo > f` reads f only under X, while the target after `||`, `&`, or a newline is read in both the project root and X, and a piped cd keeps both folders.
- PASS: 훅이 값을 모르는 변수로 cd 하면 지금처럼 원래 폴더에 남는다고 보고 막는다
  Reason: The `cd "$STAGE_TEST_UNSET_CD" && echo x > f.md` subtest is denied by the registration gate, and my probe of `cd $UNSET_346_X && echo a > f` returned only the project-root f; expand_leading_variable returns the operand unchanged when no value is found.
- PASS: .stage 삭제 검사는 바뀌지 않는다
  Reason: The diff of 3e193051 leaves command_deletes_stage untouched and it passes neither assignments nor follow_and_chains to _command_groups; the test's `true && cd src && rm -rf .stage` is still denied with the `.stage` delete message, and all 448 hook tests pass.
- PASS: 새 테스트가 고치기 전 코드에서 실패하고 고친 뒤 통과한다
  Reason: I extracted stage/ at 3e193051^ into the scratchpad, copied in the new test file, and ran the new test: 4 failures (all four allow cases); on the current tree the same test passes with the full test_stage_guard.py run (268 OK).
```

## Retrospective

[R-00000346](../../retrospectives/R-00000346.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
