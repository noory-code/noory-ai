---
id: W-00000380
title: Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000380
promotion: not_applicable
review: passed
scope: stage/scripts/tests,stage/CHANGELOG.md,.github/workflows/stage.yml
promotes:
decision_refs:
---

# W-00000380 Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축

## Purpose

Windows CI 의 Scripts suite 단계(샤드당 128-212초, ubuntu 의 약 5배)를 테스트 격리와 단언을 그대로 둔 채 단축해 Stage PR 의 CI 결과가 더 빨리 나온다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- PR 의 stage 워크플로에서 windows-latest Scripts suite 단계의 가장 느린 샤드가 main 기준(e0d95a1 최대 181초, 75c700d8 최대 212초)보다 30% 이상 빠르다(127초 미만).
- scripts 테스트 수가 main(75c700d8)의 821개에 이 카드가 더한 5개를 합친 826개이고, 각 OS 의 샤드들이 hooks 455 개와 scripts 826 개를 정확히 한 번씩 실행한다. 테스트 삭제·skip·단언 약화가 없다.

## Next action


## Related truth


## Progress

- 2026-11-21: 처음 계획은 픽스처 비용만 줄이는 것이었다. strace 로 세 보니 스크립트 스위트가 프로세스를 약 9,500개 띄웠고, 그중 픽스처 몫은 약 1,700개, 커밋마다 뜨는 `git maintenance` 가 약 520개였다. 나머지는 테스트 대상인 드라이버 코드의 git 호출이었다. Windows 러너에서 잰 git 프로세스 하나는 35-46ms(ubuntu 약 1ms)였다. 테스트 전용 전역 git 설정으로 프로세스를 9,500개에서 7,700개로 줄였지만, Windows 샤드 합계는 main 971/1001초 대 PR 1037/1017초로 노이즈 안이었다.
- 2026-11-22: 픽스처만으로는 성공 기준에 닿지 않는다고 메인 세션에 보고했고, 사용자가 B안(Windows 샤드 수를 이 카드 안에서 늘린다)을 골랐다. 그래서 범위에 `.github/workflows/stage.yml` 을 넣고, 목적과 성공 기준을 픽스처 수단에서 Windows 단계 시간이라는 결과 쪽으로 고쳐 적었다. 드라이버 git 호출 줄이기와 Windows 에서 timeout 이 손자 프로세스를 죽이지 못하는 버그는 메인 세션이 후속 카드로 등록한다.


### Executor report at close — 2026-11-22

```
What changed: Added stage/scripts/tests/git_test_config.py (a throwaway GIT_CONFIG_GLOBAL with the test identity, maintenance.auto=false, gc.auto=0, commit/tag signing off, and an init template holding only hooks/ and info/exclude) with five tests in test_git_test_config.py; test_drive, test_drive_unattended, test_drive_parallel, test_land_run, and test_driver_git call it and drop their per-repository `git config user.*` calls; .github/workflows/stage.yml now runs WINDOWS_SHARD_TOTAL=6 shards on windows-latest and SHARD_TOTAL=3 elsewhere (matrix.shard 1..6, shards 4-6 excluded for ubuntu-latest and macos-latest, --total chosen per OS); test_ci_workflows.py expands the matrix and checks each OS runs every shard number up to its own total, and the shard split test also covers a total of 6; stage/CHANGELOG.md has two Unreleased entries; the card was retargeted to the outcome after the user chose the shard split.
Why: strace showed about 9,500 processes per scripts run and a Windows git process costs 35-46 ms against about 1 ms on ubuntu; the shared config cut processes to about 7,700 and the local suite from 150 s to 110 s but stayed within Windows run-to-run noise (6-shard sums 1037/1017 s against main 971/1001 s), so on PR #92 run 44991635243 six Windows shards took 66-102 s in Scripts suite against 128-212 s with three, and the whole stage run took 170 s against 254-286 s on main.
Decisions made: Six Windows shards rather than five so the Windows step lands near the slowest macOS job; the other OSes keep three shards to avoid extra runner time; the test git config leaves the system config in force so Git for Windows keeps core.autocrlf; the template keeps an empty hooks directory because test_stage_id_reservation installs a pre-receive hook; the driver's own git calls and the Windows timeout that does not kill shell=True grandchildren were left to follow-up cards the main session registers.
Work not done: The driver_repository snapshot still starts three to four git processes per snapshot; close_work's --timeout and --review-timeout still wait for a shell=True grandchild on Windows; no fixture template repository was built because a Windows copytree of .git saves only about 80 ms per repository.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델(Claude 대역)의 리뷰이고 교차 venue 리뷰가 아니다.
- PR #92 의 stage 실행 44991635243(head bf382e14): 05:58:11 에 시작해 06:01:01 에 끝났다(170초). 모든 잡이 성공했다.
  main e0d95a1 의 실행 44921559626 은 254초, 75c700d8 의 실행 44936057502 는 286초였다.
- windows-latest Scripts suite 단계(초): 3.12 샤드 1-6 = 71, 80, 77, 81, 90, 73 / 3.9 샤드 1-6 = 90, 66, 102, 75, 84, 77.
  가장 느린 샤드 102초. 바꾸기 전 3샤드는 e0d95a1 에서 128-181초, 75c700d8 에서 133-212초였다.
- 같은 실행의 다른 OS Scripts suite: ubuntu 26-41초, macOS 39-66초(바꾸기 전 23-49초, 43-104초).
- CI 로그에서 샤드별 테스트 수를 셌다. windows-latest 3.9(6샤드) hooks 76+76+76+76+76+75=455, scripts
  138+138+138+138+137+137=826. ubuntu-latest 3.12(3샤드) hooks 152+152+151=455, scripts 276+275+275=826.
  main 75c700d8 를 로컬에서 discover 하면 hooks 455, scripts 821 이고, 이 카드는 `test_git_test_config.py`
  5개를 더했다. 테스트를 지우거나 skip 하거나 단언을 바꾸지 않았다(픽스처의 `git config user.*` 호출만 뺐다).
- 픽스처 변경만 들어간 실행(44938724642, 44939281780)의 Windows 6개 샤드 합은 1037초, 1017초로, main 의 971초,
  1001초와 노이즈 안에서 같았다. 이 효과는 성공 기준의 근거로 쓰지 않는다.
- 코드 커밋이 여럿이라 main 75c700d8 위에 합친 로컬 커밋 b06ca1ef 에서 닫았다.

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_git_test_config.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_drive_unattended.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
- 닫기 리뷰어는 `test_ci_workflows.py`(4 통과)와 `test_git_test_config.py`(5 통과)만 실행했다. 전체 discover 와
  GitHub Actions 조회는 클라우드에서 승인을 받지 못해 실행하지 못했다. 826 이라는 수와 CI 시간은 이 카드에 적힌
  증거와 바뀐 파일을 읽은 것에 기댄다. 그 수와 시간은 닫는 쪽이 CI 로그와 API 에서 직접 셌다.
- 닫은 뒤 main 4287eb70(W-00000377)을 병합하고 두 스위트를 다시 돌렸다. hooks 461, scripts 823 모두 통과했다.
  scripts 823 은 병합된 main 의 818 에 이 카드의 5개를 더한 수다. 회고 R-00000380 은 PR #93 의 세 절 형식으로 고쳐 적었다.
