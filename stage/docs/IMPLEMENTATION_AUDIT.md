# Stage 구현 감사

이 문서는 설계도 대비 현재 구현 상태를 기록한다.

## 결론

현재 구현은 Stage의 첫 실행 루프를 만든 상태다. 설계도 전체가 구현 완료된 상태는 아니다.

완료된 범위는 `.stage/` 산출물 구조, 초기화 헬퍼, 진입 스킬, 감사 CLI, Claude 호환 훅, 기본 완료 게이트다.

## 구현된 범위

| 영역 | 상태 | 근거 |
|---|---|---|
| 산출물 구조 | 구현됨 | `templates/project-stage/` |
| 초기화 | 구현됨 | `scripts/init_stage.py` |
| 감사 CLI | 구현됨 | `scripts/audit_stage.py` |
| 진입 스킬 | 구현됨 | `skills/stage-init`, `skills/stage-audit`, `skills/stage-decision`, `skills/stage-retrospective` |
| Claude 훅 | 구현됨 | `hooks/hooks.json`, `hooks/stage_guard.py` |
| 삭제 게이트 | 구현됨 | `.stage` 전체 삭제 차단 |
| 승격 게이트 | 구현됨 | `.stage/.runtime/intents/<work-item>.json` + 완료된 작업 항목 확인 |
| Archive 게이트 | 구현됨 | `type: archive` intent + completed/rejected 작업 항목 확인 |
| 등재 게이트 | 구현됨 | 소스 수정 전 `present/work/items/` active 작업 항목 확인 |
| 커밋 게이트 | 구현됨 | staged 소스, 같은 명령의 `git add` 대상, `git commit -a` 대상의 작업 항목 등재와 completed blocker 확인 |
| Stop 인계 | 구현됨 | Stop 시 세션 요약 기록 |
| 이식성 게이트 | 구현됨 | `.stage` 내부 OS 전용 스크립트 차단 |
| 산출물 패밀리 구조 | 구현됨 | 색인 문서, 개별 기록 디렉터리, `operations/artifacts.md` 분리 |
| Archive 거처 | 구현됨 | `past/work/archive/items/` + `past/work/archive/retrospectives/`와 감사 규칙 |
| 거버넌스 범위 | 구현됨(확정) | 광역 기본(거의 모든 파일) + `settings.json` 제외 목록. 파손 시 fail-closed. 협소화는 감사 GOV000-002로 가시화 |
| 작업 계층 | 구현됨(확정) | `parent` 필드 + 훅 차단(부모 부재·자기 참조·닫힌 부모 아래 자식) + 감사 WORK017-019, BACKLOG002 |
| 작업 분류·검증 | 구현됨(확정) | `kind` 필드 + `operations/verification.md` kind별 `passed` 기준 표 + 감사 KIND001 |
| 계보 | 구현됨(확정) | B↔W 양방향(`source`/`realized_by`) + state `work_items` — 감사 WORK020, BACKLOG004/005, STATE001 |
| 결정 기록 | 구현됨(확정) | `present/work/decisions/` 패밀리 + `decision_refs` 역링크 + 원칙 인용 강제(WORK014-016, WORK021/022) |
| 원칙 코어 고정 | 구현됨 | canon 코어(사고·완료·행위) 삭제 시 감사 CANON001 error + SessionStart 코어 원칙 요약 주입 |
| 질문 게이트 | 구현됨 | `AskUserQuestion` 직전 목적·원칙 상기 1회 리마인드(재질문 통과) |
| 산출물 카탈로그 | 구현됨(확정) | `operations/artifacts.md` §Artifact catalog + FAMILY001(형태 발명 warning) + SessionStart 압축 맵 주입 |
| 언어 규칙 | 구현됨 | 실행 자산 전부 영어(CLAUDE.md §Language), `docs/`·`.discuss/`만 한국어(사용자 승인 예외) |
| Codex 훅 호환 | 구현됨(확정) | 동일 `hooks/hooks.json`을 Codex가 자동 발견 + 출력·도구명 계약 정렬 + 신뢰 승인 후 e2e(deny→등재→허용→Stop) 확인 — `hooks/README.md` §Host contract |
| 다중 세션 `.runtime/` | 구현됨 | intent·세션 요약·질문 마커의 세션/항목 차원 분리 — `hooks/README.md` §Runtime concurrency |

