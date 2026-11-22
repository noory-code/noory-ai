---
id: W-00000380
title: Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
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


## Verification
