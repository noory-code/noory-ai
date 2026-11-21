---
id: W-00000379
title: Stage CI 의 테스트를 여러 잡으로 나눠 PR 결과가 빨리 나온다
kind: ops
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000379
promotion: not_applicable
review: passed
scope: .github/workflows/stage.yml,.github/scripts
promotes:
decision_refs:
---

# W-00000379 Stage CI 의 테스트를 여러 잡으로 나눠 PR 결과가 빨리 나온다

## Purpose

Stage PR 의 CI 결과가 Windows 테스트 한 잡을 기다리느라 10분 걸리던 것이 줄어든다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- PR 에서 stage 워크플로가 시작해서 끝날 때까지 걸린 시간이 바꾸기 전(약 10분)보다 줄었다
- 나눈 잡들이 실행한 테스트 수의 합이 나누기 전 한 잡이 실행한 수와 같다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-21

```
What changed: Added .github/scripts/unittest_shard.py and ran both Stage suites through it in a three-value shard matrix in stage.yml (18 jobs, smoke steps in shard 1 only); added two tests to stage/scripts/tests/test_ci_workflows.py (matrix shards equal 1..SHARD_TOTAL including the ubuntu-24.04 entries; shards together run every test exactly once for totals 1, 2, 3, 4, 8); added a stage/CHANGELOG.md Unreleased entry.
Why: The workflow's wall time is its slowest job, and the Windows scripts suite alone took 536 seconds; on PR #87 the stage run finished in 4m05s against 10m39s before, ubuntu scripts shards took 21-36 seconds against 97, and CI logs show shards running 152+152+151=455 hook and 269+269+268=806 scripts tests.
Decisions made: Shard round-robin over sorted test ids rather than by module, so the heavy modules spread across shards; shard every OS with the same count of three because the user asked to shorten ubuntu too; keep the helper under .github/scripts as repository CI tooling outside the shipped plugin; crossed the card scope into stage/scripts/tests/test_ci_workflows.py and stage/CHANGELOG.md to guard the silent gap a drifted shard count would cause, and the repository rule requires a changelog entry for any change inside stage/.
Work not done: Test fixtures were not made cheaper; the Python 3.9 matrix entries were not reduced; one macOS job queued about 75 seconds because GitHub runs five macOS jobs at once, which stayed off the critical path.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- PR #87 의 stage 실행(44920216721): 15:38:00 에 시작해 15:42:05 에 끝났다(4분 5초). 바꾸기 전 PR #86 의 실행은
  15:09:14 ~ 15:19:53(10분 39초)였다. Windows 잡은 142~241초, Ubuntu 잡은 39~47초였다.
- CI 로그에서 샤드별 테스트 수를 셌다. Windows 3.9 와 Ubuntu 3.12 모두 hooks 152+152+151=455, scripts
  269+269+268=806 이고, 나누지 않은 로컬 실행도 455 와 806 이다.
- 코드 커밋이 둘(bae6d0ab, beb8f79a)이라 리뷰가 모든 경로를 받도록 두 커밋을 합친 로컬 커밋에서 닫았다.

- Checks at close 2026-11-21: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
- 닫기 리뷰어는 클라우드에서 명령 실행 승인을 받지 못해 아무 명령도 실행하지 못했다. 판정은 이 카드에 적힌 CI
  증거와 바뀐 파일을 읽은 것에 기댄다. 테스트 수와 시간은 닫는 쪽이 CI 로그와 API 에서 직접 셌다.
