---
id: W-00000344
title: 플레인리를 켜면 스타일이 바로 적용되게 하고 비교 실험을 기본 평가 명령으로 옮긴다
kind: development
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000344
promotion: not_applicable
review: passed
scope: plainly/output-styles/plainly.md, plainly/tests/test_contract.py, plainly/README.md, plainly/CHANGELOG.md, plainly/evals, plainly/.claude-plugin/plugin.json, plainly/.gitignore, .claude-plugin/marketplace.json, README.md
promotes:
decision_refs:
---

# W-00000344 플레인리를 켜면 스타일이 바로 적용되게 하고 비교 실험을 기본 평가 명령으로 옮긴다

## Purpose

플레인리가 한국어 답을 실제로 바꾸는지 같은 질문으로 언제든 다시 재 볼 수 있게 한다

## Actions

없음 — 스타일 파일 한 줄, 평가 질문 다섯 개, 테스트와 문서를 함께 바꾼다.

## User value

플레인리 규칙을 고칠 때마다 고치기 전과 후를 같은 질문으로 다시 잴 수 있다. 지금까지는 스크래치에
짠 스크립트로 쟀고, 스크래치가 지워지면 질문과 세는 방법을 다시 만들어야 했다. Claude Code 의
`claude plugin eval` 이 플러그인을 켠 경우와 끈 경우를 함께 돌리므로 비교하는 코드를 따로 둘
필요도 없다.

2026-11-16 스크래치 복사본에서 시험한 결과, 평가는 플러그인의 출력 스타일을 저절로 켜지 않았다.
스타일 파일에 `force-for-plugin: true` 를 넣자 켠 쪽에서만 스타일이 적용됐다. 사용자는 플레인리를
켜면 스타일이 바로 적용되도록 계약을 바꾸기로 정했다.

## Scope

### Included

- `plainly/output-styles/plainly.md` 에 `force-for-plugin: true` 를 넣는다. 플러그인을 켜면
  `outputStyle` 설정과 상관없이 이 스타일이 적용된다.
- `plainly/evals/` 에 질문과 정규식 채점 기준을 둔다. 스타일이 켜졌는지 보는 질문 하나와,
  예전 비교 실험의 한국어 질문 네 개(작업 보고, 두 기준 설명, 실제 세션 테스트 설명, 동료에게
  설명하는 글)다. 채점은 "실측", "축", "재측정", 엠대시 같은 모양이 답에 없는지 본다.
- 평가 결과 폴더(`plainly/evals/results/`)는 git 에 올리지 않는다.
- 테스트: frontmatter 에 `force-for-plugin` 이 정확한 철자로 있는지, `evals/` 에 마크다운만
  있는지 확인한다.
- README, 플러그인 매니페스트 설명, 마켓플레이스 설명, 저장소 README 의 플레인리 소개를 새
  계약에 맞춘다. 저장소 README 는 지금 "출력 스타일 다섯 개"라고 잘못 적혀 있다.
- 변경 기록 `## Unreleased` 에 적는다.

### Excluded

- 실제 대화 기록을 세는 스크립트. 사용자의 대화 기록을 읽으므로 공개 저장소에 두지 않는다.
- 릴리스. 계약이 바뀌므로 마이너 버전이 되며, 이 카드를 합친 뒤 따로 낸다.
- LLM 채점기. 돈이 드는 채점은 필요해질 때 더한다.

## Risks

- 플러그인을 켠 사람은 다른 출력 스타일을 고를 수 없다. Claude Code 는 강제된 플러그인 스타일이
  있으면 `outputStyle` 설정을 보지 않는다(2.1.321 코드에서 확인). 다른 스타일을 쓰려면 플러그인을
  꺼야 한다.
- 정규식 채점은 모양만 본다. 뜻이 보존됐는지는 재지 못한다.
- 평가를 돌릴 때마다 `claude` 실행 비용이 든다. 질문 다섯 개를 기본 3번씩, 켠 쪽과 끈 쪽으로
  돌리면 30번이다.


## Success criteria

- 플레인리를 켜면 outputStyle 설정 없이도 스타일이 적용되고, 평가의 스타일 확인 질문이 켠 쪽에서만 통과한다
- claude plugin eval 로 한국어 질문 네 개를 돌리면 플러그인을 켠 경우와 끈 경우의 점수가 함께 나온다
- 테스트가 force-for-plugin 철자와 evals 폴더에 마크다운만 있다는 것을 확인한다
- README 와 매니페스트·마켓플레이스 설명이 켜면 바로 적용되고 다른 스타일을 쓰려면 플러그인을 꺼야 한다고 말한다

## Next action

`force-for-plugin` 과 `evals/` 를 확인하는 테스트를 먼저 쓰고 실패하는 것을 본다.

## Related truth

- W-00000263 — 플레인리를 한국어 전용 스타일 하나로 정리한 에픽(보관됨).
- `plainly/tests/test_contract.py` — 플러그인이 스타일 말고 실행되는 것을 싣지 않는다는 계약.


## Progress

스타일 파일에 `force-for-plugin: true` 를 넣었다. `plainly/evals/` 에 질문 다섯 개와 정규식 채점
기준 열 개를 두었고, 결과 폴더는 `plainly/.gitignore` 로 뺐다. 플러그인 README 에 켜고 끄는 법과
평가 절을 새로 썼고, 매니페스트·마켓플레이스 설명과 저장소 README 소개를 맞췄다. 커밋 `6fc759b6`.

