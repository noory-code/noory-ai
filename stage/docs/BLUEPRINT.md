# Stage Mermaid 설계도

이 문서는 Stage 설계도를 Mermaid 차트 중심으로 정리한다.

## 1. 전체 지도

```mermaid
mindmap
  root((Stage))
    Mission
      "LLM 수행 지속성"
      "문맥 질서"
      "행위 통제"
      "산출물 승격"
      "호스트/플랫폼 독립성"
    Principles
      SSOT
      MECE
      "Fail Fast"
      AHA
      KISS
    Lifecycle
      Official
      Current
      Planned
    Operations
      Before
      During
      After
      Retrospective
    Spaces
      canon
      model
      decisions
      archive
      work
      state
      operations
```

## 2. 큰 시간축

```mermaid
timeline
  title Stage 산출물 지위 (라이프사이클: 게이트가 강제)
  Official : 공식 산출물
           : 신뢰 가능한 정본
           : 승격된 결정
  Current : 작업 중 산출물
          : 임시 판단
          : 열린 질문
  Planned : 계획
          : 제안
          : 후보 작업
```

## 3. 개별 시간축

```mermaid
flowchart LR
  Before["Before\n목적 확인\n정본 확인\n성공 기준 확인"]
  During["During\n판단\n분기\n실패 처리\n실행"]
  After["After\n검증\n완료 판단\n승격 또는 보류"]
  Retrospective["Retrospective\n회고\n원칙 적용 평가\n개선점 기록"]

  Before --> During --> After --> Retrospective
```

## 4. 공간축

```mermaid
flowchart TB
  Stage[".stage/"]

  Stage --> Official["official\n공식 지위 (승격된 정본)"]
  Stage --> Work["work\n작업 카드 라이프사이클"]
  Stage --> DecisionsF["decisions\npending 결정"]
  Stage --> State["state\n작업 중 상태"]
  Stage --> Proposals["proposals\n제안"]
  Stage --> Roadmap["roadmap\n테마 / 마일스톤"]
  Stage --> Operations["operations\n행위 규칙"]
  Stage --> Settings["settings.json\n거버넌스 범위\n광역 기본 + 제외 목록"]

  Official --> Canon["canon\n원칙 / 용어 / 불변 조건"]
  Official --> Model["model\n구조 / 경계 / 인터페이스"]
  Official --> Decisions["decisions\n승격된 결정"]
  Official --> Archive["work/archive\n보관된 작업 기록 + 회고"]

  Canon --> CanonRecords["*/\n개별 원칙 / 용어 / 불변 조건"]
  Model --> ModelRecords["components / boundaries / interfaces"]
  Decisions --> DecisionRecords["records\n개별 결정 SSOT (DE- id 유지)"]
  Archive --> ArchiveRecords["items / retrospectives\n보관 작업 기록과 회고"]

  Work --> Planned["planned\n계획 카드 + views (planned 보조 뷰)"]
  Work --> Current["current\nactive / review 카드"]
  Work --> Retros["retrospectives\n회고 기록"]
  Work --> WorkViews["active.md / review.md\ncurrent 뷰"]

  DecisionsF --> Pending["pending\n작업 중 결정 (DE-)"]

  State --> StateRecords["observations / questions / assumptions / risks\nwork_items로 작업 연결"]

  Roadmap --> RoadmapThemes["themes\nTH- 테마 (체인에서 상태 계산)"]
  Roadmap --> RoadmapMilestones["milestones\nM- 마일스톤 (닫기 시 기저 동결)"]
  Proposals --> ProposalRecords["P-\n개별 제안"]

  Operations --> BeforeOps["before"]
  Operations --> DuringOps["during"]
  Operations --> AfterOps["after"]
  Operations --> RetrospectiveOps["retrospective"]
  Operations --> OutputOps["output"]
  Operations --> ArtifactOps["artifacts"]
  Operations --> DocOps["documentation"]
  Operations --> VerifyOps["verification"]
  Operations --> BacklogOps["backlog"]
  Operations --> HookOps["hooks"]
```

## 5. 세 축의 결합

