---
id: W-00000120
title: 깊이 1 예외에서 카드 이름 모양을 다시 뺀다
kind: fix
venue: codex
milestone:
priority: 2
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/, stage/hooks/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000120 깊이 1 예외에서 카드 이름 모양을 다시 뺀다

## Purpose

W-00000114 가 수명 주기 루트 깊이 1 의 .md 를 카드 모양 검사에서 빼면서, 은퇴한 v4 평평한 카드(work/current/W-xxx.md)도 함께 통과하게 됐다. 전에는 게이트가 그 자리에서 막았고 지금은 감사(WORK026)가 나중에 잡는다 — 조기 차단이 사후 감지로 내려앉았다. 깊이 1 예외에서 작업 ID 모양 이름(W-숫자.md)만 도로 빼서 조기 차단을 되살린다. 인덱스·README·템플릿은 그대로 통과해야 한다.

## Actions

- 깊이 1 예외에서 **작업 ID 모양 이름**(`W-` + 숫자 + `.md`)만 도로 뺀다. 인덱스·README·
  템플릿은 그대로 통과해야 한다 — 그것을 막던 것이 W-00000114 가 고친 잠금이다.
- 은퇴한 평평한 카드가 게이트에서 다시 거절되는 것을 테스트로 고정한다. 그러면서 W-00000114
  가 연 자리(계획 인덱스 편집 허용)가 안 깨지는 것도 같은 묶음에서 고정한다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

손으로 만든 옛 모양 카드가 게이트에서 바로 막힌다. 지금은 통과했다가 나중에 감사에서
`WORK026` 으로 잡히는데, 조기 차단이 사후 감지로 내려앉은 상태다.

## Scope

### Included


### Excluded


## Risks

- 예외를 좁히다 인덱스·템플릿까지 막으면 W-00000114 가 고친 잠금이 되살아난다. 두 성질을
  같은 테스트 묶음에서 함께 고정해 한쪽을 고치다 다른 쪽이 깨지지 않게 한다.

## Success criteria

- 수명 주기 폴더 깊이 1 에 놓인 `W-<숫자>.md` 파일 쓰기가 게이트에서 거절된다. 테스트가
  고정한다.
- `index.md`·`README.md`·`_template.md` 편집은 그대로 통과한다. 같은 묶음의 테스트가
  고정한다.
- 깊이 2·3 의 진짜 카드 검사와 부모 게이트는 그대로다 — 기존 훅 테스트가 전부 통과한다.
- `python3 -m unittest discover -s stage/hooks/tests -q` 와
  `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

## Verification

## Retrospective

## Promotion decision
