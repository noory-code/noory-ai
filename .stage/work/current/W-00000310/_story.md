---
id: W-00000310
title: 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_supervised.py, stage/scripts/driver_unattended.py, stage/scripts/driver_review.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/claude_review_companion.py, stage/templates/v4/project-stage/settings.jsonc, stage/scripts/tests/, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000310 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다

## Purpose

Codex 리뷰어나 다른 프로젝트의 Claude 리뷰어가 돌린 시험 코드가 저장소를 바꿔도 그 리뷰가 승인으로 끝나지 않게 한다

## Actions

- W-00000309 가 `stage/scripts/claude_review_companion.py` 에 넣은 앞뒤 스냅숏 비교(`driver_repository.repository_path_snapshot`)를
  리뷰어 명령을 부르는 자리(감독·무인 드라이버, `close_work.py`)로 옮겨 모든 리뷰어에 건다. 대역의 검사는 그 공통 검사로
  대체해 한 곳만 남긴다(SSOT).
- v4 템플릿(`stage/templates/v4/project-stage/settings.jsonc`)의 Claude 리뷰 명령이 공통 검사를 받게 한다.

## User value


## Scope

### Included


### Excluded


## Risks

- 리뷰 중에 사람이 같은 체크아웃을 만지면 그 변경도 리뷰 실패로 잡힌다(O-00000013 과 같은 모양). 실패 메시지가 그
  가능성을 알려야 한다.
- 실측 근거: W-00000309 의 Progress. `python3 -m unittest` 가 돌린 시험 코드는 권한 규칙과 상관없이 썼다.


## Success criteria

- 드라이버와 close_work 가 어느 리뷰어 명령이든 앞뒤 저장소를 비교해 판정 파일 밖이 바뀌면 리뷰를 실패로 기록하고 바뀐 경로를 알린다는 것을 테스트가 확인한다
- v4 템플릿의 Claude 리뷰 명령이 같은 검사를 받는다는 것을 테스트가 확인한다

## Next action

## Related truth

## Progress

2026-11-01 클라우드 세션. 검사를 대역(`claude_review_companion.py`)에서 `close_work.run_close_review` /
`reject_review_writes` 와 감독 드라이버로 옮겼다. 무인 드라이버는 리뷰를 `close_work` 로 돌리므로 따로 고칠 것이 없다.
v4 템플릿의 `reviewers.claude` 는 빈 값이고 프로젝트가 직접 채운다. 검사가 명령 바깥에 있으니 어떤 명령이든
걸리며, 템플릿에는 그 사실을 안내 주석으로 적었다.

실측(`LiveReviewerWriteProbeTest`, CLI `2.1.316 (Claude Code)`, 권한은 두 경로 모두 `Edit(//<판정 파일>)` 과
`Bash(python3 -m unittest:*)`)으로 `close_work.run_close_review` 를 거쳐 확인했다.

| 경로 | 시험 실행 | 통과 | 남은 변경 | 판정 파일 |
|---|---|---|---|---|
| cloud 대역 | 했다 | 아니오 | ` M tracked.txt` (직접 쓰기 셋은 없음) | 지워짐 |
| 프로젝트 `reviewers.claude` 1판 | 안 했다 | 예 | 없음 | 남음 — 검사가 걸릴 일이 없던 판 |
| 프로젝트 `reviewers.claude` 2판 | 했다 | 아니오 | ` M tracked.txt` | 지워짐 |

프로젝트 경로 1판에서 리뷰어는 "직접 돌려서 통과한다"는 기준을 시험을 돌리지 않고 통과시켰다. 시험을 돌릴지는
모델이 고르므로, 실측 시험은 시험이 돌지 않은 판을 미완료로 기록하고 건너뛰게 했다.

## Verification

## Retrospective

## Promotion decision
