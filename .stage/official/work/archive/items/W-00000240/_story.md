---
id: W-00000240
title: stage 0.61.0 을 배포한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000240
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000240 stage 0.61.0 을 배포한다

## Purpose

로드맵 결정이 공식 자리에 바로 쓰이는 변경과 닫기 기준 감사가 아직 저장소에만 있어서 설치된 플러그인에는 안 닿으므로, 0.61.0 으로 내보내 실제로 불러와지는지 확인한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 0.61.0 이 변경 기록과 두 매니페스트에서 같고, 그 커밋이 원격에 올라갔고, 새 버전이 실제로 불러와지는 것이 관측되었다

## Next action


## Related truth


## Progress

버전이 맞고, 올라갔고, 실제로 불러와지는 것을 봤다.

- `stage/CHANGELOG.md` 의 `## 0.61.0 — 2026-08-07`, `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json` 셋 다 `0.61.0`.
- `5e893898 chore(stage): release 0.61.0` 이 `main` 에 올라갔다.
- `~/.claude/plugins/installed_plugins.json` 의 `stage@noory-ai` 가 `0.61.0`,
  설치 위치가 `~/.claude/plugins/cache/noory-ai/stage/0.61.0`. 그 복사본의
  `scripts/audit_stage.py` 가 오늘 더한 `ROADMAP010` 을 담고 있다.

**갱신하는 것은 `/plugin` 이다.** 배포 직후엔 `0.43.8` 이었고 `/reload-plugins` 를 두 번
돌려도 안 바뀌었다. `/plugin` 을 연 뒤에 `0.61.0` 이 됐다.

## Next action

없음. 닫는다.

## Verification


### Executed at close — 2026-08-07

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
```

## Retrospective


## Promotion decision
