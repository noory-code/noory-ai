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
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
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


## Verification


## Retrospective


## Promotion decision
