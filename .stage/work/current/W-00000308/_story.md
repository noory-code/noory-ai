---
id: W-00000308
title: worktree 진입 판정 수정(W-00000304)을 담은 stage 패치를 출시하고 설치본을 업데이트한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/, stage/.codex-plugin/, .stage/
promotes:
decision_refs:
---

# W-00000308 worktree 진입 판정 수정(W-00000304)을 담은 stage 패치를 출시하고 설치본을 업데이트한다

## Purpose

W-00000304의 훅 수정이 설치된 Claude Code 세션에 적용되도록 stage 패치를 출시하고 설치본을 업데이트한다

## Actions
최신 main에서 별도 브랜치를 만들고 start_work.py로 카드를 시작합니다. release_plugin.py로 패치 버전을 올린 뒤 hooks·scripts 전체 검사와 감사를 실행하고 PR을 엽니다. 사용자가 설치 결과를 확인할 때까지 종료하지 않습니다.

## User value
설치된 Stage에서도 세션이 들어간 worktree의 카드와 승격 intent를 올바르게 읽도록 합니다.

## Scope

### Included
- 누적된 Stage 변경 기록과 두 호스트 매니페스트를 0.63.5로 맞춥니다.
- 검사 결과와 사용자에게 남은 설치·동작 확인 절차를 기록합니다.

### Excluded
- 이번 세션에서 /plugin 설치, Claude 재시작, 사용자 환경의 설치 버전 확인을 대신하지 않습니다.
- 릴리스 PR을 병합하거나 카드를 닫지 않습니다.

## Risks
자동 검사가 통과해도 설치본이 새 버전으로 바뀌었다는 뜻은 아닙니다. 원래 checkout에 열린 작업이 있으면 예전 등록 게이트도 통과할 수 있으므로 사용자 확인 시 이 조건을 구분해야 합니다.

## Success criteria

- stage 매니페스트 두 개의 버전이 0.63.4보다 높고, CHANGELOG의 그 버전 절에 worktree 진입 판정 수정 항목이 있다
- claude plugin update stage@noory-ai 와 재시작 뒤, 원래 checkout에서 시작해 worktree로 들어간 Claude 세션이 그 worktree의 .stage 카드를 등록 게이트에 막히지 않고 고친다(다시나에서 확인)
- 같은 세션에서 그 worktree에 만든 승격 intent가 그 worktree의 `.stage/official/` 편집을 허락한다. 다시나 DE-00000005 승격으로 확인한다. 0.62.0에서는 훅이 원래 checkout에서 intent를 찾아 막혔다(2026-11-01).
- 출시 뒤 W-00000304를 리뷰 대기 목록에서 보관한다

## Next action

1. 이 세션은 릴리스 PR을 연 뒤 멈춥니다. PR 병합은 아직 남아 있습니다.
2. PR 병합 뒤 로컬 마켓플레이스 checkout을 최신으로 맞춥니다. 사용자가 `/plugin`에서 Stage를 업데이트하고 재시작한 뒤 설치된 버전이 0.63.5인지 확인합니다.
3. 사용자가 다시나 세션에서 worktree에 들어가 `.stage` 카드 편집이 통과하는지 확인합니다. 원래 checkout에는 열린 작업이 없어야 합니다. 같은 세션에서 worktree의 승격 intent로 DE-00000005의 공식 기록 편집이 허용되는지도 확인합니다.
4. 사용자가 설치 버전과 동작을 확인했다고 알려 준 뒤 남은 회고·종료 절차와 W-00000304 보관을 진행합니다. 확인 전에는 이 카드를 닫지 않습니다.

## Related truth

DE-00000054와 `.stage/operations/verification.md`에 따라 새 버전이 실제로 불러와졌음을 확인해야 release 검증을 통과합니다. 루트 CLAUDE.md가 릴리스 도구와 두 매니페스트의 동기화를 정합니다. PR #18이 추가한 승격 권한 확인 기준도 유지합니다.

## Progress

2026-11-01: 클라우드 PR #19를 병합한 main에서 `codex/w308-stage-patch`를 만들었습니다. start_work.py로 기존 scope 그대로 시작하고 release_plugin.py를 한 번 실행해 0.63.5를 준비했습니다. 사용자 승인 뒤 PR #18도 병합하고 그 main 위로 릴리스 커밋을 옮겼습니다. 추가 변경은 성공 기준 한 줄뿐이며 제품 코드는 같습니다.

설정에서 파생된 venue는 claude로 유지합니다. 이번 릴리스 준비와 검사는 사용자가 이 로컬 Codex 세션에 직접 지시해 실행했습니다. Claude가 실행했다고 기록하지 않습니다. 설치·재시작과 실제 버전 확인은 사용자가 맡습니다.

### Executor report — 2026-11-01

What changed: 릴리스 도구가 두 매니페스트와 CHANGELOG를 0.63.5로 맞췄습니다. 기존 카드를 시작하고 설치 확인이 남았음을 기록했습니다.
Why: worktree 등록·승격 판정 수정을 설치할 수 있는 패치로 준비하되 설치 전 상태를 완료로 보고하지 않습니다.
Decisions made: main에 직접 push하지 않고 릴리스 PR만 엽니다. 사용자의 확인 전에는 status: active, verification: pending을 유지합니다. 공식 정책을 승격하지 않으므로 promotion은 not_applicable입니다. PR #18의 추가 기준을 유지합니다. 제품 범위 밖 수정은 없습니다. 검사 출력은 /tmp/w308-hooks.log, /tmp/w308-scripts.log, /tmp/w308-audit.log에 썼으며 카드의 scope 밖인 임시 증거 파일입니다.
Work not done: 릴리스 PR 병합, /plugin 업데이트, 재시작, 설치 버전과 worktree 편집·승격 확인, W-00000304 보관, 회고와 카드 종료는 남아 있습니다.
Changed paths (JSON): [".stage/work/active.md", ".stage/work/planned/index.md", ".stage/work/planned/W-00000308/_story.md", ".stage/work/current/W-00000308/_story.md", "stage/CHANGELOG.md", "stage/.claude-plugin/plugin.json", "stage/.codex-plugin/plugin.json"]
Review dispositions (JSON): []

## Verification

2026-11-01 로컬 실행 결과:

- `python3 stage/scripts/release_plugin.py stage --bump patch`: 종료 코드 0, `Released stage 0.63.5`.
- `python3 -m unittest discover -s stage/hooks/tests -q`: 393개 통과, 종료 코드 0.
- `python3 -m unittest discover -s stage/scripts/tests -q`: 719개 통과, 종료 코드 0.
- `python3 stage/scripts/audit_stage.py`: 오류 0개, 기존 경고 32개.
- `git diff --check`: 통과.

두 매니페스트의 버전과 CHANGELOG 절은 0.63.5이며 worktree 진입 판정 수정 항목을 포함합니다. 설치 확인과 실제 worktree 동작은 미실행이므로 release 전체 검증은 pending입니다.

## Retrospective

사용자가 설치 버전과 동작을 확인한 뒤 작성합니다. 아직 완료하지 않았습니다.

## Promotion decision

not_applicable — 이 릴리스 카드는 공식 결정이나 정책 승격을 소유하지 않습니다.
