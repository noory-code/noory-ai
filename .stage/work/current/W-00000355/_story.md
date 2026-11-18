---
id: W-00000355
title: stage 0.66.6 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000355
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000355 stage 0.66.6 을 낸다

## Purpose

자식 프로세스 출력을 UTF-8 로 읽는 고침과 회고 번호가 막히면 주인을 따라가는 고침이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 컴퓨터와 프로젝트가 그것을 쓸 수 있게 한다.

## Actions

없음. 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 옮긴다.

## User value

Windows 를 UTF-8 이 아닌 로캘로 쓰는 사람도 카드를 닫을 때 검사 출력이 증거에 남는다. 회고 번호를 예전에
차례로 매긴 프로젝트도 오래된 카드를 손으로 번호를 찾지 않고 닫을 수 있다.

## Scope

### Included

- 패치 버전을 올린다(0.66.5 → 0.66.6). 설정이나 훅이 새로 생기지 않았으므로 고침이다.
- 쌓인 변경 기록 한 묶음(W-00000352, W-00000353)에 그 버전 제목을 붙인다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- PR 로 main 에 합치고, 합친 뒤 `claude plugin list` 로 확인한다.

### Excluded

- 다른 플러그인 릴리스.
- W-00000352·W-00000353 의 닫기 리뷰. macOS 에서 따로 한다.

## Risks

- W-00000352·W-00000353 은 닫기 리뷰를 받기 전에 배포된다. 사용자가 머지와 릴리스를 먼저 하라고 정했다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.6 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 stage 를 0.66.6 으로 읽는다

## Next action

PR 을 머지한 뒤 `claude plugin list` 로 0.66.6 을 확인하고 닫는다.

## Related truth

- 사용자 결정(2026-11-18): "릴리스 진행하세요".

## Progress

- `python stage/scripts/release_plugin.py stage --bump patch`: "Released stage 0.66.6". 변경 기록에
  `## 0.66.6 — 2026-11-18` 제목이 붙고, 두 매니페스트가 0.66.6 이 됐다.
- PR #64 를 main 에 합쳤다(`169175d5`).

## Verification

- 맥북의 `claude plugin list`: `stage@noory-ai`, Version 0.66.6, Read from
  `/Users/woogis/Workspace/repo/noory-ai/stage`, enabled.
- `stage/.claude-plugin/plugin.json`, `stage/.codex-plugin/plugin.json` 둘 다 `"version": "0.66.6"`.

### Executed at close — 2026-11-18

```
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

$ claude plugin list
[exit 0]
... (142 earlier lines omitted)
    Status: ✔ enabled

  ❯ skill-creator@claude-plugins-official
    Version: e6143c9807a0
    Scope: user
    Status: ✘ disabled

  ❯ stage@noory-ai
    Version: 0.66.6
    Read from: /Users/woogis/Workspace/repo/noory-ai/stage
    Scope: user
    Status: ✔ enabled

  ❯ supabase@claude-plugins-official
    Version: 0.1.16
    Scope: project
    Status: ✘ disabled

  ❯ swift-lsp@claude-plugins-official
    Version: 1.0.0
    Scope: project
    Status: ✘ disabled

  ❯ typescript-lsp@claude-plugins-official
    Version: 1.0.0
    Scope: user
    Status: ✔ enabled

  ❯ ui-theme-designer@claude-plugins-official
    Version: 2.0.0
    Scope: user
    Status: ✘ disabled

Synced from claude.ai:

  ❯ cowork-plugin-management@synced
    Version: 0.2.2
    Path: /Users/woogis/.claude/plugins/synced/86ec35dd-b0f6-4feb-a326-b7072ead6eaf_3cab8a53-21f2-45b8-86ba-c3f338b0bed8/cowork-plugin-management~g2
    Status: ✔ loaded

```

## Retrospective

R-00000355 에 적었다.


## Promotion decision
