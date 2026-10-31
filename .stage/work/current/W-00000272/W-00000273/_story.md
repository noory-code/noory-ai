---
id: W-00000273
title: 세 플러그인이 기준과 근거를 주고받는 약속을 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000273
promotion: promoted
review: passed
scope: .stage/research/llm-work/implementation-design.md, .stage/decisions/pending/
promotes: .stage/official/decisions/records/DE-00000074.md, .stage/official/decisions/index.md
decision_refs: DE-00000074
---

# W-00000273 세 플러그인이 기준과 근거를 주고받는 약속을 정한다

## Purpose

각 플러그인이 독립적으로 동작하면서 같은 기준의 출처와 변경 이력을 잃지 않도록 연결 방법을 정합니다

## Actions

등록 커밋과 별도 worktree를 준비한 뒤 Claude가 설계합니다. Codex가 결과를 검토합니다.

## User value

다음 세션이 기준을 읽을 때 출처와 적용 범위를 추측하지 않아도 되도록 약속을 정합니다.

## Scope

### Included

- Stage 결정 원문, Distill의 파생 규칙, Avatar 개인 기준의 소유 위치와 안정적인 참조를 정합니다.
- 생성·확인·예외·변경·철회·조회·내보내기의 입력과 결과, 잘못된 입력의 처리를 정합니다.
- 각 플러그인이 없는 경우에도 가능한 동작과 두 저장소에서 별도로 검사할 경계를 정합니다.
- Claude와 Codex의 기준 전달 시점을 정하고 실제로 사용했음을 확인할 증거를 정합니다.
- 설계 결정을 pending에 기록하고 적용한 원칙을 적습니다.

### Excluded

- 제품 코드, 사용자 설정과 저장소 실행 정책을 임의로 바꾸지 않습니다.
- 전체 대화 자동 수집이나 모든 판단을 가로채는 기능을 첫 범위로 확대하지 않습니다.

## Risks

Distill은 이미 전역 기억과 관계 기록을 제공합니다. Avatar의 가치를 단순한 전역 저장으로 중복시키지 않습니다.
두 저장소를 하나의 변경 목록으로 취급하면 검증 증거가 빠집니다. 각 저장소의 실행과 검토 경계를 설계에 포함합니다.

## Success criteria

- 각 기록을 어디에서 고치고 다른 플러그인이 어떻게 참조하는지 한 곳에서 확인할 수 있습니다
- 새 기준과 예외와 AI의 추정을 구별하고 이전 기준을 적용하지 않을 조건을 구체적인 사례로 검토합니다
- 두 저장소에서 각각 구현하고 검증할 범위와 순서가 정해져 구현자가 제품 역할을 다시 정할 필요가 없습니다

## Next action

2026-11-01 닫기 리뷰와 감사를 통과해 종료했습니다. 사용자 승인에 따라 DE-00000074를 공식 기록으로 옮겼습니다. 이어서 W-00000274의 종료 증거를 정리합니다.

## Related truth

SSOT, MECE, AHA, SoC, Honesty를 적용합니다.
부모 카드의 연구 경로에서 decision-criteria.md, session-continuity.md, avatar.md와 findings/2026-10-05-distill.md를 읽습니다.
Stage와 Distill의 현재 코드를 다시 대조하며 연구 문서를 구현 사실로 대신하지 않습니다.

## Progress

2026-10-05: 작업을 등록했습니다. 연결 설계는 아직 작성하지 않았습니다.

2026-10-05: Claude(Opus 5.5)가 설계 초안을 썼습니다. [구현 설계](../../../../research/llm-work/implementation-design.md)와 [DE-00000074](../../../../official/decisions/records/DE-00000074.md)(당시 `status: open`)입니다.
첫 실행에서 Claude가 소스를 읽고 있을 때 Codex 실행자가 SIGINT를 보내 그 실행을 멈췄습니다. 이어진 실행에서 같은 Claude 작성자가 초안을 마쳤습니다.
설계는 Distill(`f186e001`)과 이 worktree의 Stage 소스를 직접 읽고 썼습니다. 연구 문서를 구현 사실로 대신하지 않았습니다.
당시 Distill 프로젝트 판별 비교는 실행 권한이 없어 돌리지 못했고, 실행자에게 요청으로 남겼습니다.

