---
id: W-00000410
title: 지난 카드들의 보고에 남은 작은 고침 넷을 넣는다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts,stage/hooks,stage/skills,.github/workflows/stage.yml,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000410 지난 카드들의 보고에 남은 작은 고침 넷을 넣는다

## Purpose

지난 카드들의 보고에만 남아 있던 작은 고침 넷이 코드와 CI 에 들어가서, 같은 후보가 다음 보고에 다시 오르지 않는다 (O-00000061)

## Actions


## User value


## Scope

### Included


### Excluded

- 매번 같은 규칙 문장을 줄이는 일(M-00000006 의 (가)가 판정한다). 넷째 기준이 그것 없이는 채워지지 않으면 채워지지 않는다고 보고한다.
- 다른 프로젝트(Dasina)의 설정을 고치는 일, 규칙 후보의 첫 정리, 토론·계획 세션의 브리핑, 스킬 줄이기.


## Risks


## Success criteria

- CI 가 release_plugin.py --check-released --since 0.67.0 을 돌려, 릴리스된 변경 기록 절에 뒤늦게 더해진 줄이 있으면 실패한다
- 쓰인 기록 번호를 세는 코드가 한 곳에 있고 번호를 고르는 곳들이 그것을 쓴다
- model_fallbacks 를 선언했는데 그 명령에 $STAGE_MODEL 이 없으면 audit 가 경고한다
- 세션 색인이 같은 카드를 두 번 싣지 않고, 그렇게 줄어든 자리로 이 저장소의 결정 제목이 모두 실린다

## Next action

작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.


## Related truth

- O-00000061 의 "그 전 카드들에서 나온 것", W-00000409 의 후속 후보(같은 카드를 두 번 싣는 약 550자), W-00000392 와 W-00000396(`--check-released`, `fetch-depth: 0` 이 필요하다), W-00000386(`model_fallbacks`).
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 그 목록에서 옮겨 적었다. 사용자가 고른 묶음이 아니다.


## Sessions

- session_018VXR6QTeKjAAj8MoTZaY5B — work — 2026-11-23 — opened from the index: not reported yet


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 340510d1 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B (`claude/w410-small-fixes`)를 띄웠다. 브리핑이 색인을 달고 12,613바이트가 되어, 첫 메시지에 본문을 옮기지 않고 세션이 같은 명령으로 브리핑을 스스로 내어 읽게 했다.


## Verification
