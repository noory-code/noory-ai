---
id: W-00000375
title: PR #85 브랜치에 main 을 합쳐 충돌을 푼다
kind: chore
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000375
promotion: pending
review: pending
scope: stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000375 PR #85 브랜치에 main 을 합쳐 충돌을 푼다

## Purpose

PR #85 가 main 과 충돌 없이 머지된다

## Actions

액션으로 나누지 않는다. 머지 커밋 하나를 만드는 일이다.

## User value

PR #85(Windows 에서 리뷰어가 PowerShell 도구로 테스트를 실행하게 한 고침)는 PR #83 이 먼저 머지되면서
main 과 충돌한다. 이 일이 끝나면 PR #85 를 머지할 수 있다.

## Scope

### Included

- `origin/main`(e9e0c025)을 `claude/reviewer-powershell-rule` 에 합친다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에서 양쪽 항목을 모두 남긴다.

### Excluded

- 양쪽 항목의 글을 고치는 일.
- Stage 릴리스.

## Risks

- 머지 커밋에는 PR #83 이 main 에 넣은 파일도 들어온다. 이 카드가 고친 것은 충돌한 두 파일뿐이다.

## Success criteria

- stage/CHANGELOG.md 의 Unreleased 에 PowerShell 규칙 항목과 main 의 블루프린트 항목이 모두 있고 충돌 표시가 없다
- 충돌을 푼 트리에서 감사와 리뷰 관련 테스트가 통과한다

## Next action

닫고 PR #85 를 머지한다.

## Related truth

- W-00000361: 같은 까닭으로 PR #71 에 main 을 합친 카드.
- W-00000374: PR #85 의 고침을 담은 카드.

## Progress

- 충돌한 파일은 두 개다. `stage/CHANGELOG.md` 는 양쪽이 `## Unreleased` 맨 위에 한 항목씩 더했다. 이
  브랜치의 항목을 위에, main 의 항목을 그 아래에 두었다.
- `.stage/official/work/archive/index.md` 는 양쪽이 표 끝에 한 줄씩 더했다. 번호 순서대로 W-00000366,
  W-00000374 로 두었다. 이 파일은 카드 범위 밖이고, W-00000374 의 보관 intent 를 만들어서 고쳤다.
- 머지 커밋에서 그 밖의 파일은 모두 PR #83 에서 온 것이고 손대지 않았다.

## Verification

- 환경은 `local-no-codex` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다(DE-00000086).
- 이 카드는 DE-00000087 의 대상 경로를 고치지 않는다. 머지로 들어온 `.stage/settings.json` 은 PR #83 이
  main 에서 이미 바꾼 것이다.
- 한국어 Windows 11(cp949)에서 충돌을 푼 뒤 두 파일에 충돌 표시가 없는 것을 확인했다.