```mermaid
flowchart TB
  subgraph Global["큰 시간축: 산출물 지위"]
    GOfficial["Official\n공식"]
    GCurrent["Current\n작업 중"]
    GPlanned["Planned\n계획"]
  end

  subgraph Local["개별 시간축: 작업 흐름"]
    LBefore["Before\n입력 결정"]
    LDuring["During\n실행 통제"]
    LAfter["After\n지위 결정"]
  end

  subgraph Space["공간축: 책임 위치 (라이프사이클은 게이트가 부여)"]
    SCanon["official/canon"]
    SModel["official/model"]
    SDecisions["official/decisions/records"]
    SArchive["official/work/archive"]
    SCurrent["work/current"]
    SRetro["work/retrospectives"]
    SPending["decisions/pending"]
    SState["state"]
    SPlanned["work/planned + work/views"]
    SProposal["proposals"]
    SRoadmap["roadmap (고정; 상태는 결정 체인에서 파생)"]
    SOps["operations"]
  end

  GOfficial --> LBefore
  GPlanned --> LBefore
  LBefore --> LDuring
  LDuring --> GCurrent
  GCurrent --> LAfter
  LAfter --> GOfficial
  LAfter --> GPlanned

  GOfficial --> SCanon
  GOfficial --> SModel
  GOfficial --> SDecisions
  GOfficial --> SArchive
  GCurrent --> SCurrent
  GCurrent --> SRetro
  GCurrent --> SPending
  GCurrent --> SState
  GPlanned --> SPlanned
  GPlanned --> SProposal
  GOfficial -.-> SRoadmap
  GCurrent -.-> SRoadmap
  GPlanned -.-> SRoadmap
  SOps --> LBefore
  SOps --> LDuring
  SOps --> LAfter
```

## 6. 작업 항목 상태 전이

작업 항목 상태 enum의 SSOT는 `operations/artifacts.md`다. `work/current/README.md`는 같은 값을 참조한다.

```mermaid
stateDiagram-v2
  [*] --> captured
  captured --> triaged
  triaged --> ready
  ready --> selected
  selected --> active: start_work.py (planned work/planned -> current work/current)
  captured --> rejected_planned: 착수 전 폐기
  active --> blocked: 진행 차단
  blocked --> active: 차단 해소
  active --> review: 검증 요청
  review --> active: 재작업
  review --> rejected: 폐기
  review --> completed: 검증·회고·승격 판단 완료
  completed --> archived: 현재 작업 흐름에서 제거
  rejected --> archived: 기록 보관
  rejected_planned --> archived: 기록 보관
  archived --> [*]
```

계획 단계(`captured`/`triaged`/`ready`/`selected`)는 `work/planned/`에 있고, `start_work.py`가
`work/current/`의 `active`로 이동시킨다. 착수 전 폐기(`rejected`)는 계획 카드에서도 일어난다.

`archived` 이동은 승격과 다르다. `official/work/archive/` 대상은 archive intent로 보관하며, rejected 작업도 보관할 수 있다.

## 7. 요청 처리 흐름

```mermaid
sequenceDiagram
  participant User as 사용자
  participant Stage as Stage
  participant Context as Context
  participant Hero as LLM Hero
  participant Verify as Verification
  participant Retro as Retrospective
  participant Artifact as Artifact

  User->>Stage: 요청
  Stage->>Context: Official / Current / Planned 확인
  Context-->>Stage: 정본, 상태, 계획 반환
  Stage->>Stage: 질문 필요성 판단
  Stage->>Hero: 원칙과 컨텍스트 제공
  Hero->>Artifact: 작업 중 산출물 생성
  Artifact->>Verify: 검증 요청
  Verify-->>Stage: 통과 또는 보류
  Stage->>Retro: 작업 회고
  Retro-->>Stage: 원칙 적용 평가와 개선점
  Stage->>Artifact: 공식 승격 또는 재작업
```

## 8. 원칙 적용 위치