2026-10-05: Codex·감독 독립 검토가 초안을 반려했습니다. 지적 13개를 모두 받아들여 Claude(Opus 5.5)가 설계 문서와 DE-00000074를 고쳤습니다.
고친 내용:
- snapshot 나이 대신, 넘기는 순간에 생산자 CLI를 부르고 선택 직전마다 `criteria check`를 부릅니다.
- TTY 확인을 없애고 대화 원문과 출처를 받는 확인 동작으로 바꿨습니다.
- 멱등 키와 의미 digest로 같은 요청을 가립니다.
- 출처에 참조·원문·digest·행위자를 남깁니다. `stage:` 출처를 지원하고, 출처가 바뀌거나 없어지면 표시합니다.
- 앞선 결과는 파일 sha256과 실행 증거로 대조합니다.
- Avatar 출처 투영의 규칙을 정했습니다.
- Distill은 선언된 정적 검사를 전부 통과해야 완료입니다.
- novel-ai 구현 worktree에서 그 worktree의 드라이버로 실행합니다. 기점은 `f186e001`로 고정했습니다.
- 기준 충돌을 푸는 순서와 조건의 AND/OR·경로 판정을 정했습니다.
- 실제 검증은 과제를 미리 고정하고, 결과를 모두 남깁니다.
- 명령 예시의 경로는 자리표시자로 바꿨습니다.
표식 파일 비교는 감독이 실제로 실행했고, 그 결과를 감독이 보고한 출력으로 인용했습니다. 제품 코드, 설정, 커밋은 바꾸지 않았습니다.

2026-10-05: Codex 재검토는 전체 방향을 받아들였습니다. 다만 계약 오류 8개가 남았다고 지적했습니다. Claude(Opus 5.5)가 해당 절만 고치고 DE-00000074를 맞췄습니다.
- 생산자 명령을 JSON argv 배열(`shell=False`)로 받습니다. 받은 AI에게는 완성된 check 배열을 packet에 실어 줍니다.
- 멱등 digest에 동작 이름, 대상 ID와 버전, payload 전체를 넣습니다.
- 투영을 버전 digest와 봉투 digest로 나눴습니다.
- `check` 결과는 `eligible_current`일 때만 적용합니다. 확인되지 않은 버전, 제안 상태, 다른 범위의 기준은 적용하지 않습니다.
- `partial`과 `needs_judgment`는 판단을 기록한 뒤에 적용합니다. 조건 항목끼리는 AND, 항목 안에서는 OR로 판정합니다.
- `stage:` 출처의 경로 안전과 출처 상태를 정하고, 출처가 바뀌거나 사라진 결정은 `unresolved`로 처리합니다.
- Distill 완료 검사를 `uv run mypy src/`와 `uv run ruff format --check src/ tests/`를 포함한 네 가지로 바로잡았습니다.
- novel-ai 구현 worktree 준비는 감독이 했다고 보고한 사실로 반영했습니다.
외부 worktree는 읽지도 고치지도 않았습니다.

2026-10-06: Avatar 확인이 기존 버전을 고치지 않고 N+1을 만든다는 점과 scope 객체 모양을 설계에 명시했습니다. 원래 검토본의 digest를 남겼으며 Claude의 최종 수정 리뷰가 이 설명을 승인했습니다. Stage의 모호한 경로를 unresolved로 두는 규칙도 표에 반영했습니다. SSOT·Honesty를 적용합니다.

### Executor report at close — 2026-11-01

