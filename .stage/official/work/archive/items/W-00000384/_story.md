---
id: W-00000384
title: 릴리스와 변경 기록 줄 추가가 겹칠 때 union 병합 결과를 확인한다
kind: qa
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000384
promotion: not_applicable
review: passed
scope: stage/scripts/tests/test_changelog_union.py,stage/scripts/release_plugin.py,stage/CHANGELOG.md
promotes:
decision_refs:
reserved_ids: DE-00000096
---

# W-00000384 릴리스와 변경 기록 줄 추가가 겹칠 때 union 병합 결과를 확인한다

## Purpose

한 브랜치가 릴리스해서 Unreleased 를 버전 제목으로 바꾸고 다른 브랜치가 Unreleased 에 줄을 더한 뒤 합칠 때 변경 기록이 어떻게 되는지 안다

## Actions

- `stage/scripts/tests/test_changelog_union.py` 가 임시 저장소에서 `release_plugin.py` 로 실제 릴리스를 만들고, 카드
  브랜치와 두 방향으로 합친 결과를 글자 그대로 고정한다.
- 줄이 잘못된 절에 들어간 경우를 찾고 고치는 방법을 아래 `## Progress` 에 적는다.

## User value

W-00000377 서브세션이 남긴 질문이다. 루트 `.gitattributes` 가 모든 `CHANGELOG.md` 에 `merge=union` 을
건다. 릴리스는 `## Unreleased` 제목을 버전으로 바꾸고 새 `## Unreleased` 를 연다. 다른 브랜치가 같은 때 Unreleased 에
줄을 더하면 union 이 그 줄을 어느 절에 두는지 확인하지 않았다. GitHub 머지 버튼은 union 을 따르지 않는다(PR #90, #91).


## Scope

### Included

- union 을 건 경우와 걸지 않은 경우, 줄을 `## Unreleased` 맨 위에 더한 경우와 마지막 줄 뒤에 더한 경우, 두 합치는 방향.

### Excluded

- 잘못 놓인 줄을 자동으로 찾는 점검 도구. 후속 후보로 남긴다.
- 카드가 이미 있는 대기 줄을 고치는 경우(union 은 고치기 전과 후 줄을 모두 남긴다).

## Risks

- 시험은 이 컨테이너의 git 으로 확인했다. union 이 충돌한 양쪽을 쓰는 순서(합쳐지는 쪽이 먼저)는 git 의 동작이고
  Stage 가 정하지 않는다.

## Success criteria

- 두 브랜치를 git 으로 합친 결과가 시험으로 고정되어 있고, 줄이 잘못된 절에 들어가면 그 처리 방법이 카드에 적혀 있다

## Next action

## Related truth

## Progress

### 확인한 결과

릴리스는 대기 줄을 옮기지 않고 그 위에 새 `## Unreleased` 와 버전 제목을 끼워 넣는다. git 은 카드가 더한 줄을 이웃한
줄로 자리를 잡는데, 그 이웃이 이제 버전 제목 아래에 있다. 어떤 경우에도 머지는 실패하지 않는다(union 을 건 경우).

| 카드가 줄을 더한 자리 | 합치는 방향 | union | 결과 |
|---|---|---|---|
| `## Unreleased` 맨 위 (이 저장소의 관례) | 카드 → 릴리스 브랜치 | 건다 | 줄이 릴리스된 절 맨 위에 들어간다. 새 `## Unreleased` 는 비어 있다. |
| `## Unreleased` 맨 위 | 릴리스 브랜치 → 카드 브랜치 | 건다 | 줄은 `## Unreleased` 에 남는다. 버전 제목 앞의 빈 줄이 빠진다. |
| `## Unreleased` 맨 위 | 어느 쪽이든 | 걸지 않는다 (GitHub 머지 버튼) | 충돌한다. |
| 마지막 대기 줄 뒤 | 어느 쪽이든 | 걸든 안 걸든 | 충돌 없이 줄이 릴리스된 절에 들어간다. |

맨 위 경우에 방향이 갈리는 이유: 두 쪽이 같은 자리에 줄을 끼워 넣어 충돌하고, union 은 합쳐지는 쪽(ours)의 줄을 먼저
쓴다. 마지막 줄 뒤 경우는 충돌이 아니므로 union 과 무관하다. 즉 잘못 놓이는 문제는 union 이 만든 것이 아니라 릴리스가
제목만 끼워 넣는 방식과 줄 단위 3-way 머지에서 온다.

### 처리 방법

```yaml
when: 합치는 두 쪽 중 한쪽에만 있는 `## x.y.z — date` 제목이 어떤 플러그인의 CHANGELOG.md 에 있다
check:
  - 머지 결과에서 그 버전 절의 줄을, 그 제목을 만든 릴리스 커밋의 같은 절과 비교한다
    (`git log -1 --format=%H -S "## x.y.z — date" -- <plugin>/CHANGELOG.md` 로 커밋을 찾고 `git show <commit>:<plugin>/CHANGELOG.md`)
  - 머지 결과의 `## Unreleased` 와 버전 제목 사이에 빈 줄이 하나 있는지 본다
if: 버전 절에 릴리스 커밋에 없던 줄이 있다
then: 그 줄을 `## Unreleased` 아래로 옮기고 같은 머지(또는 바로 다음 커밋)에서 커밋한다
if: 빈 줄이 빠졌다
then: 빈 줄을 넣는다
order: 카드 브랜치에 릴리스된 기본 브랜치를 먼저 합친다(`.gitattributes` 의 안내와 같다). 맨 위에 더한 줄은 그러면 제 절에 남는다.
```

시험 `test_comparing_the_released_section_with_the_release_commit_finds_the_line` 이 이 비교로 줄을 찾고 옮기면 의도한
변경 기록이 되는 것을 고정한다.

### Executor report at close — 2026-11-22

```
What changed: Added stage/scripts/tests/test_changelog_union.py, which runs release_plugin.py in a throwaway repository with and without merge=union and pins the merge text in both directions: a line added first under Unreleased lands in the released section when the card is merged into the released branch, and stays queued without its blank line when the released branch is merged into the card branch; without union that case conflicts (GitHub's button); a line added after the last queued line lands in the released section in every direction with or without union; a fourth test pins the handling check (compare the released section with the release commit and move extra lines back) for both the top and the bottom line; added the stage/CHANGELOG.md note; wrote the result table and the handling procedure in the card's Actions, Scope, Risks, and Progress.
Why: The card's success criterion asks that the merge result be pinned by a test and that the handling of a misplaced line be written on the card.
Decisions made: release_plugin.py is unchanged, because no line-based release format makes git place a concurrent addition correctly (the queued lines never move, only a heading is inserted above them) and union resolves every conflict silently; the handling is a manual check written on the card instead of a new tool, and an automatic check is left as a follow-up; the misplacement is not caused by union (the bottom-line case misplaces with plain three-way merge too); the reserved DE-00000096 was not used, because the card adds no policy beyond the existing DE-00000091 and the handling procedure.
Work not done: No automatic detection of misplaced changelog lines; the .gitattributes comment and the release step in CLAUDE.md were not updated to point at the handling.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6RKC7WJPCucJXJqZEQ)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w384-changelog-union` 의 10a31bda 까지를 squash 했다(4a45a115).
- 메인 세션이 다시 돌린 검사: `test_changelog_union.py` 4개 통과, scripts 전체 통과, 감사 오류 0건.
- 결과(시험으로 고정): 맨 위에 더한 줄은 union 으로 합칠 때 합치는 방향에 따라 릴리스된 절이나 Unreleased 에 들어간다.
  union 없이 합치면 충돌한다. 맨 아래에 더한 줄은 방향과 union 여부에 상관없이 릴리스된 절에 들어간다.
- 처리 방법은 이 카드의 `## Progress` 에 있다. 그 비교가 두 경우 모두 줄을 찾는 것을 시험이 확인한다.

- Checks at close 2026-11-22: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS)
