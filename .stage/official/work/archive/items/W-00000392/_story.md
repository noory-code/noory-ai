---
id: W-00000392
title: 릴리스된 변경 기록 절에 나중에 끼어든 줄을 찾는다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000392
promotion: not_applicable
review: passed
scope: stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,stage/scripts/tests/test_changelog_union.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000392 릴리스된 변경 기록 절에 나중에 끼어든 줄을 찾는다

## Purpose

합친 뒤 이미 릴리스된 버전 절에 들어간 줄을 사람이 손으로 비교하지 않아도 명령 하나가 알려 준다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- release_plugin.py 의 점검이 각 릴리스 절을 그 릴리스 커밋이 쓴 내용과 비교해 더해진 줄을 출력하고 실패로 끝나는 시험이 있고 통과한다
- 끼어든 줄이 없으면 점검이 통과한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: release_plugin.py gained a --check-released mode that compares each released changelog section with the section its release commit wrote, lists the lines it gained under their heading, and exits 1 when there are any and 0 otherwise; tests cover both outcomes and the union-merge scenarios now use the check instead of a by-hand comparison.
Why: a line a card adds to the old Unreleased section can land under a released heading in a conflict-free merge, and finding it took a manual comparison with the release commit (W-00000392 purpose).
Decisions made: --check-released is a mode mutually exclusive with --bump; the release commit is the oldest non-merge commit whose diff adds the exact heading line, read from one git log -p and one git cat-file --batch process; blank lines are ignored and repeated lines are counted; headings no commit added (uncommitted, or written while resolving a merge) are listed as not checked and do not fail the check; edits to an existing line in a released section are reported as added lines; release_plugin.py is kept as one module at 515 lines rather than split, because the split would add a file outside the card's scope.
Work not done: None
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6PoF1nN6ehAWA4GPgD)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w392-release-section-check` 의 2fc471ca 까지를 squash 했다(17063278).
- 성공 기준 1, 2: `test_release_plugin.py` 11개(새 시험 3개: 더해진 줄을 출력하고 실패, 바뀌지 않으면 통과, `--bump` 와 함께
  쓸 수 없음)와 `test_changelog_union.py` 5개가 통과한다.
- 실제 저장소(1,205 커밋 클론)에서 `release_plugin.py <plugin> --check-released`: plainly, rag, evonest, flutter-cask,
  pencil_m3_flutter 는 통과(0). stage 는 실패(1)하고 0.51.0, 0.49.0, 0.43.5 세 절의 항목 넷을 출력했다. 0.51.0 의 항목은
  커밋 97563cc4("record the working-directory fix in the 0.51.0 entry")가 릴리스 뒤에 일부러 더한 것이다.
- 메인 세션이 다시 돌린 검사: scripts 전체 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 5 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