```
What changed: 이번 닫기 리뷰가 찾은 범위 검사 문서 모순을 고쳤습니다. 설계 6절은 Distill의 project/key와 Avatar의 personal/personal을 생산자별로 검사한다고 명시하며, DE-00000074와 카드에 수용 근거를 남겼습니다. 최초 설계부터 이번 종료 준비까지의 보고를 합칩니다. Claude가 implementation-design.md와 DE-00000074의 설계를 작성하고 두 차례 반려된 계약을 수정했습니다. Codex가 대화 원본 재조회 범위와 Windows 미검증 문구를 바로잡았고 감독이 10월에 .stage/decisions/index.md를 재생성했습니다. 이후 Avatar 확인의 N+1 버전과 scope 객체 모양을 명시했고, 소유자 승인·사용자 승격 승인과 구현·시험 근거를 결정과 카드에 기록했습니다. R-00000273도 작성됐습니다. 이번에는 기존 로그를 보존하고 누적 보고 한 개를 추가하며, 결정에 종료·승격 순서를 명시합니다.
Why: 설계 기준 세 개가 이미 두 차례 통과했어도 마지막 보고에 전체 결정과 범위 밖 변경이 빠지면 실행 경위를 확인할 수 없습니다. 설계 결과와 모든 실행의 누적 범위를 함께 검토할 수 있게 합니다.
Decisions made: 정상 Avatar snapshot의 개인 범위 키는 프로젝트 키와 비교하지 않습니다. 설계 3·7절과 현재 handoff_producers.snapshot()의 동작이 이미 이 계약을 따르므로 제품 설계를 바꾸지 않고 6절의 모순을 고쳤습니다. 앞선 보고 계약 판정은 PASS였으며 아래 누적 결정·경로는 모두 유지합니다. (1) Distill은 기존 전역 metadata.db의 기준 전용 표 다섯 개로 프로젝트 기준을 소유하고, 사람이 정한 project 키를 씁니다. 기존 knowledge·recall·promote·move·crystallize는 기준 표를 읽지 않으며 fastembed 로딩과 touch도 하지 않습니다. Avatar는 개인 기준·선택·돌아보기·출처 투영을, Stage는 목적·작업·결정·증거를 소유합니다. (2) 서로 import하거나 DB를 열지 않고 공개 CLI의 criteria-snapshot/1 JSON으로 연결합니다. scope는 Distill의 project/key 또는 Avatar의 personal/personal 객체이며 참조는 producer:id@version입니다. 버전은 보존하고 쓰기마다 generation을 올립니다. (3) snapshot 파일과 600초 TTL은 폐기했습니다. handoff_packet이 전달 시점에 생산자를 호출하고 받은 AI는 기준에 기대는 선택 직전에 check를 실행합니다. generation·checked_at은 그 시점만 보장합니다. eligible_current만 적용하고 superseded·revoked·unconfirmed·proposed·scope_mismatch·unknown과 실행 실패는 적용하지 않습니다. 저장소 없음과 조회 실패도 구별하며 이전 snapshot으로 대체하지 않습니다. (4) producers.json은 첫 원소가 절대 실행 파일 경로인 JSON argv 배열입니다. shell=False와 30초 timeout을 쓰고 완성한 check argv를 packet에 싣습니다. 잘못된 설정은 E_PRODUCERS_INVALID입니다. Windows 실제 실행까지 검증했다고 주장하지 않습니다. (5) origin은 source_ref·quote·quote_sha256·source_sha256·actor·recorded_by·captured_at을 담습니다. 사용자 원문은 최대 2000자이며 대화 원본을 자동 재조회하지 않습니다. 확인은 TTY나 인증이 아니라 대화의 원문·출처를 기록하는 동작입니다. confirmation과 ai_confidence는 독립이며 AI 추정은 현재로 적용하지 않습니다. Avatar confirm은 N을 보존하고 근거를 담은 N+1을 만듭니다. (6) stage 출처는 다른 project이면 not_checkable, 절대 경로·상위 이동·루트 밖 심볼릭 링크이면 rejected_ref, 절 부재면 missing, hash 차이면 changed입니다. 바뀌거나 사라지거나 거부된 결정 출처는 새 확인 전까지 unresolved이며 원본 이력은 보존합니다. matches는 진실 판정이 아닙니다. (7) 모든 쓰기는 idempotency_key를 요구합니다. digest는 동작·대상·버전과 검증한 payload 전체를 담고 키·저장 위치·출력 형식·생산자가 정할 값만 제외합니다. 같은 키·같은 digest는 replay, 다른 digest는 E_IDEMPOTENCY_CONFLICT입니다. 의미상 동일성에 조건·예외·notes를 포함하며 중복은 E_DUPLICATE_CRITERION, 철회 뒤 record는 새 ID입니다. (8) 조건 항목은 AND, any 안은 OR, 예외 하나라도 맞으면 제외합니다. 경로는 파일·디렉터리만 허용하고 glob과 모호한 범위를 넓히지 않습니다. partial은 실제 파일로 다시 판정해 applies일 때만, needs_judgment는 모든 note를 met으로 기록한 뒤에만 적용합니다. unresolved는 적용하지 않으며 Condition judgment를 다음 packet에도 싣습니다. (9) 충돌은 현재 명시 지시, 목적, 원문 근거가 있는 overrides 순서로 풉니다. 나열 순서는 권위가 아닙니다. 그래도 막힐 때만 사용자에게 묻고 Resolved conflict를 기록합니다. (10) 이전 결과는 Evidence JSON의 파일 hash·명령·종료 코드·시각과 현재 파일·git status를 대조합니다. 실행 검사를 재실행하지 않았다면 not re-run으로 적으며 acceptance·독립 리뷰와 구분합니다. packet은 목적→현재 기준→이전 결과→낡은 판단→결정 순서→남은 작업을 링크가 아닌 본문으로 전달합니다. (11) Avatar 투영은 버전 digest와 봉투 digest를 분리합니다. 같은 봉투는 duplicate, 같은 버전 내용 변경·같은 세대 봉투 변경·철회 사건 유실은 거절합니다. 앞부분을 보존한 높은 세대는 받고 낮은 세대는 현재 표시를 덮지 않습니다. Distill이 없어도 역사적 출처와 직접 입력으로 동작하며 조건이 다른 선택을 모순으로 확정하거나 개인 기준으로 자동 승격하지 않습니다. (12) 판정 재사용·자동 추출·recall 대체 표시·Avatar의 Distill 들여오기·Gemini 허용 목록·훅·설정·드라이버 변경은 첫 흐름 밖입니다. Distill CLI와 MCP 여섯 동작은 같은 계약을 쓰고 Codex enabled_tools와 버전 메타데이터를 맞춥니다. (13) Distill 완료 검사는 pytest, mypy src/, ruff check src/ tests/, ruff format --check src/ tests/ 네 개를 전부 통과해야 합니다. 기존 오류도 면제하지 않되 동작을 보존해 고칠 수 있습니다. (14) 구현 순서는 설계 뒤 Distill과 Avatar, 이어 Stage, 마지막 실제 연결 시험입니다. novel-ai와 noory-ai는 독립 worktree·하네스·검증·리뷰를 쓰며 외부 결과를 noory-ai 드라이버 관측으로 둔갑시키지 않습니다. 준비 기점 f186e001과 커밋 승인을 구분합니다. 준비물 커밋 뒤 Codex 사용량 제한으로 드라이버가 멈췄을 때 사용자가 직접 구현을 승인했고, 독립 Claude 리뷰는 유지했습니다. (15) 실제 검증은 미리 고정한 parse_port·parse_host 과제와 C0/C1/C2를 양방향으로 실행하며 실패·비구별 결과도 보존합니다. 실제 사용자 DB 대신 임시 DB를 쓰고 모델·CLI·훅 상태·출력을 기록합니다. Avatar 확인·이력·투영 단계도 포함합니다. 여섯 수신 세션 결과는 그 사례만 증명하며 일반 성공률·시간 절감·무인 경로를 증명하지 않습니다. (16) 최초 Claude 실행의 SIGINT 중단과 뒤 실행 결과를 구분합니다. 첫 no-index 검사에서 차이가 있다는 종료 코드 1을 오류로 오해한 기록도 지우지 않고 정정했습니다. 런타임 준비는 Codex, 설계 작성은 Claude, 세션 요약은 훅의 작업입니다. (17) 소유자 승인과 사용자의 공식 승격 승인은 확보됐습니다. 제품 구현과 실제 연결 증거는 각 카드가 소유합니다. 2026-10-31 결정에 따라 DE-00000074를 공식 기록으로 옮기되 현재 도구가 허용하는 종료 상태를 먼저 거칩니다. 범위 밖 변경 전체: .stage/.runtime/driver/logs/W-00000273-claude.metadata.json; .stage/.runtime/driver/logs/W-00000273-claude.stderr.txt; .stage/.runtime/driver/logs/W-00000273-claude.stdout.jsonl; .stage/.runtime/driver/logs/W-00000273-followup-prompt.md; .stage/.runtime/driver/logs/W-00000273-followup-runner.py; .stage/.runtime/driver/logs/W-00000273-followup.metadata.json; .stage/.runtime/driver/logs/W-00000273-followup.stderr.txt; .stage/.runtime/driver/logs/W-00000273-followup.stdout.jsonl; .stage/.runtime/driver/logs/W-00000273-prompt.md; .stage/.runtime/driver/logs/W-00000273-repair-prompt.md; .stage/.runtime/driver/logs/W-00000273-repair-runner.py; .stage/.runtime/driver/logs/W-00000273-repair.metadata.json; .stage/.runtime/driver/logs/W-00000273-repair.stderr.txt; .stage/.runtime/driver/logs/W-00000273-repair.stdout.jsonl; .stage/.runtime/driver/logs/W-00000273-review-prompt.md; .stage/.runtime/driver/logs/W-00000273-review-runner.py; .stage/.runtime/driver/logs/W-00000273-review.metadata.json; .stage/.runtime/driver/logs/W-00000273-review.stderr.txt; .stage/.runtime/driver/logs/W-00000273-review.stdout.jsonl; .stage/.runtime/driver/logs/W-00000273-runner.py; .stage/.runtime/driver/logs/W-00000273-verification-final.json; .stage/.runtime/driver/logs/W-00000273-verification.json; .stage/.runtime/driver/logs/W-00000273-verify.py; .stage/.runtime/driver/logs/W-00000273.md; .stage/.runtime/sessions/481a3c12-88ef-43e8-8667-1d7a24ce5ab5.md; .stage/decisions/index.md; .stage/work/current/W-00000272/W-00000273/_story.md; .stage/work/retrospectives/R-00000273.md. 특히 10월에 감독이 재생성한 .stage/decisions/index.md를 포함합니다.
Work not done: 이 보고 시점에는 새 닫기 리뷰, 공식 경로 이동과 promoted 기록이 남았습니다. 이 카드는 제품 구현이나 실제 AI 시험을 새로 실행하지 않습니다. O-00000049의 관측 종료, 데스크톱·Windows 실제 실행, 일반 성공률 검증과 첫 범위 밖 기능도 수행하지 않았습니다. 승인·설계·제품별 기존 검증과 이번 절차를 구별합니다.
```