## Phase A: Discovery

| # | Severity | 문제 | 근거 | 영향 | 해결 방향 |
|---|:---:|---|---|---|---|
| P1 | ✅ Closed | ~~Codex에서 런타임 훅 강제가 검증되지 않았다.~~ | Codex hooks 기능이 플러그인 `hooks/hooks.json`을 자동 발견·실행(별도 어댑터 불필요, 소스+`hooks/list` 실측). 호환 버그 3건 수정 후 사용자 TUI 신뢰 승인, e2e로 deny→등재→허용→Stop 요약 전 사이클 확인. e2e 중 라이브 버그 2건(빈 parent 정규식·패치 본문 셸 해석) 추가 수정. | — | 계약 정본 = `hooks/README.md` §Host contract. 잔여 배포 결정(마켓플레이스 등재)은 사용자 몫. |
| P2 | 🟡 Gap | 의사결정 통제 대부분이 문서/스킬 지침이고 자동 게이트가 아니다. | 설계도는 질문, 실행, 중단, 단순화, 추상화, 승격, 회고 게이트를 정의한다. 현재 훅은 명확한 파일/명령 위반만 차단한다. | 원칙 적용이 모델 자율성에 남아 장기 프로젝트 일관성이 약해질 수 있다. | `stage-decision` 결과를 구조화된 기록으로 남기고, 필수 필드 누락을 훅 또는 CLI로 검증한다. |
| P3 | 🟡 Gap | SessionStart 컨텍스트 주입이 얕다. | 현재 상태, 진행 작업, 검토 대기, 이전 세션만 주입한다. | `past/canon`, `past/model`, `future`, `operations`를 충분히 읽지 못해 상위 목적 판단이 약해진다. | 컨텍스트 예산 규칙을 만들고 `past` 정본과 열린 질문을 우선순위 기반으로 주입한다. |
| P4 | 🟡 Gap | SSOT/MECE 위반 검출이 아직 기본 구조 감사에 머문다. | `audit_stage.py`는 템플릿 누락, enum, 완료 blocker, 색인, archive 위치를 검사한다. 정본 중복, 책임 경계 충돌, 의미 중복은 아직 검출하지 않는다. | 문서가 쌓일수록 정본 충돌과 책임 경계 붕괴가 생길 수 있다. | 감사 CLI에 라우팅 충돌, 중복 소유, 정본 후보 누락 검사를 추가한다. |
| P5 | ✅ Closed | ~~회고 산출물의 단위와 저장 위치가 아직 약하다.~~ | `operations/retrospective.md`는 규칙이고, 실제 작업별 회고 파일 구조는 없었다. | “항상 회고” 원칙이 기록 양식 없이 약해질 수 있었다. | `present/work/retrospectives/` 구조로 보정함. |
| P6 | ✅ Closed | ~~훅 판단이 Markdown 표의 상태 문자열에 의존한다.~~ | `완료`, `통과`, `보류` 같은 문자열을 정규식으로 해석했다. | 표현이 달라지면 게이트가 열리거나 닫히는 오판 가능성이 있었다. | `present/work/items/*.md` 프론트매터 enum으로 보정함. |
| P7 | ✅ Closed | ~~백로그와 다른 산출물 영역을 단일 문서 중심으로 과소설계했다.~~ | `future/backlog.md`, `future/roadmap.md`, `present/*/*.md`가 본문과 색인 역할을 겸할 수 있었다. | 문서가 커질수록 SSOT, MECE, 이력, 우선순위 관리가 붕괴할 수 있었다. | 산출물 패밀리를 `index` + `items/records` + `_template` + `views`로 분리함. |
| P8 | ✅ Closed | ~~완료·회고 게이트가 등재된 작업에만 적용된다.~~ | 미등재 소스 수정이 가능하면 하네스가 옵트인이 됐다. | 회고 필수와 부분 완료 금지가 자율 규칙으로 약해질 수 있었다. | 소스 수정 전 active 작업 항목 등재를 차단 게이트로 추가함. |
| P9 | ✅ Closed | ~~승격 게이트가 본문 마커에 의존한다.~~ | `[stage-promote]`나 `승격` 문자열이 공식 산출물 본문을 오염시킬 수 있었다. | `past`의 evergreen 문서 원칙과 충돌했다. | `.stage/.runtime/promote-intent.json` 대역 외 신호로 변경함. |
| P10 | ✅ Closed | ~~커밋·Stop 게이트 의미론이 장기 프로젝트와 충돌한다.~~ | 미완료 작업 전체를 기준으로 커밋/중단을 막으면 중간 커밋과 세션 인계가 어려웠다. | 상태 조작을 유도할 수 있었다. | 커밋은 대상 소스 등재와 completed blocker 확인으로 두고, Stop은 요약 기록으로 변경함. |
| P11 | ✅ Closed | ~~셸 경로에서 등재·승격 게이트가 우회된다.~~ | redirect, append redirect, cp, mv, tee, sed -i 같은 셸 쓰기 경로가 Write 도구 게이트를 지나지 않았다. | 하네스 강제가 도구 선택에 따라 사라졌다. | 셸 쓰기 대상 추출과 git 복합 명령 추정을 추가함. 인라인 인터프리터 쓰기는 best-effort 감지 범위 밖으로 문서화함. |
| P12 | ✅ Closed | ~~작업 scope 기본값이 fail-open이다.~~ | `scope: .` 또는 빈 scope가 전체 경로와 매칭될 수 있었다. | 작업 항목 하나로 모든 소스 변경이 통과했다. | 빈 scope와 `.`은 매칭 없음, 전역은 `*`만 허용하도록 변경함. |
| P13 | ✅ Closed | ~~설계도 공간축과 상태 어휘가 구현과 어긋난다.~~ | §5 공간축, §6 상태 전이, §9 게이트 목록이 현재 템플릿/스킬과 완전히 일치하지 않았다. | 설계도 대비 감사의 기준이 흔들렸다. | 공간축, 작업 상태 enum, 의사결정 8게이트를 현재 구현과 맞춤. |
| P14 | ✅ Closed | ~~완료 산출물의 수명 종점과 index↔item 불일치 감지가 없다.~~ | `archived` 상태는 있으나 물리적 거처와 검출 규칙이 없었다. | present가 장기적으로 누적되고 SSOT 불일치가 조용히 생길 수 있었다. | `past/work/archive/items/`와 `audit_stage.py` 색인·archive 검사로 보정함. |
| P15 | ✅ Closed | ~~감사 CLI가 설계된 사용법을 오탐한다.~~ | 전체 텍스트에서 `문자-숫자` 패턴을 작업 항목 ID로 해석해 회고 링크와 SHA 표기를 오류로 처리했다. | 감사가 올바른 사용을 막아 우회 대상이 될 수 있었다. | 작업 항목 참조를 `items/*.md` 링크로 한정하고 템플릿 누락은 warning으로 낮춤. |
| P16 | ✅ Closed | ~~rejected 작업을 archive로 보관할 실행 경로가 없다.~~ | `past/work/archive/` 쓰기가 승격 게이트에 묶여 completed/approved만 허용했다. | rejected 항목이 present에 남거나 상태 위조를 유도할 수 있었다. | `type: archive` intent를 추가하고 completed/rejected 보관을 허용함. |
| P17 | ✅ Closed | ~~canon 단일 문서와 index 라우팅 표의 책임 경계가 불완전하다.~~ | canon 상위 `*.md`가 상세 본문 소유처럼 보였고, operations 라우팅 일부가 index에 없었다. | SSOT와 MECE 감사 기준이 흐려질 수 있었다. | canon 상위 문서를 색인/요약으로 명명하고 operations 라우팅을 보강함. |
| P18 | ✅ Closed | ~~승격 intent의 work_item이 대상 paths와 바인딩되지 않는다.~~ | 완료된 임의 작업 항목 하나가 past 전체 수정의 만능 열쇠가 될 수 있었다. | 승격 게이트가 공식 산출물 보호 장치로 기능하지 못한다. | 일반 승격은 work item `promotes` 경로와 일치해야 하고, archive는 대상 파일명과 work_item ID가 일치해야 한다. |
| P19 | ✅ Closed | ~~의사결정 통제 축의 실체가 아직 약하다.~~ | `stage-decision`은 8게이트를 정의하지만 결정 기록 스키마와 검사 지점이 없었다. | Stage의 두 축 중 의사결정 통제가 산문에 머물렀다. | `present/work/decisions/` 패밀리(`DE-*`, `work_item` 역링크, status enum)와 감사 WORK014/015/016으로 보정함. 훅 수준 강제(예: 결정 없는 completed 차단)는 과차단 위험이 있어 감사 검사로 한정 — 확장 여부는 토론. |
| P20 | ✅ Closed | ~~다중 호스트/다중 세션 런타임 동시성 설계가 없다.~~ | 단일 슬롯 3종을 다중화(Codex 라운드 11, Finding 13건 반영 후 클린): intent = **(작업 항목, 정규화 경로)당 1파일**(`intents/<item>--<basename>-<digest>.json`, CLI로만 생성) + 소비 = **rename 원자 예약**(경합 패자 deny), 경로별 후보 2개↑는 모호성 deny, 레거시 lazy migration. 세션 요약 = `sessions/<session_id>.md`(keep 5 + 방금 쓴 파일 고정 + 24h 신선 보존 — 시계 스큐 하 soft cap), SessionStart는 최신 1개 주입. 질문 마커 = `question-ack/<session_id>`(1일 경과분 정리). 세션 차원 = 양 호스트 훅 stdin의 `session_id`(부재 시 `default`). | — | 계약 = `hooks/README.md` §Runtime concurrency. |
| P21 | ✅ Closed | ~~회고 완료가 회고 산출물과 연결되지 않는다.~~ | `retrospective: completed`는 R 파일 존재와 연결을 요구하지 않았다. | 회고 필수가 자기 인증으로 퇴화할 수 있었다. | `retrospective_ref`와 회고 파일 `work_item` 역링크를 감사 CLI가 검증함. |
| P22 | ✅ Closed | ~~언어 전략이 결정되지 않았다.~~ | 템플릿·스킬·훅 메시지·스크립트가 한국어였고 규칙 SSOT(noory-ai/CLAUDE.md §Language)와 어긋났다. | 배포 형식과 산출물 언어가 불일치했다. | 실행 자산 전부 영어로 전환함. 예외(사용자 승인): `docs/` 3종과 `.discuss/`는 한국어 — `.discuss/stage-language-decision-2026-07-09.md`. |
| P23 | ✅ Closed | ~~archived 작업의 회고가 present에 영구 체류한다.~~ | 회고 ref 해석이 항상 `present/work/retrospectives/`를 향해 archive 항목의 R 파일이 present에 남아야 했다. | "present = 작업 중" 의미가 회고 차원에서 침식됐다. | `past/work/archive/retrospectives/` 추가, ref를 항목 위치 기준으로 해석, archive intent가 R 파일 동반 이동을 허용(파일명 = `retrospective_ref` 바인딩). |
| P24 | ✅ Closed | ~~BLUEPRINT·DISCUSSION이 신규 구조를 반영하지 못했다.~~ | 결정 기록 패밀리, archive retrospectives, settings 거버넌스, 계층/계보가 다이어그램·논의에 없었다. | 설계도 대비 감사 기준이 lag 상태였다. | §4에 decisions·archive retrospectives·settings 노드, §15에 거버넌스·계층·질문 게이트를 반영하고 DISCUSSION에 보편성·계층·원칙 배선 절을 추가함. |
| P25 | ✅ Closed | ~~보편성·계층·원칙 배선의 확정 범위가 토론 대상이다.~~ | 초안이 토론 없이 굳을 수 있었다. | 사용자 의도와 다른 고착 위험이 있었다. | `.discuss/stage-universality-hierarchy-2026-07-09.md`에서 논점 13건 전부 확정(사용자 결정 9건 + 원칙 도출 4건) 후 구현 배치 2로 반영함 — 광역 거버넌스 기본, 계층 훅 차단, B↔W 계보, kind 검증 선언, 코어 원칙 고정, DE 원칙 인용 강제, 코어 원칙 주입, 질문 게이트, 8자리 ID. |
| P26 | 🟡 Gap | SessionStart 컨텍스트 예산의 나머지 절반이 남았다. | 코어 원칙 요약·산출물 맵은 주입되지만 열린 질문·selected 백로그 등 present/future 우선순위 주입은 없다. | 세션이 계획·불확실성을 이어받지 못한다(P3의 잔여). | 컨텍스트 예산 규칙을 설계해 질문 상위 K개·selected 백로그를 주입한다. |
| P27 | 🟡 Gap | 소비측 컨텍스트(스킬·룰·인스트럭션) 활용 배선이 없다. | 사용자 지시(2026-07-10): 계획·실행 시 플러그인을 설치한 프로젝트에 정의된 스킬·룰·기타 인스트럭션을 적극 활용해야 하고(없어도 동작이 목표), 그 컨텍스트가 잘못됐다고 판단되면 적극 수정 요청해야 한다. 현재 스킬·훅은 `.stage/`만 읽는다. | 호스트 프로젝트의 기존 규범과 Stage 판단이 병렬로 놀아 일관성이 갈라질 수 있다. | 소비측 컨텍스트 발견·활용 규칙 + 오류 판단 시 수정 요청 루프를 설계한다. 사용자 지정: 큐의 마지막 작업. |

