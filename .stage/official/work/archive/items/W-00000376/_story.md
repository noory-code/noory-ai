---
id: W-00000376
title: PR 브랜치에서 CI 가 같은 테스트를 한 번만 실행하게 하기
kind: ops
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000376
promotion: not_applicable
review: passed
scope: .github/workflows,stage/scripts/tests/test_ci_workflows.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000376 PR 브랜치에서 CI 가 같은 테스트를 한 번만 실행하게 하기

## Purpose

워크플로 네 개가 push 와 pull_request 양쪽에서 실행돼서 PR 이 열린 브랜치에 push 하면 같은 테스트가 두 번 실행되는 것을 고쳐, PR 의 검사 수와 기다리는 시간을 절반으로 줄인다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

PR 을 올린 사람이 CI 를 기다리는 시간이 줄어든다. PR #85 는 검사 24개가 실행됐는데 그 가운데 12개는 같은
테스트를 한 번 더 실행한 것이었다. 사용자가 CI 테스트가 과하다고 했다(2026-11-21).

## Scope

### Included

- 워크플로 네 개(`stage`, `plugin-contracts`, `avatar`, `plainly`)의 `push` 조건에 `branches: [main]` 을
  더한다.
- 워크플로가 그 한정을 빼면 실패하는 테스트를 `stage/scripts/tests/test_ci_workflows.py` 에 더한다. 워크플로를
  지키는 테스트가 이미 그 파일에 있어서 같은 곳에 두었다.
- `stage/CHANGELOG.md` 에 적는다. Stage 폴더의 파일을 고쳤기 때문이다.

### Excluded

- OS 와 Python 버전 조합을 줄이는 일. 확인하는 범위가 좁아지므로 따로 정할 일이다.
- `main` 브랜치에 필수 검사를 정하는 일과 저장소의 자동 머지 설정.

## Risks

- PR 을 열지 않은 브랜치에 push 하면 CI 가 실행되지 않는다. 지금까지는 실행됐다. 이 저장소는 PR 로만
  머지하므로 머지 전에 한 번은 반드시 실행된다.

## Success criteria

- 워크플로 네 개의 push 조건이 main 브랜치로 한정돼 있고 pull_request 조건과 paths 는 그대로다
- 이 PR 의 검사가 워크플로마다 pull_request 로 한 번씩만 실행된다

## Next action

PR 을 올려 검사 수를 확인한 뒤 머지한다.

## Related truth

- W-00000375: PR #85 의 검사 24개를 기다리면서 중복을 발견했다.

## Progress

- 워크플로 네 개에 같은 두 줄을 더했다. `paths` 와 `pull_request` 는 건드리지 않았다.
- 테스트는 `.github/workflows/*.yml` 을 모두 읽는다. 워크플로가 새로 생겨도 같은 규칙을 확인한다.

## Verification

- 환경은 `local-no-codex` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다(DE-00000086).
- 이 카드는 DE-00000087 의 대상 경로를 고치지 않는다.
- 한국어 Windows 11(cp949)에서 `python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q`
  2개와 `python3 -m unittest discover -s tests -q` 가 통과했다.
- PR #86 을 올려서 두 번째 성공 기준을 확인했다. `gh pr checks 86 --json workflow,event` 로 세면 검사가
  24개이고 모두 `pull_request` 로 실행됐다. 워크플로 네 개마다 6개씩이다. `push` 로 실행된 것은 없다.
  이 PR 은 워크플로 파일 네 개를 모두 고쳐서 네 워크플로가 다 실행됐다. PR #85 는 워크플로 두 개가
  `push` 와 `pull_request` 로 6개씩 실행돼서 24개였다.

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`; `python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q`; `python3 -m unittest discover -s tests -q`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