## Verification

2026-11-01 재검토: 보고 계약과 설계 기준 두 개는 PASS였고, 첫 기준은 정상 Avatar snapshot을 프로젝트 키와 비교하도록 적은 문구 때문에 FAIL이었습니다. 이 지적을 `accept`합니다. 설계 6절의 거절 조건을 Distill과 Avatar로 나눠 기존 소유권·출력 계약 및 `handoff_producers.snapshot()`과 맞췄습니다. 코드 변경 없이 문서 모순을 고치고 재검토합니다.
2026-11-01: 앞선 닫기 리뷰가 설계 기준 세 개는 승인했지만 누적 실행 보고를 반려했다는 지적을 수용합니다(`accept`). 마지막 보고에 유지되는 모든 결정과 모든 실행의 범위 밖 경로를 합쳤습니다. 10월에 감독이 재생성한 `.stage/decisions/index.md`도 명시했습니다. 기존 보고는 보존하고 완전한 보고 한 개를 추가했습니다.
Stage 감사는 구조 검사입니다. 설계의 타당성과 소유자 승인까지 대신하지 않습니다.

`design` 종류의 통과 기준은 소유자의 리뷰와 승인입니다.
2026-10-05: 작업 소유자 Codex가 Claude와 다른 입장에서 수정본을 검토했고 성공 기준 3개 모두 통과로 판단했습니다. 판정 원본은 `.stage/.runtime/driver/reviews/W-00000273-owner.json`입니다.
기록 소유자와 공개 호출 경로, 확인·범위·변경·철회 처리, 두 저장소의 별도 실행과 검증 경계를 확인했습니다.
기존 경로에 기준 기능을 더하지 않는다는 문구는 정적 검사 오류 수정까지 금지한다는 뜻이 아니므로, 동작을 보존하는 수정은 허용한다고 명시했습니다.
설계를 채택했지만 종료 명령과 회고는 아직 실행하지 않았습니다. frontmatter의 완료 관련 표시는 그 절차 뒤에 갱신합니다.
실행 조건: 구현 카드를 드라이버로 돌리려면 따로 승인받은 설계 커밋이 필요합니다. novel-ai 구현 worktree에도 하네스 커밋 승인이 필요합니다.
수정 전 초안에서 실행한 검사 결과(2026-10-05):

