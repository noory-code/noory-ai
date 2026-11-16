---
id: W-00000345
title: plainly 0.8.0 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000345
promotion: not_applicable
review: not_required
scope: plainly/CHANGELOG.md, plainly/.claude-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000345 plainly 0.8.0 을 낸다

## Purpose

플러그인을 켜면 스타일이 바로 적용되는 계약과 평가 질문이 아직 이 저장소 안에만 있으므로, 버전을 올려 다른 컴퓨터와 프로젝트가 받을 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 매니페스트를 함께 움직인다.

## User value

다른 컴퓨터에서 플레인리를 받은 사람도 플러그인을 켜기만 하면 스타일이 적용된다. `outputStyle`
설정을 따로 하지 않아도 된다. 평가 질문도 함께 받으므로 어디서든 `claude plugin eval` 로 다시 잴
수 있다. 이 컴퓨터는 저장소 폴더에서 바로 읽으므로 이미 쓰고 있다.

## Scope

### Included

- 마이너 버전을 올린다(0.7.3 → 0.8.0). 스타일을 고르는 방식에서 켜면 적용되는 방식으로 계약이
  바뀌었기 때문이다.
- 쌓인 변경 기록 한 묶음(W-00000344)에 그 버전 제목을 붙인다.
- 매니페스트를 같은 버전으로 옮긴다. 플레인리는 Claude Code 매니페스트 하나만 싣는다.
- PR 로 main 에 합치고, 합친 뒤 `claude plugin list` 와 새 세션의 디버그 로그로 확인한다.

### Excluded

- 다른 플러그인 릴리스.

## Risks

- 이 컴퓨터는 플러그인을 저장소 폴더에서 바로 읽어서, 설치본 확인으로는 다른 컴퓨터에서
  받는 경우를 가려내지 못한다. 확인한 범위를 그대로 적는다.
- 이미 다른 출력 스타일을 고른 사람은 업데이트 뒤 플레인리로 바뀐다. 변경 기록과 README 에 그
  사실과 끄는 법을 적었다(W-00000344).

## Success criteria

- 매니페스트와 변경 기록이 0.8.0 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 plainly 를 0.8.0 으로 읽는다
- 새 세션이 outputStyle 설정 없이 플레인리를 강제 적용한다는 디버그 로그 줄을 남긴다

## Next action

`python3 stage/scripts/release_plugin.py plainly --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.
- W-00000344 — 이 릴리스가 담는 변경(보관됨).

## Progress

0.7.3 → 0.8.0. 쌓여 있던 한 묶음에 그 버전 제목이 붙었고 매니페스트가 같은 값을 말한다. 릴리스
커밋 `2489585d` 를 PR #51 로 main 에 합쳤다(`bf84812b`). macOS 3.9 작업 하나가 러너를 받지 못해
취소됐고, 다시 돌려 통과한 뒤 합쳤다.

## Verification

- 매니페스트와 변경 기록이 0.8.0 하나를 말한다 — 통과. `plainly/.claude-plugin/plugin.json` 이
  `0.8.0` 이고 변경 기록에 `## 0.8.0 — 2026-11-16` 이 있다.
- 릴리스 커밋이 원격 main 에 올라갔다 — 통과. PR #51 이 CI 검사 24개 통과 뒤 합쳐졌다.
- `claude plugin list` 가 plainly 를 0.8.0 으로 읽는다 — 통과. `Version: 0.8.0`, `Read from:` 이
  저장소의 `plainly` 폴더다.
- 새 세션이 `outputStyle` 설정 없이 플레인리를 강제 적용한다 — 통과. 사용자 설정을 읽지 않고
  (`--setting-sources ""`) 플러그인만 켠 `claude -p` 세션의 디버그 로그에 `Using forced plugin
  output style: plainly:Plainly` 가 남았고, 적용된 스타일을 물으니 `plainly:Plainly` 라고 답했다.
- 확인하지 않은 것: 이 저장소 폴더가 아닌 곳에서 받아 설치하는 경우.

### Executed at close — 2026-11-17

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 22 tests in 0.002s

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

## Retrospective

[R-00000345](../../retrospectives/R-00000345.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.

