---
id: W-00000240
title: stage 0.61.0 을 배포한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
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

버전은 맞고 올라갔다. 불러와지는 것은 아직 못 봤다.

- `stage/CHANGELOG.md` 의 `## 0.61.0 — 2026-08-07`, `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json` 셋 다 `0.61.0`.
- `5e893898 chore(stage): release 0.61.0` 이 `main` 에 올라갔다.
- 설치된 플러그인은 아직 `0.43.8` 을 들고 있다
  (`~/.claude/plugins/installed_plugins.json` 의 `stage@noory-ai`). 캐시가 따라오면 바뀐다.
  O-00000037 이 코덱스 쪽에서 같은 모양을 적었다 — 릴리스 직후엔 안 따라오고 나중에 스스로
  따라잡는다.

**그래서 못 닫는다.** 종류 `release` 의 통과 기준은 "새 버전이 실제로 불러와지는 것이
관측되었다"이고, 버전만 올라간 상태는 통과가 아니다(DE-00000054). 0.60.0 에서 이 자리를 한 번
틀렸다(O-00000039).

## Next action

다음 세션에서 설치된 버전을 다시 본다 — `~/.claude/plugins/installed_plugins.json` 의
`stage@noory-ai` 가 `0.61.0` 이면 회고 쓰고 닫는다. 며칠이 지나도 `0.43.8` 이면 무엇이
캐시를 되살리는지 모른다는 뜻이므로 O-00000037 에 클로드 쪽 실측을 더한다.

## Verification


## Retrospective


## Promotion decision