- `python3 stage/scripts/audit_stage.py --project-root .`: 종료 코드 1, 오류 1개, 경고 32개. 경고는 보관 기록의 빈 성공 기준(WORK029)으로 등록 때와 같습니다. 오류는 `DECISION004`입니다. 새 DE-00000074가 생성형 인덱스 `.stage/decisions/index.md`에 아직 없습니다. 이 파일은 작성자의 쓰기 허용 경로 밖이라 감독이 `python3 stage/scripts/refresh_decision_index.py --project-root .`로 고쳐야 합니다.
- `git diff --check`: 출력 없음. 새 파일 두 개는 `git diff --no-index --check /dev/null <path>`로 따로 보았고 출력이 없었습니다.

수정본에서 다시 실행한 검사 결과(2026-10-05):

- 감사: 종료 코드 1, 오류 1개(`DECISION004`, 인덱스는 감독이 갱신할 몫), 경고 32개(WORK029). 수정 전과 같습니다. 구조 검사가 덜 끝난 상태이고, 제품 실패는 아닙니다.
- `git diff --check`와 새 파일 두 개의 `--no-index --check`: 출력 없음.

계약 수정 뒤 다시 실행한 검사 결과(2026-10-05):

- 감사: 오류 0개, 경고 32개(WORK029)입니다. `DECISION004`가 사라졌습니다. 작성자는 인덱스를 고치지 않았으므로 감독이 갱신한 결과로 봅니다.
- `git diff --check`와 새 파일 두 개의 `--no-index --check`: 출력 없음.
- 구조 검사와 공백 검사가 통과했을 뿐입니다. 설계 승인이나 `design` 검증 통과는 아닙니다.