```mermaid
flowchart LR
  Principles["원칙\nSSOT / MECE / Fail Fast / AHA"]
  Context["컨텍스트\nOfficial / Current / Planned"]
  Harness["하네스\n질문 / 분기 / 실패 / 검증"]
  Product["산출물\n작업 중 결과"]
  Gate["게이트\n완료 / 승격 / 보류"]
  Retro["회고\n원칙 적용 평가\n개선점"]
  Official["공식 산출물\nOfficial"]
  Feedback["환류\nCurrent 또는 Planned"]

  Principles --> Harness
  Context --> Harness
  Harness --> Product
  Product --> Gate
  Gate -->|통과| Retro
  Retro --> Official
  Gate -->|불충분| Feedback
  Feedback --> Context
```

## 9. 의사결정 통제

```mermaid
flowchart TB
  DecisionPoint["Decision Point\n선택의 기로"]

  DecisionPoint --> PurposeGate["Purpose Gate\n상위 목적 확인"]
  DecisionPoint --> TruthGate["Truth Gate\n검증된 사실과 모름 분리"]
  DecisionPoint --> QuestionGate["Question Gate\n사용자 결정 필요성 판단"]
  DecisionPoint --> CoverageGate["Coverage Gate\nMECE 확인"]
  DecisionPoint --> OwnershipGate["Ownership Gate\nSSOT 위치 확인"]
  DecisionPoint --> FailureGate["Failure Gate\n깨진 가정과 불완전 처리 노출"]
  DecisionPoint --> PromotionGate["Promotion Gate\n검증된 산출물만 승격"]
  DecisionPoint --> RetroGate["Retrospective Gate\n다음 실행 변화 기록"]

  Principles["원칙\nSSOT / MECE / Fail Fast / AHA / KISS"]
  Context["컨텍스트\nOfficial / Current / Planned"]
  Priority["우선 가치\n진실성 / 사용자 의도 / 프로젝트 본질 / 완료 안정성"]

  Principles --> DecisionPoint
  Context --> DecisionPoint
  Priority --> DecisionPoint

  PurposeGate --> Outcome["결정 결과"]
  TruthGate --> Outcome
  QuestionGate --> Outcome
  CoverageGate --> Outcome
  OwnershipGate --> Outcome
  FailureGate --> Outcome
  PromotionGate --> Outcome
  RetroGate --> Outcome

  Outcome --> Current["Current\n작업 중 산출물"]
  Outcome --> Official["Official\n공식 산출물"]
  Outcome --> Planned["Planned\n계획 또는 제안"]
```

## 10. Stage 하네스의 두 축

```mermaid
flowchart LR
  Stage["Stage Harness"]

  Stage --> ArtifactAxis["산출물 구조화"]
  Stage --> DecisionAxis["의사결정 통제"]

  ArtifactAxis --> GlobalTime["큰 시간축\nOfficial / Current / Planned"]
  ArtifactAxis --> LocalTime["개별 시간축\nBefore / During / After"]
  ArtifactAxis --> SpaceAxis["공간축\ncanon / model / decisions / work / state / operations"]

  DecisionAxis --> DecisionPoint["Decision Point\n선택의 기로"]
  DecisionAxis --> Principles["Principles\n판단 기준"]
  DecisionAxis --> Priority["Priority\n충돌 시 우선 가치"]
  DecisionAxis --> Gates["Gates\nPurpose / Truth / Question / Coverage / Ownership / Failure / Promotion / Retrospective"]
  DecisionAxis --> Retro["Retrospective Gate\n작업 후 회고"]
  DecisionAxis --> Learning["Learning\n원칙과 컨텍스트 개선"]

  ArtifactAxis --> HookLayer["Runtime Hooks\n문맥 주입 / 차단 / 세션 요약"]
  DecisionAxis --> HookLayer
  HookLayer --> SessionStart["SessionStart\nStage 문맥 주입"]
  HookLayer --> PreToolUse["PreToolUse\n규칙 위반 차단"]
  HookLayer --> PostToolUse["PostToolUse\n승격 의도 2단계 완료"]
  HookLayer --> Stop["Stop\n세션 요약 기록"]

  GlobalTime --> StableExecution["지속 가능한 수행"]
  LocalTime --> StableExecution
  SpaceAxis --> StableExecution
  DecisionPoint --> StableExecution
  Principles --> StableExecution
  Priority --> StableExecution
  Gates --> StableExecution
  Retro --> StableExecution
  Learning --> StableExecution
  HookLayer --> StableExecution
```

## 11. 첫 완성 단위

