---
id: W-00000274
title: Distill이 근거와 함께 현재 적용할 기준을 반환하게 한다
kind: development
venue: codex
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000274
promotion: deferred
review: not_required
scope: /Users/woogis/Workspace/novel-workspace/novel-ai/plugins/distill/
promotes:
decision_refs: DE-00000085
---

# W-00000274 Distill이 근거와 함께 현재 적용할 기준을 반환하게 한다

## Purpose

새 선택에서 적용 범위에 맞는 현재 기준과 그 근거를 사용할 수 있게 합니다

## Actions

W-00000273에서 교환 형식을 정한 뒤 Distill 저장소에서 실패하는 테스트부터 작성합니다.

## User value

관련 없는 프로젝트의 규칙이나 바뀐 옛 기준 때문에 잘못 선택하는 일을 줄입니다.

## Scope

### Included

- 기존 저장소에 기준의 출처, 발언 주체, 확인 여부, 조건·예외와 변경 관계를 보존합니다.
- 현재 적용할 기준을 조회하고 근거를 함께 반환합니다.
- 기존 데이터의 읽기·이동·규칙 생성에 새 필드가 미치는 영향을 검사합니다.
- 해당 저장소의 버전·변경 기록·테스트 규칙을 따릅니다.

### Excluded

- Stage나 Avatar의 내부 코드를 import하지 않습니다.
- Codex 대화 전체의 자동 수집을 암묵적으로 추가하지 않습니다.

## Risks

현재 recall은 읽은 경로에서 supersedes 관계를 조회하지 않습니다. 실제 실패를 테스트로 재현한 뒤 고칩니다.
metadata.py의 insert와 move, 추출·규칙 생성·검색의 모든 필드 전달 경로를 확인해야 합니다.
noory-ai의 드라이버가 외부 저장소 변경을 자동으로 관측한다고 가정하지 않습니다.

## Success criteria

- 사람이 밝힌 기준과 AI의 추정을 저장하고 조회할 때 구별합니다
- 조건과 예외와 기준 변경을 보존하고 다른 프로젝트의 기준이나 대체된 기준을 현재 기준으로 반환하지 않습니다
- 기존 기록과 저장·검색 경로를 유지하고 두 호스트가 같은 형식으로 기준을 읽을 수 있습니다

## Next action

2026-11-01 제품 배포 근거와 네 가지 검사를 확인하고 종료했습니다. 이 카드에 남은 종료 절차는 없습니다.

## Related truth

SSOT, MECE, TDD, Fail Fast, Honesty를 적용합니다.
실제 경로와 독립성 규칙은 부모 카드에서 확인합니다. novel-ai에는 현재 .stage 디렉터리가 없습니다.

## Progress

### Executor report — 2026-11-01 종료 절차

What changed: DE-00000085와 R-00000274를 작성하고 제품 커밋·배포·리뷰 근거를 연결했습니다. 닫기 도구가 외부 제품 검사 네 개를 실행한 뒤 카드와 인덱스를 갱신했습니다.
Why: 다른 저장소의 제품을 noory-ai HEAD 리뷰로 검증했다고 보고하지 않고 실제 제품 증거로 종료합니다.
Decisions made: 사용자 승인에 따라 이 카드만 review: not_required로 닫았습니다. 원본과 배포의 patch-id 일치, 배포 커밋의 origin/main 포함, 기존 독립 리뷰 승인을 확인했습니다. 이번에는 제품 소스를 수정하지 않았습니다. 기존 비차단 지적 여섯 개는 한계로 남깁니다. promotion은 deferred이며 공식 정책을 바꾸지 않습니다. 이번 종료에서 바뀐 아래 여섯 경로는 모두 기존 제품 scope 밖의 Stage 기록입니다. 과거 실행 준비에서 바뀐 외부 .stage/와 .gitignore도 위 기록을 보존했습니다.
Changed paths (JSON): [".stage/decisions/index.md", ".stage/decisions/pending/DE-00000085.md", ".stage/work/active.md", ".stage/work/current/W-00000272/W-00000274/_story.md", ".stage/work/retrospectives/R-00000274.md", ".stage/work/review.md"]
Review dispositions (JSON): []

2026-10-05: 현재 소스를 읽고 등록했습니다. 제품 파일은 바꾸지 않았습니다.

2026-10-05: 같은 HEAD `f186e0017af732caa7e4fbabeba4b7eb5f7429c6`에서 Distill용 worktree를 만들었습니다.
경로는 `/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill`이고 가지는 `codex/criteria-distill`입니다.
그 안에만 영어 Stage 실행 환경과 로컬 W-00000274 카드를 준비했습니다.
로컬 카드는 이 카드와 부모의 합의를 참조하고, 해당 저장소에서 실행한 증거를 소유합니다.
준비 과정에서 패키지 범위 밖의 `.stage/`와 `.gitignore`를 바꿨습니다. 제품 변경과 구별해 검토해야 합니다.
원래 novel-ai 체크아웃은 바꾸지 않았습니다.
2026-10-06 사용자의 승인 뒤 준비물을 `32964c6c`로 커밋하고 해당 worktree의 드라이버를 시작했습니다.
실행·검사·독립 리뷰 기록은 그 worktree의 `.stage/.runtime/driver/logs/W-00000274.md`에서 확인합니다.

