---
id: W-00000301
title: worktree에 들어간 Claude 세션에서 훅이 그 worktree를 작업 루트로 판정하게 한다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_worktree_workspace_root.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000301
promotion: pending
review: pending
scope: stage/hooks/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs: DE-00000084
---

# W-00000301 worktree에 들어간 Claude 세션에서 훅이 그 worktree를 작업 루트로 판정하게 한다

## Purpose

Claude Code 세션이 같은 저장소의 linked worktree로 들어가도 훅이 원래 checkout을 작업 루트로 잡아 worktree의 .stage 편집과 작업 등록을 막는 것을 고친다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Given 같은 저장소의 linked worktree에 들어간 Claude 세션(훅 입력 cwd는 worktree 안, CLAUDE_PROJECT_DIR는 원래 checkout), When 그 worktree의 파일을 편집하면, Then 훅은 그 worktree를 작업 루트로 판정한다: worktree의 .stage/ 편집은 원래 checkout에서처럼 governed가 아니고, 열린 작업 항목은 worktree의 .stage/에서 찾는다
- 드라이버가 고정한 환경, CLAUDE_PROJECT_DIR가 없고 cwd만 있는 Codex 훅, worktree 밖의 cwd, 다른 저장소의 worktree에서는 작업 루트 판정이 지금과 같다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