### Executed at close — 2026-11-01

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

### Review at close — 2026-11-01

```
Review report: .stage/.runtime/driver/logs/W-00000273.md
Criteria:
- PASS: 각 기록을 어디에서 고치고 다른 플러그인이 어떻게 참조하는지 한 곳에서 확인할 수 있습니다
  Reason: 설계 3~7절이 원본 소유자, 수정 명령, 버전 참조와 읽기 전용 투영을 한 문서에 정합니다. 6절은 Distill의 project/key와 Avatar의 personal/personal을 따로 검사하며 현재 handoff_producers.snapshot()과 일치하므로 정상 개인 기준을 프로젝트 키 때문에 거부하던 문서 모순을 해결했습니다.
- PASS: 새 기준과 예외와 AI의 추정을 구별하고 이전 기준을 적용하지 않을 조건을 구체적인 사례로 검토합니다
  Reason: 설계 4·5·7·8·10절이 사용자 발언·확인과 AI 추정, 조건과 예외, 대체·철회·미확인·범위 불일치·조회 실패를 구별합니다. 높은 확신도의 미확인 기준, 변경된 출처, 철회 후 낮은 세대 투영, 부분 경로와 조건별 사례를 들어 적용하지 않을 조건과 재확인 절차를 정합니다.
- PASS: 두 저장소에서 각각 구현하고 검증할 범위와 순서가 정해져 구현자가 제품 역할을 다시 정할 필요가 없습니다
  Reason: 설계 5~7·10·11절이 Distill과 Avatar 구현 뒤 Stage 연결 및 양방향 실제 시험 순서를 정하고 저장소별 파일·검사·독립 리뷰·결과 기록 책임을 나눕니다. 승인 당시 드라이버 계획과 사용자 승인 후 직접 실행을 구별하며 외부 결과를 noory-ai 드라이버 검증으로 주장하지 않습니다.
- PASS: Purpose and scope-boundary reporting contract
  Reason: 마지막 Executor report의 Decisions made와 Work not done은 비어 있지 않고 유지되는 결정과 이번 문서 수정 이유, 남은 종료·공식 승격 절차 및 미실행 검증을 구별합니다. 일곱 보고의 누적 경로 30개와 이번 지정 경로 3개를 모두 포함하며 결정 인덱스 갱신을 비롯한 범위 밖 경로 28개를 명시합니다. 설계 목적에 필요한 변경이며 제품 코드나 설정을 이번에 바꿨다고 주장하지 않습니다.
```

## Retrospective

[R-00000273](../../../retrospectives/R-00000273.md).

## Promotion decision

2026-10-31 사용자 결정에 따라 DE-00000074 를 공식 기록으로 올린다. 닫은 뒤 `.stage/official/decisions/records/DE-00000074.md` 로 옮긴다.