```mermaid
flowchart TB
  CompleteUnit["첫 완성 단위"]

  CompleteUnit --> Structure[".stage/ 산출물 구조"]
  CompleteUnit --> Routing["index.md 라우팅 규칙"]
  CompleteUnit --> ItemRecords["개별 산출물 파일\nitems / records / templates"]
  CompleteUnit --> ArtifactRules["operations/artifacts.md\n산출물 패밀리 규칙"]
  CompleteUnit --> Before["operations/before.md"]
  CompleteUnit --> During["operations/during.md"]
  CompleteUnit --> After["operations/after.md"]
  CompleteUnit --> Retrospective["operations/retrospective.md"]
  CompleteUnit --> Hooks["operations/hooks.md\nSessionStart / PreToolUse / Stop"]
  CompleteUnit --> Promotion["current -> official 승격 규칙"]
  CompleteUnit --> PlannedGuard["planned/proposals는 공식 진실이 아님"]
  CompleteUnit --> CompletionGate["부분 완료 금지\n첫 단위부터 닫힌 루프"]

  Structure --> ClosedLoop["닫힌 루프"]
  Routing --> ClosedLoop
  ItemRecords --> ClosedLoop
  ArtifactRules --> ClosedLoop
  Before --> ClosedLoop
  During --> ClosedLoop
  After --> ClosedLoop
  Retrospective --> ClosedLoop
  Hooks --> ClosedLoop
  Promotion --> ClosedLoop
  PlannedGuard --> ClosedLoop
  CompletionGate --> ClosedLoop
```

## 11-1. 산출물 패밀리 원칙

```mermaid
flowchart TB
  Family["산출물 패밀리"]

  Family --> Index["index 또는 *.md\n현재 뷰 / 색인 / 지도"]
  Family --> Records["items 또는 records\n개별 산출물 SSOT"]
  Family --> Template["_template.md\n생성 규격"]
  Family --> Views["views\n파생 정렬"]
  Family --> Ops["operations/*.md\n운영 규칙"]

  Index --> Rule["본문 복제 금지"]
  Records --> Rule
  Template --> Rule
  Views --> Rule
  Ops --> Rule

  Rule --> Durable["지속 가능한 문서 구조"]
```

## 12. 완성도와 회고 게이트

```mermaid
flowchart TB
  WorkDone["작업 종료 후보"]

  WorkDone --> External["외부 관점 완료\n사용자 요청 충족"]
  WorkDone --> Internal["내부 관점 완료\n원칙 / 검증 / 구조 충족"]
  WorkDone --> Retrospective["회고 완료\n무엇이 잘 작동했는가\n무엇을 고칠 것인가"]

  External --> CompletionDecision["완료 판단"]
  Internal --> CompletionDecision
  Retrospective --> CompletionDecision

  CompletionDecision -->|모두 충족| Promote["공식 승격"]
  CompletionDecision -->|하나라도 부족| Return["Current로 반환\n재작업 또는 보류"]

  Promote --> Official["Official\n공식 산출물"]
  Return --> Current["Current\n작업 중 산출물"]
```

## 13. 호스트와 플랫폼 독립성

```mermaid
flowchart TB
  StagePlugin["Stage Plugin"]

  StagePlugin --> PortableCore["호스트 공통 코어"]
  StagePlugin --> HostAdapters["호스트별 강제 어댑터"]
  StagePlugin --> Platforms["지원 플랫폼"]

  PortableCore --> CodexCore["Codex\n산출물 구조 / 스킬"]
  PortableCore --> ClaudeCore["Claude\n산출물 구조 / 스킬"]
  HostAdapters --> ClaudeHooks["Claude\nhooks/hooks.json 직접 등록"]
  HostAdapters --> CodexHooks["Codex\n같은 hooks/hooks.json 자동 발견\n+ TUI 1회 신뢰 승인"]

  Platforms --> Windows["Windows"]
  Platforms --> Linux["Linux"]
  Platforms --> MacOS["macOS"]

  PortableCore --> Markdown["Markdown 산출물"]
  PortableCore --> RelativePaths["상대 경로"]
  PortableCore --> PlainFiles["일반 파일 기반"]
  PortableCore --> NoShellAssumption["셸 의존 최소화"]
  PortableCore --> NoHostLockIn["호스트 전용 기능에 잠금 금지"]

  CodexCore --> SameStage["동일한 .stage 구조"]
  ClaudeCore --> SameStage
  ClaudeHooks --> EnforcedStage["행위 통제\n(deny / systemMessage / 컨텍스트 주입)"]
  CodexHooks --> EnforcedStage
  CodexHooks -.-> TrustCaveat["미신뢰 시 조용히 제외\n(exec 포함) — 설치 후 신뢰 필수"]
  Windows --> SameStage
  Linux --> SameStage
  MacOS --> SameStage

  SameStage --> DurableExecution["공통 산출물 하네스"]
  EnforcedStage --> DurableExecution
```