Claude Code 2.1.321 코드에서 확인한 것: 강제된 플러그인 스타일이 있으면 `outputStyle` 설정을 보지
않고 그 스타일을 쓴다. 디버그 로그에 `Using forced plugin output style:` 줄을 남긴다.

## Verification

- 플러그인을 켜면 `outputStyle` 설정 없이도 스타일이 적용되고, 스타일 확인 질문이 켠 쪽에서만
  통과한다 — 통과. 바꾼 플레인리를 스크래치에 복사해 `claude plugin eval . --trust-plugin` 을
  돌렸다. `style-active` 가 켠 쪽 1.00, 끈 쪽 0.00 이다. 바꾸기 전 복사본에서는 두 쪽 모두 "없음"
  이라고 답했고 trace 의 `output_style` 이 `default` 였다.
- 한국어 질문 네 개의 점수가 켠 쪽과 끈 쪽으로 함께 나온다 — 통과. 같은 실행, 질문마다 3번씩:

  | 질문 | 켠 쪽 | 끈 쪽 | 끈 쪽에서 걸린 채점 |
  |---|---|---|---|
  | `two-axes` | 1.00 | 0.50 | "축" 세 번 모두 |
  | `explain-to-colleague` | 1.00 | 0.83 | 엠대시 한 번 |
  | `work-report` | 1.00 | 1.00 | 없음 |
  | `live-test` | 1.00 | 1.00 | 없음 |

  `work-report` 와 `live-test` 는 이번 실행에서 두 쪽 차이가 없었다. 끈 쪽 모델도 "재측정",
  "실기", "실측" 을 쓰지 않았다. 두 질문은 이 말들이 다시 나오는지 지키는 용도로 남긴다. 실행에
  쓰인 모델은 결과 파일에 남지 않아 확인하지 못했다. 비용은 $2.04 다.
- 테스트가 `force-for-plugin` 철자와 `evals/` 에 마크다운만 있다는 것을 확인한다 — 통과. 새 테스트
  세 개(`test_the_style_applies_as_soon_as_the_plugin_is_enabled`,
  `test_descriptions_do_not_call_the_style_selectable`, `test_evals_hold_markdown_cases_only`)와
  바뀐 frontmatter 키 테스트가 바꾸기 전에 다섯 군데 실패했고, 바꾼 뒤 22개 모두 통과한다. 저장소
  계약 테스트 7개도 통과한다.
- README 와 설명이 켜면 바로 적용되고 다른 스타일을 쓰려면 플러그인을 꺼야 한다고 말한다 — 통과.
  플러그인 README 의 "Turning it on and off" 절, 매니페스트와 마켓플레이스의 "applied while the
  plugin is enabled".
- 평가를 저장소 폴더가 아니라 스크래치 복사본에서 돌렸다. `--trust-plugin` 허락을 스크래치 복사본에
  대해 받았기 때문이다. 내용은 커밋 `6fc759b6` 과 같다.
- 정규식 채점은 문장 모양만 본다. 뜻이 보존됐는지는 재지 않았다.


### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 22 tests in 0.003s

OK

$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 22 tests in 0.003s

OK

$ python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.002s

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

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000344.md
Criteria:
- PASS: 플레인리를 켜면 outputStyle 설정 없이도 스타일이 적용되고, 평가의 스타일 확인 질문이 켠 쪽에서만 통과한다
  Reason: plainly/output-styles/plainly.md frontmatter has force-for-plugin: true; I did not rerun claude plugin eval, but read the recorded run's aggregate-result.json (Claude 2.1.321, scratch copy whose plainly/ diff -r against the repo shows no difference) where style-active scores with 1.00 and without 0.00.
- PASS: claude plugin eval 로 한국어 질문 네 개를 돌리면 플러그인을 켠 경우와 끈 경우의 점수가 함께 나온다
  Reason: I did not rerun the eval; the recorded aggregate-result.json holds with and without arms for all four Korean cases (two-axes 1.00 vs 0.50, explain-to-colleague 1.00 vs 0.83, work-report and live-test 1.00 vs 1.00), matching the card's Verification table.
- PASS: 테스트가 force-for-plugin 철자와 evals 폴더에 마크다운만 있다는 것을 확인한다
  Reason: Ran python3 -m unittest discover -s plainly/tests -q: 22 tests OK; test_the_style_applies_as_soon_as_the_plugin_is_enabled asserts the exact force-for-plugin key and test_evals_hold_markdown_cases_only asserts every non-results file under evals/ is .md and each case has graders.
- PASS: README 와 매니페스트·마켓플레이스 설명이 켜면 바로 적용되고 다른 스타일을 쓰려면 플러그인을 꺼야 한다고 말한다
  Reason: plainly/README.md 'Turning it on and off' says enabling applies the style, it replaces outputStyle, and another style means /plugin disable; plugin.json and marketplace.json say 'applied while the plugin is enabled' and no longer call it selectable; the repo README now says one style applied while enabled.
```

## Retrospective

[R-00000344](../../retrospectives/R-00000344.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
