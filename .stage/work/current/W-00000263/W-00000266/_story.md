---
id: W-00000266
title: 정한 대로 스타일 파일을 내고 훅을 물러나게 한다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: active
verification: passed
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: plainly/
promotes:
decision_refs:
---

# W-00000266 정한 대로 스타일 파일을 내고 훅을 물러나게 한다

## Purpose

설계대로 output style 파일을 만들고 같은 글이 훅으로 겹쳐 들어가지 않게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- output-styles 아래 스타일 파일이 생기고 모두 keep-coding-instructions 를 true 로 담는다
- 고정 규칙이 원본과 어긋나면 테스트가 깨진다
- 스타일이 켜져 있으면 훅이 아무것도 넣지 않는다

## Next action


## Related truth


## Progress

`plainly/output-styles/` 아래 다섯 개를 냈다. `styles/` 가 baseline·델타 네 개·fixed-rules.md 를
소유하고 `scripts/build_styles.py` 가 붙여서 만든다. 만든 파일을 커밋했다.

훅은 물러나는 게 아니라 없앴다. 코덱스에서 안 쓴다고 사용자가 밝혔으므로 훅을 남길 이유가
없어졌다. `hooks/`, `src/plainly/`, `scripts/configure.py`, `skills/plainly-configure/`,
`.codex-plugin/` 을 지웠다. 성공 기준 세 번째("스타일이 켜져 있으면 훅이 아무것도 넣지 않는다")는
넣을 훅 자체가 사라져서 충족된다.

범위를 세 군데 넘었다. `tests/test_plugin_contracts.py` 는 모든 플러그인이 두 매니페스트를
갖도록 요구해서 깨졌고, 한 호스트만 지원하는 플러그인을 허용하게 고쳤다. `README.md` 와
`CLAUDE.md` 의 플레인리 설명도 고쳤다.

범위 밖에서 하나 더 나왔다. `stage/scripts/release_plugin.py` 가 두 매니페스트를 다 요구해서
플레인리 릴리스가 막혔다. 있는 매니페스트만 올리고 하나도 없으면 거부하도록 고치고 테스트 두
개를 붙였다.

## Verification

테스트 네 스위트가 통과한다.

- `python3 -m unittest discover -s plainly/tests -q` — 16개
- `python3 -m unittest discover -s tests -q` — 7개
- `python3 -m unittest discover -s stage/scripts/tests -q` — 637개
- `python3 -m unittest discover -s stage/hooks/tests -q` — 374개

실제 세션에서도 확인했다. `claude -p --plugin-dir plainly --settings
'{"outputStyle":"plainly:Decision"}' --debug-file` 로 돌리니 디버그 로그가
`Loaded 5 output styles from plugin plainly default directory` 를 찍고, 고른 스타일이 답을
지배하고, 플레인리 훅은 하나도 등록되지 않는다.

`keep-coding-instructions` 가 실제로 코딩 지침을 남기는지는 여기서 못 봤다. `-p` 세션에는 그
지침 덩어리가 아예 없어서 스타일을 켜든 안 켜든 갈리지 않는다. W-00000267 이 대화형 세션에서
본다.

## Retrospective


## Promotion decision
