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
retrospective: completed
retrospective_ref: R-00000410
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

작업 세션이 둘째 기준의 고침을 보고하면 가져와 닫기 리뷰를 다시 돌린다.


## Related truth

- O-00000061 의 "그 전 카드들에서 나온 것", W-00000409 의 후속 후보(같은 카드를 두 번 싣는 약 550자), W-00000392 와 W-00000396(`--check-released`, `fetch-depth: 0` 이 필요하다), W-00000386(`model_fallbacks`).
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 그 목록에서 옮겨 적었다. 사용자가 고른 묶음이 아니다.


## Sessions

- session_018VXR6QTeKjAAj8MoTZaY5B — work — 2026-11-23 — opened from the index: O-00000061


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 340510d1 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B (`claude/w410-small-fixes`)를 띄웠다. 브리핑이 색인을 달고 12,613바이트가 되어, 첫 메시지에 본문을 옮기지 않고 세션이 같은 명령으로 브리핑을 스스로 내어 읽게 했다.


- 2026-11-23 작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B 가 5150d29b 를 보고했다. 성공 기준 1-4 를 주장했다(넷째는 여유 40자). 지휘 세션이 squash 커밋에서 scripts 950, hooks 483 통과와 audit 오류 0 을 다시 확인했다. 범위 밖 변경은 `stage/docs/SCHEMA_V5.md` 한 곳이다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: 얕은 체크아웃에서 `--check-released` 를 거부하는 것, 트리에 번호와 상태가 남는 것.
- 2026-11-23 닫기 리뷰가 둘째 기준을 반려했다: `register_work.existing_numbers` 와 `migrate_stage.next_work_number` 가 아직 따로 센다. 작업 세션에 돌려보냈다.
- Follow-up candidate: 색인의 여유가 40자다. 규칙 문장을 줄이거나 상한을 다시 정한다(M-00000006 의 (가)).
- Follow-up candidate: `register_work` 의 옛 구조 폴더 훑기와 `migrate_stage.next_work_number` 를 `used_numbers` 아래로 모으거나, 옛 구조는 범위 밖이라고 적는다.
- Follow-up candidate: `review.strengths` 명령의 TIER007 은 설정이 그 강도가 어느 venue 로 도는지 말해야 가능하다.

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Review at close 2026-11-23 by claude_review_companion: rejected (1 PASS ran, 2 FAIL read, 3 PASS ran, 4 PASS ran)
