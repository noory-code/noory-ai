---
id: W-00000351
title: flutter-cask 와 pencil-m3-flutter 에 개발을 멈췄다고 표시하기
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000351
promotion: pending
review: not_required
scope: flutter-cask/README.md, flutter-cask/CHANGELOG.md, pencil_m3_flutter/README.md, pencil_m3_flutter/CHANGELOG.md, README.md, .claude-plugin/marketplace.json
promotes:
decision_refs:
---

# W-00000351 flutter-cask 와 pencil-m3-flutter 에 개발을 멈췄다고 표시하기

## Purpose

flutter-cask 와 pencil-m3-flutter 를 보는 사람이 개발이 멈췄다는 것과 그 이유를 바로 알게 한다.

## Actions

이 스토리는 문서 몇 줄만 바꾸므로 따로 나눈 액션이 없다.

## User value

두 플러그인을 설치하려는 사람이 앞으로 기능이 더해지지 않는다는 것을 먼저 알고 고를 수 있다.
7월 평가에서 멈추기로 정한 것이 어디에도 적혀 있지 않던 상태가 끝난다.

## Scope

### Included

- 두 플러그인의 README 맨 위에 개발을 멈췄다는 안내와 이유를 적는다.
- 두 플러그인의 CHANGELOG 에 `## Unreleased` 를 만들고 같은 내용을 적는다.
- 루트 README 의 두 절과 Claude Code 마켓플레이스의 두 설명에 같은 내용을 적는다.

### Excluded

- 코드를 지우지 않는다.
- 릴리스하지 않고 매니페스트도 바꾸지 않는다.
- 마켓플레이스에서 빼지 않는다. rag 와 같은 방식이다(W-00000348).

## Risks

- 표시가 한 곳이라도 빠지면 그곳을 본 사람은 아직 개발 중인 플러그인으로 안다.

## Success criteria

- 두 플러그인의 README, 루트 README 의 두 절, Claude Code 마켓플레이스의 두 설명 어디를 봐도 개발이 멈췄다는 것이 보인다.
- 코드를 지우거나 릴리스하지 않아서 이미 설치한 사람은 그대로 쓸 수 있다.

## Next action

닫는다.

## Related truth

- 2026-07-18 플러그인 평가: 두 플러그인은 "릴리스하지 않고, 지우지 않고, 멈춤을 표시한다"고 정했지만 표시하지 않았다.
- 사용자 결정(2026-11-17): "멈춤 표시부터".
- 같은 방식으로 rag 를 표시한 카드: W-00000348.

## Progress

- 커밋 `48db5717`: 두 README 맨 위, 두 CHANGELOG 의 새 `## Unreleased`, 루트 README 의 두 절, Claude Code
  마켓플레이스의 두 설명에 개발을 멈췄다고 적었다.
- 이유는 "2026년 3월 이후 기능 작업이 없다"로 적었다. 두 플러그인을 마지막으로 바꾼 커밋은 2026-07-12 이지만,
  그것은 모든 플러그인에 Codex 지원을 더한 일이고 기능 작업은 2026-03-20 이 마지막이다.
- pencil-m3-flutter 의 CHANGELOG 에는 H1 제목이 없어서, 저장소 규칙대로 파일 맨 앞에 `## Unreleased` 를 만들었다.
- 이 카드를 등록할 때 `--scope` 를 여섯 번 넘겼고, 여섯 경로가 모두 카드에 들어갔다. W-00000349 의 고침이
  실제 등록에서도 동작한다.
- `git add -A flutter-cask pencil_m3_flutter` 를 폴더 단위로 넘겨서 범위 넘음 알림에 두 폴더가 떴다. 실제로 바뀐
  파일은 모두 범위 안에 있다.

## Verification

- `python3 -m unittest discover -s tests -q`: 통과. 마켓플레이스 파일을 읽는 저장소 계약 테스트다.
- `python3 -m unittest discover -s plainly/tests -q`: 통과.
- `python3 -m json.tool .claude-plugin/marketplace.json`: JSON 이 깨지지 않았다.
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0.
- Codex 마켓플레이스 항목에는 설명 칸이 없어 표시하지 않았다. W-00000348 과 같은 이유다. 대신 README 두 곳에 표시가 있다.

## Retrospective

R-00000351 에 적었다.

## Promotion decision

not_applicable. 공식 기록으로 올릴 결정이 없다.
