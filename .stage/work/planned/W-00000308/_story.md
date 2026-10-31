---
id: W-00000308
title: worktree 진입 판정 수정(W-00000304)을 담은 stage 패치를 출시하고 설치본을 업데이트한다
kind: release
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/, stage/.codex-plugin/, .stage/
---

# W-00000308 worktree 진입 판정 수정(W-00000304)을 담은 stage 패치를 출시하고 설치본을 업데이트한다

## Purpose

W-00000304의 훅 수정이 설치된 Claude Code 세션에 적용되도록 stage 패치를 출시하고 설치본을 업데이트한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage 매니페스트 두 개의 버전이 0.63.4보다 높고, CHANGELOG의 그 버전 절에 worktree 진입 판정 수정 항목이 있다
- claude plugin update stage@noory-ai 와 재시작 뒤, 원래 checkout에서 시작해 worktree로 들어간 Claude 세션이 그 worktree의 .stage 카드를 등록 게이트에 막히지 않고 고친다(다시나에서 확인)
- 같은 세션에서 그 worktree에 만든 승격 intent가 그 worktree의 `.stage/official/` 편집을 허락한다. 다시나 DE-00000005 승격으로 확인한다. 0.62.0에서는 훅이 원래 checkout에서 intent를 찾아 막혔다(2026-11-01).
- 출시 뒤 W-00000304를 리뷰 대기 목록에서 보관한다

## Next action

1. main에서 `python3 stage/scripts/release_plugin.py stage --bump patch`로 출시하고 커밋·push한다. 루트 `CLAUDE.md`의 Plugin Changes 절이 출시 절차를 소유한다.
2. 마켓플레이스가 로컬 checkout(`~/Workspace/repo/noory-ai`)이므로 그 checkout을 최신으로 맞춘 뒤 `claude plugin update stage@noory-ai`를 돌리고 Claude Code를 다시 시작한다.
3. 다시나 세션에서 worktree에 들어가 `.stage` 카드 편집이 통과하는지 확인한다. 이때 원래 checkout의 `.stage`에는 열린 작업이 없어야 한다. 열린 작업이 있으면 이전 판정에서도 통과하기 때문이다.
4. W-00000304를 `stage-archive`로 보관한다.
