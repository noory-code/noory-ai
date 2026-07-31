---
id: W-00000168
title: 실행하는 쪽이 무엇을 스스로 하고 무엇을 보고하는지 계약으로 세운다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000168
promotion: not_applicable
review: not_required
scope: stage/docs/, stage/skills/stage-drive/, stage/scripts/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000168 실행하는 쪽이 무엇을 스스로 하고 무엇을 보고하는지 계약으로 세운다

## Purpose

2026-07-31 에 사고가 둘 났는데 **원인이 같다 — 만든 쪽이 자기가 내린 판단을 보고에 안 적었다.**

- 목적을 띄우는 장치를 만들 때, 설계가 "작업이 둘 이상 돌면 어떻게 할지"를 안 정했다. 만든 쪽이
  그 자리를 스스로 정해 "아무것도 안 띄운다"를 골랐다. 그 선택이 보고에 없었고, 판정하는 쪽이
  코드를 읽다가 찾았다.
- 같은 일에서 낡은 시험 하나가 깨졌다. 고칠 파일 목록 밖이라 손을 못 댔는데, 그 사실도 보고에
  없었다. 역시 판정하는 쪽이 찾았다.

**둘 다 자율이 과해서 난 것이 아니다.** 스스로 정한 것은 정해야 만들 수 있는 것이었고, 못 고친
것은 목록이 막은 것이다. 빠진 것은 **말해 주는 일**이다.

지금 만든 쪽이 남기는 보고에는 무엇을 바꿨는지, 왜 바꿨는지, 어느 파일을 건드렸는지가 들어간다.
**스스로 내린 판단과 하지 않기로 한 일을 적는 칸이 없다.**

## Actions

- [W-00000169](W-00000169.md) — 자율과 보고의 계약을 결정으로 남기고 철학 문서를 맞춘다
  (설계 · claude)
- [W-00000170](W-00000170.md) — 실행하는 쪽에 주는 지시와 보고 형식에 그 계약을 싣는다
  (구현 · codex)

## User value

만든 쪽이 무엇을 자기가 정했고 무엇을 안 했는지 보고에서 바로 읽힌다. 지금은 판정하는 쪽이
코드를 다 읽어야 알아낼 수 있고, 놓치면 아무도 모른다.

## Scope

### Included

- 실행하는 쪽의 자율과 보고를 정하는 결정 하나.
- 그 계약을 실행하는 쪽에 주는 지시와 보고 형식에 싣는 일.
- 철학 문서에서 지금 이와 반대로 적힌 문장을 고치는 일.

### Excluded

- 고칠 파일 목록으로 막는 것을 푸는 일. 그대로 둔다 — 목록 밖은 하지 않고 보고하는 것이 계약이다.
- 보고를 안 하면 막는 검사. 손으로 몇 번 굴려 보고 정한다.

## Risks

- 보고 칸이 늘면 만든 쪽이 형식을 어길 확률도 는다. 지금도 보고 형식을 못 맞춰 실패한 적이 있다.
- 판정하는 쪽이 그 칸을 안 읽으면 값이 없다. 판정에 주는 지시도 같이 봐야 한다.

## Success criteria

- 결정 하나가 자율과 보고를 다 정하고, 층이 둘이라는 것이 읽힌다.
- 만든 쪽에 주는 지시가 그 계약을 그대로 말한다.
- 보고 형식에 스스로 정한 것과 하지 않은 것을 적는 칸이 있다.
- 철학 문서에 이와 반대되는 문장이 없다.
- 사람이 겪는 결과: 보고만 읽고도 "만든 쪽이 무엇을 자기 판단으로 정했는지" 알 수 있다.

## Next action

W-00000169 를 시작한다. 결정 내용은 2026-07-31 논의에서 이미 합의됐다.

## Progress

## Verification

### Executed at close — 2026-07-31

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
