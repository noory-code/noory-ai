---
id: W-00000278
title: 세 플러그인을 기본 브랜치에 병합하고 배포한 버전을 확인한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000278
promotion: not_applicable
review: not_required
scope: stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md, avatar/, .agents/plugins/marketplace.json, .claude-plugin/marketplace.json, /Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill/, .stage/research/llm-work/integration/
promotes:
decision_refs:
---

# W-00000278 세 플러그인을 기본 브랜치에 병합하고 배포한 버전을 확인한다

## Purpose

검토한 세 플러그인을 원격 기본 브랜치에 반영하고 배포한 버전을 실제로 불러옵니다

## Actions

원격 main에서 배포용 작업 폴더 두 개를 만들고 검토한 제품 커밋만 적용합니다.
Stage·Avatar의 릴리스 명령을 실행하고 Distill의 1.10.0 버전 일치를 확인합니다.
로컬 검사와 원격 CI가 통과하면 PR을 병합합니다. 원격 main을 새로 받아 버전과 실제 로드를 확인합니다.

## User value

사용자는 "푸시하고 병함하고 배포하고 그러세요"라고 요청했습니다.
검토한 기능을 두 저장소의 기본 브랜치에서 설치하고 사용할 수 있게 합니다.

## Scope

### Included

세 플러그인의 검토한 제품 변경과 배포 메타데이터, PR·CI·호스트 로드 증거를 다룹니다.

### Excluded

관련 없는 원본 체크아웃 변경과 개인 기준 DB는 배포에 넣지 않습니다.

## Risks

두 원격 저장소에 새 커밋이 있으므로 main에서 배포 가지를 만듭니다. 제품 파일의 중첩 변경과 CI를 확인합니다.
기록용 준비물 커밋은 제품 커밋과 구별합니다. 배포용 작업 폴더는 기존 시험 소스를 보존하기 위해 별도로 만들었습니다.
진입 경로는 Claude·Codex 두 곳이며 원격 저장소는 두 개입니다. 상태는 로컬 준비·푸시·병합·새 버전 로드 네 단계로 기록합니다.

## Success criteria

- Stage·Avatar·Distill의 검토된 변경이 각 원격 기본 브랜치에 병합됩니다
- 배포한 버전이 변경 기록과 두 호스트 manifest에서 일치하고 새 세션에서 실제로 불러와집니다
- 배포 검사와 원격 커밋 및 남은 제한을 기록하며 관련 없는 기존 변경은 보존합니다

## Next action

배포와 증거 검사를 마치고 작업을 닫았습니다. 이번 배포에서 남은 단계는 없습니다.

## Related truth

SSOT·SoC·Honesty·Completion을 적용합니다. W-00000274~277의 구현·검사 기록과 root CLAUDE.md의 배포 절차를 따릅니다.

## Progress

GitHub CLI에 주어진 환경 변수의 인증은 실패했습니다. 해당 변수 없이 기존 CLI 인증을 사용하자 저장소 조회에 성공했습니다.
인증 파일과 전역 설정은 바꾸지 않았습니다. Git 푸시 dry-run도 성공했습니다.
실제 배포 경로는 noory-ai의 `/Users/woogis/.codex/worktrees/criteria-release/noory-ai`와
novel-ai의 `/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/criteria-release`입니다.
후자는 등록 당시 Distill 경로와 다릅니다. 소스 보존을 위한 별도 작업 폴더이며 scope 필드는 바꾸지 않았습니다.

Stage 0.63.3·Avatar 0.1.2를 noory-ai PR #5로 병합했습니다. Distill 1.10.0은 novel-ai PR #2로 병합했습니다.
PR 검사 37개가 통과했습니다. 세 릴리스는 각각 병합 커밋을 가리킵니다.
두 원격 main을 새로 받아 Claude·Codex에서 스킬 세 개와 같은 경로의 manifest 버전을 실제로 읽었습니다.
임시 설치 세 개를 제거했고 사용자 설정 파일의 바이트가 같음을 확인했습니다. 원본 체크아웃의 관련 없는 변경은 보존했습니다.

## Verification

원격 PR·릴리스 링크와 커밋, 실제 도구 호출, 파일 해시는 `.stage/research/llm-work/integration/release-status.md`와 그 증거 폴더에 있습니다.
Claude가 배포 메타데이터를 준비했고 Codex 감독 세션이 diff·버전·검사 결과·실제 호스트 호출을 확인했습니다.
W-00000279에서 발견한 CI 결함은 모두 수용하고 고쳤습니다. 독립 Claude 리뷰 세 번에서 추가 결함을 보고하지 않았습니다.
배포 확인은 새 세션에서 스킬과 manifest를 읽는 범위입니다. 훅을 끄고 MCP 도구는 호출하지 않았으며, 실제 업무의 비용 절감 효과는 측정하지 않았습니다.

### Executed at close — 2026-10-07

```
$ python3 .stage/research/llm-work/integration/verify_release_evidence.py
[exit 0]
PASS: three published versions, two merged PRs, 37 CI jobs, matching source files, and two actual hosts.
```

## Retrospective

[R-00000278](../../../retrospectives/R-00000278.md)에 외부·내부 결과와 적용 원칙을 기록했습니다.

## Promotion decision

not_applicable. 이 배포에서 새 공식 결정을 만들지 않았습니다.