## 바로 보정한 항목

| 항목 | 보정 |
|---|---|
| 백로그와 주요 산출물이 단일 파일 중심이던 문제 | 색인과 개별 기록 디렉터리를 분리하는 산출물 패밀리 구조로 변경 |
| 본문 마커 승격 문제 | 승격 의도를 `.stage/.runtime/promote-intent.json`으로 분리 |
| 미등재 소스 수정 문제 | active 작업 항목 scope와 연결된 경우만 허용 |
| Stop 과차단 문제 | Stop은 인계 요약을 남기고 허용 |
| 셸 우회 문제 | redirect, cp, mv, tee, sed -i 대상 경로를 등재/승격 게이트에 연결 |
| append redirect 문제 | `>>` 대상 경로를 등재 게이트에 연결 |
| past 읽기 과차단 | 승격 게이트 입력을 쓰기 대상 경로로 한정 |
| scope fail-open 문제 | 빈 scope와 `.`을 매칭 없음으로 변경하고 `*`만 전역으로 허용 |
| archive 거처 부재 | `past/work/archive/items/` 추가와 감사 CLI 검사 연결 |
| 설계도 lag | 공간축, 작업 상태 전이, 의사결정 게이트 명칭을 구현과 일치시킴 |
| 감사 CLI 오탐 | 작업 항목 링크만 색인 참조로 해석하고 회고 링크와 산문 패턴을 제외 |
| rejected archive 불가 | archive intent를 승격 intent와 분리 |
| canon/index 책임 경계 | canon 상위 파일은 색인/요약으로 제한하고 operations 라우팅 누락을 보강 |
| 승격 만능 열쇠 문제 | 일반 승격은 `promotes`, archive는 파일명 ID로 work_item과 대상 경로를 바인딩 |
| 회고 자기 인증 문제 | `retrospective_ref`와 회고 파일 `work_item` 역링크를 감사 CLI 검사로 연결 |
| 깨진 settings.json fail-open (Codex 리뷰) | settings.json이 존재하나 파싱 불가면 `.stage` 밖 쓰기를 deny하는 fail-closed로 변경 (settings 자체 수리는 허용) |
| apply_patch 경로 미추출 (Codex 리뷰) | 패치 본문의 `*** Add/Update/Delete File:`·`*** Move to:` 경로를 추출해 등재·승격 게이트에 연결 |
| BACKLOG003 회귀 테스트 부재 (Codex 리뷰) | 파일명-ID 불일치 단독 테스트 추가 |
| 계층 훅 MultiEdit/apply_patch 우회 (Codex 재검증) | 계층 검증 입력을 "수정 후 파일 텍스트"로 정규화 — MultiEdit edits·apply_patch 본문을 투영해 판정 |
| 계층 훅 부분 수정 과차단 (Codex 재검증) | 기존 파일에 편집을 적용한 투영 텍스트로 parent/status 판단 — completed 자식의 parent 부분 수정 allow |
| apply_patch `Move to:` 계층 우회 (Codex 재검증 2차) | Move 대상 섹션을 투영 대상으로 인식 — source 기존 텍스트 + hunk를 새 경로의 투영 텍스트로 연결 |
| MultiEdit 조각 순차 미적용 (Codex 재검증 2차) | 미매칭 조각을 즉시 투영 텍스트에 선반영해 이후 edit가 순차 적용되게 수정 |
| allow 출력이 Codex에서 훅 실패로 기록 (P1) | Codex는 `permissionDecision:"allow"`(updatedInput 없음)를 unsupported로 처리 — allow를 빈 출력(exit 0, stdout 없음)으로 변경. 양 호스트 공통 계약 |
| Stop 출력이 Codex에서 파싱 실패 (P1) | Codex Stop 파서는 `decision`을 리터럴 `"block"`만 수용 — `{"continue":true,"decision":"approve"}`를 `systemMessage` 단독(또는 빈 출력)으로 변경 |
| 질문 게이트가 Codex 질문 도구를 미인지 (P1) | Codex 질문 도구명 `request_user_input`을 matcher와 `QUESTION_TOOLS`에 추가 |
| 워크스페이스 root env 허구 계약 (P1) | Codex는 워크스페이스 env를 설정하지 않음(훅 cwd + payload `cwd`가 계약) — 미검증 `CODEX_WORKSPACE_ROOT` 분기 제거 |
| 테스트가 시스템 python3(3.9.6)에서 import 실패 (Codex 라운드 9) | 훅 테스트에 `from __future__ import annotations` 추가 — 훅은 호스트의 임의 `python3`로 돌므로 guard 본체와 같은 지연 평가 계약. 3.9.6에서 99건 통과 재현 |
| 빈 `parent:` 프론트매터 false deny (Codex e2e) | `frontmatter_field_from_text`의 `\s*`가 줄바꿈을 넘어 다음 줄을 값으로 캡처 → `[ \t]*`로 교정 |
| 패치 본문 셸 해석·본문 경로 과추출 (Codex e2e) | 셸 의미론을 SHELL_TOOLS로 한정, 게이트 입력을 실제 쓰기 대상으로 축소(본문 문자열 스캔 제거) — 본문 언급만으로 등재/삭제 게이트가 발화하던 과차단 제거 |

## 다음 구현 단위

1. SessionStart 컨텍스트 예산 잔여(P26) — 열린 질문·selected 백로그 우선순위 주입.
2. 감사 CLI에 정본 중복, 책임 경계 충돌, 라우팅 누락 검사 추가(P4).
3. 소비측 컨텍스트 활용 + 수정 요청 루프(P27) — 사용자 지정: 마지막 작업.
