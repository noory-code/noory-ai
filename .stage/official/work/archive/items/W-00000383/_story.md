---
id: W-00000383
title: 옛 목록 파일이 남은 프로젝트를 옮길 때 그 파일을 지운다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000383
promotion: not_applicable
review: passed
scope: stage/scripts,stage/CHANGELOG.md
promotes:
decision_refs:
reserved_ids: DE-00000095
---

# W-00000383 옛 목록 파일이 남은 프로젝트를 옮길 때 그 파일을 지운다

## Purpose

active.md, review.md, planned/index.md 가 남은 프로젝트를 새 버전으로 옮기면 그 파일이 지워져 감사 경고 INDEX007 이 남지 않는다

## Actions


## User value

W-00000377(DE-00000091)이 세 목록 파일을 없앴다. 이미 그 파일이 있는 다른 프로젝트는 새 버전에서도
파일이 그대로 남고, 감사가 파일마다 경고 INDEX007("지워라")을 낸다. 이관 스크립트(v3→v4, v4→v5)는 고치지 않았다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 세 목록 파일이 있는 프로젝트를 옮기면 세 파일이 지워지고 감사가 INDEX007 을 내지 않는다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: The v5 migration step deletes the three retired work lists inside its journaled transaction (journal key removed_work_lists, restored by --abort from the snapshot) and lists them in --dry-run; it no longer rewrites links in those lists or appends review rows; migrate_stage.py on a project already at schema v5 deletes leftover copies (dry run lists them) and otherwise still reports no migration needed; tests cover v4-to-v5, v3-to-v5, already-v5, dry run, abort, and that the audit then reports no INDEX007.
Why: The lists restate card status and no command updates them (DE-00000091), so a migrated project should not keep them or carry INDEX007 warnings.
Decisions made: Deletion lives only in the v5 step, because the v3-to-v4 path always continues into it and a v4 project would otherwise keep the files; a project already at schema v5 also has the files deleted on the next migrate_stage.py run, because W-00000377 kept schema_version at 5 and those projects would never reach the v5 step; files are deleted without content comparison, because they hold no fact a card does not hold; the project's own .stage/index.md routing rows are not rewritten, because the audit does not flag them and they belong to the project; no decision record was written for these choices.
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6PfSTY9kta6NEXV8UR)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w383-drop-old-lists` 의 e5d73bad 를 메인 세션 브랜치에 squash 했다(024cf7f3).
- 메인 세션이 다시 돌린 검사: scripts 840개 통과, hooks 통과, 감사 오류 0건.
- 메인 세션이 따로 확인했다: 세 목록 파일을 넣은 v5 프로젝트에서 감사가 INDEX007 을 3건 냈고, `migrate_stage.py` 뒤에는
  세 파일이 지워지고 INDEX007 이 0건이었다.
- 이미 schema v5 인 프로젝트에서도 지우는 것을 사용자가 2026-11-22 에 확인했다("네 진행해주세요").

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_schema_v5_migration.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_migrate_stage*.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS)
