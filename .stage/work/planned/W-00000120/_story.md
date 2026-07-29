---
id: W-00000120
title: 깊이 1 예외에서 카드 이름 모양을 다시 뺀다
kind: fix
venue:
milestone:
status: captured
priority: 2
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/hooks/, stage/hooks/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
---

# W-00000120 깊이 1 예외에서 카드 이름 모양을 다시 뺀다

## Purpose

W-00000114 가 수명 주기 루트 깊이 1 의 .md 를 카드 모양 검사에서 빼면서, 은퇴한 v4 평평한 카드(work/current/W-xxx.md)도 함께 통과하게 됐다. 전에는 게이트가 그 자리에서 막았고 지금은 감사(WORK026)가 나중에 잡는다 — 조기 차단이 사후 감지로 내려앉았다. 깊이 1 예외에서 작업 ID 모양 이름(W-숫자.md)만 도로 빼서 조기 차단을 되살린다. 인덱스·README·템플릿은 그대로 통과해야 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
