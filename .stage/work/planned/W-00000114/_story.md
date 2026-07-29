---
id: W-00000114
title: 계층 게이트가 카드 아닌 표면을 카드로 오판하지 않는다
kind: fix
venue:
milestone:
status: captured
priority: 1
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/hooks/, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
---

# W-00000114 계층 게이트가 카드 아닌 표면을 카드로 오판하지 않는다

## Purpose

수명 주기 폴더 루트의 index.md·README.md·_template.md 등 카드가 아닌 파일을 계층 게이트가 카드 모양 검사에 태워 도구 편집을 전부 거부한다(O-00000009). 계획 인덱스에 선언된 rejected 상태로 갈 길이 없다. 게이트가 카드 아닌 표면을 검사에서 빼거나 계획 카드 반려를 스크립트가 맡게 하고, 그 갈림의 근거를 남긴다. 끝나면 W-00000092 를 DE-00000039 의 판정대로 반려 처리한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