호스트 훅 계약(도구명 매핑 · 출력 규칙 · 신뢰 게이트)의 상세 정본은 `hooks/README.md` §Host contract.

## 14. 이식성 게이트

```mermaid
flowchart LR
  Change["Stage 변경 후보"]

  Change --> HostCheck["호스트 확인\nCodex와 Claude에서 의미가 유지되는가"]
  Change --> PlatformCheck["플랫폼 확인\nWindows / Linux / macOS에서 경로와 실행이 안전한가"]
  Change --> FormatCheck["형식 확인\nMarkdown과 일반 파일로 표현 가능한가"]
  Change --> DependencyCheck["의존성 확인\n특정 셸 / GUI / 로컬 도구에 잠기지 않는가"]

  HostCheck --> Decision["이식성 판단"]
  PlatformCheck --> Decision
  FormatCheck --> Decision
  DependencyCheck --> Decision

  Decision -->|통과| Accept["Stage 설계에 포함"]
  Decision -->|실패| Redesign["재설계 또는 호스트별 어댑터로 분리"]
```

## 15. 훅 실행 게이트

```mermaid
flowchart TB
  Event["호스트 이벤트"]

  Event --> SessionStart["SessionStart"]
  Event --> PreToolUse["PreToolUse"]
  Event --> PostToolUse["PostToolUse"]
  Event --> Stop["Stop"]

  SessionStart --> Inject["Stage 문맥 주입\nplanned / current / official\n완료 게이트"]

  PreToolUse --> DeleteGate["삭제 게이트\n.stage 전체 삭제 차단\n등재 파일 삭제도 쓰기와 동일 게이트"]
  PreToolUse --> RegistrationGate["등재 게이트\n거버넌스 대상 수정 전 작업 항목 필요\n광역 기본 — 거의 모든 파일"]
  PreToolUse --> GovernanceGate["거버넌스 게이트\nsettings.json 파손 시 fail-closed"]
  PreToolUse --> HierarchyGate["계층 게이트\n부모 부재 / 자기 참조 /\n닫힌 부모 아래 자식 차단"]
  PreToolUse --> PromotionGate["승격 게이트\n대역 외 승격 의도 + promotes 바인딩\nrename 예약 (1단계)"]
  PreToolUse --> CommitGate["커밋 게이트\nstaged / git add / commit -a 대상 연결"]
  PreToolUse --> PortabilityGate["이식성 게이트\nOS 전용 스크립트 차단"]
  PreToolUse --> QuestionReminder["질문 게이트\n질문 전 목적·원칙 상기\n질문당 1회 리마인드"]

  PostToolUse --> IntentComplete["승격 의도 완료 (2단계)\nrename 예약을 확정, 차단 없음"]

  Audit["Audit CLI\n템플릿 / enum / 색인 / archive / 계층 / 계보 /\n결정 원칙 인용 / 거버넌스 / 정본 중복 /\n소유 경계 / 라우팅 검사"]

  Stop --> Summary["세션 요약 기록\n.stage/.runtime/sessions/세션별.md"]

  Inject --> Execution["일관된 수행"]
  DeleteGate --> Execution
  RegistrationGate --> Execution
  GovernanceGate --> Execution
  HierarchyGate --> Execution
  PromotionGate --> Execution
  CommitGate --> Execution
  PortabilityGate --> Execution
  QuestionReminder --> Execution
  IntentComplete --> Execution
  Audit --> Execution
  Summary --> Execution
```
