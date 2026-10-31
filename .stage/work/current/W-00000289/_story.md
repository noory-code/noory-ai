---
id: W-00000289
title: codex 명령이 설치된 컴패니언 스크립트를 찾아 쓴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_codex_companion.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/codex_companion.py, stage/scripts/tests/test_codex_companion.py, .stage/settings.json, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000079
---

# W-00000289 codex 명령이 설치된 컴패니언 스크립트를 찾아 쓴다

## Purpose

codex 플러그인 버전이 바뀌거나 다른 컴퓨터에서 돌려도 드라이버·리뷰 명령이 말없이 깨지지 않게 한다.

## Actions

- 지금 동작: `.stage/settings.json` 의 codex 실행·리뷰·프로필·회수 명령 일곱 곳이
  `/Users/woogis/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs` 를 직접
  부른다. 다른 컴퓨터·클라우드에서는 돌지 않고, codex 플러그인이 1.0.6 이 아닌 버전으로 바뀌면
  모든 codex 리뷰와 실행이 깨진다.
- `stage/scripts/codex_companion.py` 가 실행 때 컴패니언 스크립트를 찾아 `node` 로 돌린다. 찾는 순서는
  `STAGE_CODEX_COMPANION` 환경 변수, Claude Code 가 `~/.claude/plugins/installed_plugins.json` 에 적은
  `codex@openai-codex` 설치 경로, 플러그인 캐시의 가장 높은 버전이다.
- 일곱 명령이 그 스크립트를 부르게 바꾼다. 회수 명령은 Node 안에서 `status`·`cancel` 을 부르는
  자리를 같은 스크립트로 바꾼다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

codex 플러그인을 업데이트하거나 다른 컴퓨터·클라우드에서 열어도 리뷰와 실행이 그대로 돈다. 깨지면
무엇을 찾았는지 적힌 오류로 바로 드러난다.

## Scope

### Included


### Excluded

- codex 플러그인을 클라우드에 설치하는 일.
- Stage 템플릿(`settings.jsonc`) — 템플릿은 이 경로를 담지 않는다.

## Risks

- `installed_plugins.json` 의 형식은 Claude Code 가 정한다. 이 세션에서 확인한 V2 형식(`plugins` 아래
  플러그인 ID 마다 `scope`·`installPath` 를 담은 항목 목록)을 따르고, 읽지 못하면 캐시로 넘어간다.
- 클라우드에는 codex 가 없어 고친 명령이 실제 codex 로 도는지는 여기서 확인할 수 없다(DE-00000079).

## Success criteria

- settings.json 의 codex 명령 일곱 곳이 특정 사용자 홈과 플러그인 버전을 담은 경로를 쓰지 않는다는 것을 테스트가 확인한다
- codex 플러그인 버전이 바뀌어도 명령이 설치된 컴패니언 스크립트를 찾아 실행한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