2026-10-06: Codex CLI의 사용량 오류 뒤 사용자가 이 세션에서 직접 구현하도록 허용했습니다. 감독이 전용 worktree에서 구현과 검사를 이어갔습니다. Claude CLI로 독립 리뷰를 받았으며, 반려된 항목은 실패 시험으로 재현하고 수정했습니다. 드라이버의 완료 판정으로 보고하지 않습니다. 제품 커밋·푸시는 아직 하지 않았습니다.

## Verification

2026-11-01: 사용자가 승인한 일회성 리뷰 예외는 [DE-00000085](../../../../decisions/pending/DE-00000085.md)에 기록했습니다. 제품 원본 `77c2f9bd`와 배포 `bcc44303`의 patch-id는 `5a582eb413b51e572e3a5d6b0b05eef3a4e4b71e`로 같습니다. fetch 뒤 배포 커밋이 novel-ai origin/main의 조상임을 확인했습니다.

독립 리뷰 원본 `distill-claude-review-round2.json`은 `approved: true`이며 성공 기준 세 개를 모두 통과시켰습니다. 이번에 새 제품 리뷰를 실행하지는 않았습니다. 기존 비차단 지적은 그대로 남깁니다: 긴 입력의 오류 분류와 길이 제한, AI 기준 revise의 기본값 안내, CLI/MCP refs 정규화 차이, stage 출처 문법, fastembed 실제 CLI 시험 부재, criteria.py의 크기입니다. 당시 리뷰가 승인한 한계이며 이번 사용자 지시는 종료 절차만 다루므로 제품 변경과 추가 등록은 하지 않습니다.

검사 위치는 `/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill`입니다. 2026-11-01에 `uv run --frozen python -m pytest -q` 379개, `uv run --frozen mypy src/` 소스 파일 40개, `uv run --frozen ruff check src/ tests/`, `uv run --frozen ruff format --check src/ tests/` 파일 71개가 모두 통과했습니다. scope에 적힌 예전 경로는 바꾸지 않았습니다. 외부 worktree에 원래 남아 있던 카드 변경도 보존했습니다.

변경 전 기준 확인: Distill 패키지에서 `uv run --frozen python -m pytest tests/test_metadata.py tests/test_tools_recall.py tests/test_r8_independence.py -q`를 실행해 기존 테스트 50개가 통과했습니다.
`uv run --frozen pytest ...`는 pytest 실행 파일을 시작하지 못했습니다. `uv sync --frozen --group dev` 뒤 모듈 실행 방식으로 확인했습니다.
이는 새 기준 기능의 검증이 아니라 기존 동작의 기준 기록입니다.

새 실패 사례의 RED와 수정 뒤 GREEN, 기존 테스트·mypy·ruff·독립성 검사를 기록합니다.

별도 worktree에서 Stage 구조 검사는 오류 0개·경고 0개였습니다.
드라이버 dry-run은 로컬 W-00000274와 Codex 실행자, 전체 테스트·타입·린트·포맷 검사, Claude 판정자를 모두 찾았습니다.
이는 실행 준비 검사이며, 모델이 제품을 구현하거나 검토한 결과는 아닙니다.
기존 정적 검사와 포맷 실패는 O-00000049에 열거했습니다.

2026-10-06: 실행 위치, 제품별 검사 수, 리뷰 원본과 한계는 [구현·검증 기록](../../../../research/llm-work/integration/implementation-status.md)에 모았습니다. 실제 두 호스트 인계와 제품 소스 보존이 남아 있어 이 카드를 완료로 바꾸지 않습니다.

### Executed at close — 2026-11-01

```
$ cd /Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill && uv run --frozen python -m pytest -q
[exit 0]
........................................................................ [ 18%]
........................................................................ [ 37%]
........................................................................ [ 56%]
........................................................................ [ 75%]
........................................................................ [ 94%]
...................                                                      [100%]
379 passed in 3.20s

$ cd /Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill && uv run --frozen mypy src/
[exit 0]
Success: no issues found in 40 source files

$ cd /Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill && uv run --frozen ruff check src/ tests/
[exit 0]
All checks passed!

$ cd /Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill && uv run --frozen ruff format --check src/ tests/
[exit 0]
71 files already formatted
```

## Retrospective

[R-00000274](../../../../work/retrospectives/R-00000274.md)에 제품 결과와 종료 절차를 구분해 적었습니다.

## Promotion decision

deferred — DE-00000085는 이 카드만 대상으로 삼는 종료 예외입니다. 공식 정책으로 승격하지 않습니다.
