---
id: W-00000128
title: 병렬 실행이 안전하게 멈추고 되돌아온다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000128 병렬 실행이 안전하게 멈추고 되돌아온다

## Purpose

W-00000125 가 병렬 실행을 열었지만 멈추는 자리와 되돌리는 자리가 비어 있다. 다섯을 닫는다. (1) claude venue 검증 구멍 — probe 가 CLAUDE_PROJECT_DIR·PROJECT_ROOT 를 지우고 훅을 부르는데, 훅은 그 변수가 있으면 payload cwd 보다 먼저 쓴다. 지우지 말고 트리와 같아야 한다고 주장해야 그 자리가 계약이 된다. (2) 실행자 동시 개수에 상한도 타임아웃도 없다 — 카드 10개면 실행자 10개. (3) 본 체크아웃이 더러우면 트리가 그것을 못 보는데 검사도 경고도 없다. (4) 드라이버 실패로 남은 트리를 거두는 명령이 없어 사람이 손으로 git worktree remove 를 해야 한다(O-00000007 과 같은 모양). (5) 없는 카드 ID 를 넣어도 트리를 먼저 만들고 나서 실패한다. 함께 정리 경로를 실제 트리로 고정하는 테스트를 넣는다.

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
