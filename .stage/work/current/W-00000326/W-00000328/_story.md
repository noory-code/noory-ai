---
id: W-00000328
title: 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_model_tiers.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/stage_model_tiers.py, stage/hooks/stage_work.py, stage/skills/stage-work/, stage/scripts/start_work.py, stage/templates/project-stage/settings.json, stage/docs/SCHEMA_V5.md, stage/hooks/tests/test_model_tiers.py, stage/scripts/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000328 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다

## Purpose

일감을 등록하거나 시작할 때 설정의 등급 표가 고른 등급이 카드에 남게 한다

## Actions

하나의 구현 단위라 action 으로 나누지 않는다.

## User value

일감을 등록하는 사람이 모델을 따로 고르지 않아도 카드에 맞는 등급이 남는다. 나머지 story(드라이버·훅·감사)가 읽을 `tier:` 와 공용 모듈이 여기서 생긴다.

설계 SSOT: `.stage/work/current/W-00000326/W-00000327/_story.md` 의 `## Design` 중 "설정: model_tiers", "설정: tier_routing", "공용 모듈", "카드: frontmatter tier:" 를 먼저 읽는다.

## Scope

### Included

- `stage/hooks/stage_model_tiers.py` 새 공용 모듈: `model_tiers`·`tier_routing` 읽기, kind×크기로 등급 고르기, 등급과 venue 로 `model`·`effort` 꺼내기, 선언 순서로 등급 비교, 모델 별칭 비교(`[...]` 꼬리표 떼고 실제 id 에 별칭이 들어 있는지)
- `stage/hooks/stage_work.py` 의 `WorkItem` 에 `tier` 필드
- `register_work.py` 의 자동 등급과 `--tier`, `start_work.py` 의 빈 `tier:` 채우기
- 템플릿 `settings.json` 에 claude 칸만 채운 네 등급과 `tier_routing` (`"*": "standard"`)
- `stage/docs/SCHEMA_V5.md` 와 `stage/skills/stage-work/SKILL.md` 에 설정 모양·`tier:` 규칙
- 시험: `stage/hooks/tests/test_model_tiers.py`, 필요한 `stage/scripts/tests/` 시험
- `stage/CHANGELOG.md` 의 `## Unreleased` 한 줄 (매니페스트 버전은 바꾸지 않는다)

### Excluded

- 드라이버 환경 변수(W-00000329), Agent 훅(W-00000330), 감사(W-00000331)
- 이 저장소의 `.stage/settings.json`

## Risks

- 기존 카드 파서가 모르는 frontmatter 키를 거부하면 `tier:` 가 있는 카드가 깨진다. 파서와 감사의 허용 키 목록을 확인한다.
- `model_tiers` 가 없는 프로젝트의 등록 결과가 한 글자라도 바뀌면 안 된다.


## Success criteria

- model_tiers 와 tier_routing 을 둔 프로젝트에서 register_work.py 로 등록하거나 start_work.py 로 시작한 카드의 frontmatter 에 kind 와 크기로 고른 tier 가 적힌다
- --tier 로 등급을 직접 주거나 사람이 카드의 tier 를 고치면 그 값이 남고, 표에 없는 등급 이름은 등록이 거부된다
- model_tiers 가 없는 프로젝트에서 등록한 카드에는 tier 줄이 생기지 않는다

## Next action

드라이버가 Codex 실행기로 돌린다. 실행기는 W-00000327 의 설계를 읽고 `stage_model_tiers.py` 와 그 시험부터 만든다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
