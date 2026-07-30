---
id: W-00000150
title: stage 0.55.1 릴리스
kind: ops
venue: claude
milestone:
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000150
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs: DE-00000045
---

# W-00000150 stage 0.55.1 릴리스

## Purpose

미출시 절에 쌓인 고침 넷 중 셋이 **다른 프로젝트를 지금 막고 있다.** 릴리스가 늦어지는 만큼 그
프로젝트가 우회로 버틴다.

- v4 프로젝트가 자기 기존 결함 때문에 v5 마이그레이션에 막힌다 — novel-workspace 는 kind 기준 네
  줄을 손으로 추가해 넘어갔고, 우회를 모르는 프로젝트는 갇힌다.
- 보관된 v5 카드를 게이트가 다시 못 연다 — novel-workspace 가 감사 오류 하나를 못 고치고 남겨 뒀다.
- 설명 문서 갱신의 기본 실행이 프로젝트가 쌓은 내용을 지운다 — 이미 관측 22행을 잃었다.

셋 다 계약을 넓히지 않는 버그 수정이므로 patch 다.

## Actions

- `python3 stage/scripts/release_plugin.py stage --bump patch` — 미출시 절에 제목을 달고, 매니페스트
  둘의 버전을 올리고, 새 빈 미출시 절을 연다.
- 릴리스 커밋과 push 를 한 걸음으로 한다(루트 `CLAUDE.md` 의 Plugin Changes 절).
- push 뒤 코덱스 캐시를 다시 맞춘다 — 버리는 호출 한 번 뒤
  `~/.codex/plugins/cache/noory-ai/stage/<버전>/hooks/stage_guard.py` 가 있는지 확인한다
  (P-00000001).

## Scope

`stage/CHANGELOG.md`, `stage/.claude-plugin/plugin.json`, `stage/.codex-plugin/plugin.json`.

**안 하는 것**: 코드 변경. 릴리스는 이미 병합된 것을 내보내는 일이다.

## Success criteria

- `stage/CHANGELOG.md` 의 맨 위 절이 `## 0.55.1 — 2026-07-30` 이고 그 아래 항목 넷이 그대로 있다.
- 매니페스트 둘 다 `0.55.1` 이고 서로 같다.
- 새 빈 `## Unreleased` 절이 그 위에 선다.
- 릴리스 커밋이 origin/main 에 올라가 있다.
- 코덱스 캐시에 `0.55.1` 훅이 실재한다. 이것이 안 되면 다음 codex 위임이 옛 스키마로 돈다.

## Related truth

- DE-00000045 — 이 카드의 venue 예외. 릴리스 예외가 **두 번째**이고, 세 번째가 오면 정책을 고친다.
- DE-00000041 — 첫 번째 예외(W-00000137, 소진됨).
- W-00000124 — 카드가 버전을 안 올리고 릴리스가 정한다는 규칙을 세운 카드.
- P-00000001 — 코덱스 플러그인 캐시가 새 버전으로 안 갱신되면 위임이 옛 훅으로 돈다.

## Progress

- `release_plugin.py stage --bump patch` 로 미출시 절에 `0.55.1 — 2026-07-30` 제목을 달고 매니페스트
  둘을 올렸다. **명령은 커밋·push 를 안 한다** — 사람이 이어서 했다(`6274bf46`).
- push 뒤 버리는 코덱스 호출로 마켓플레이스를 다시 맞췄다.

## Verification

- `stage/CHANGELOG.md` 맨 위가 빈 `## Unreleased`, 그 아래 `## 0.55.1 — 2026-07-30` 에 항목 넷.
- 매니페스트 둘 다 `0.55.1`.
- `3a6776c0..6274bf46` 이 origin/main 에 올라갔다.
- 코덱스 캐시에 `~/.codex/plugins/cache/noory-ai/stage/0.55.1/hooks/stage_guard.py` 실재 확인.
  사전 점검 스크립트도 `cache ok` 를 냈다.


### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000150](../../retrospectives/R-00000150.md) — 다른 프로젝트가 기다리는 고침은 릴리스가 늦은
만큼 값이 준다.

## Promotion decision

FINAL: not_applicable. 릴리스는 이미 병합된 것을 내보내는 일이고 승격할 산출물이 없다.
DE-00000045 는 소진성 허가라 DE-00000030 의 판정에 따라 `pending` 에 남는다.
