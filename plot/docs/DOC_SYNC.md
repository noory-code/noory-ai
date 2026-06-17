# DOC_SYNC — 2026-06-16~17 마라톤 결정 → 문서 싱크 worklist

> **목적:** 2026-06-16~17 big-picture 마라톤(`D-2026-06-16-H~R`, `D-2026-06-17-A~L`)이
> Foundation·Actors·Services·Feature·Entities·선 룰을 **다시 정의**했다. 새 정의는
> DECISIONS.md + BIG_PICTURE_REVIEW.md §11 + FOUNDATION_CONCEPT.md 에 박혀 있으나,
> 나머지 문서는 옛 정의가 남아 안 맞는다. 이 파일은 그 싱크 작업의 SSOT(체크리스트).
>
> **출처:** 두 차례 자동 audit (문서 16 + 플랜 6 = 22개). 결과: **17/22 stale, ~116곳.**
> ✅ 깨끗(손 안 댐): CURSOR.md, 루트 CLAUDE.md, ACTORS_PLAN.md, SERVICES_PLAN.md, FEATURE_CANVAS_PLAN.md.
>
> **✅ 적용 완료 (2026-06-18)** — Tier ①②③ 전부 적용(배치 ~104 + 수동 ~22) + 최종 재검수 통과(CONCEPTS·IDENTITY·SPEC clean). 플로어 = **완화**(`D-2026-06-18-A`). **의도적 보류만 잔존:** ① CHAT_ARCH 스레드 keying(service vs feature) → AI 채팅 플레이북 논의(5.10)로 이월; ② ARCHITECTURE 잔여 = 현재-코드 서술(코드 rename은 구현 시, 전향 마커 달림); ③ NODE_DATA = 미착수 플랜(배너+park, 결정 2).
>
> **범례:** `[C]` contradiction(능동적 오류) · `[O]` outdated(개명/잔재) · `[M]` missing(신규 개념 누락).
> 체크 = 반영 완료.

## 16 델타 (새 정의 요약 — 상세는 DECISIONS)

1. identity = 일관 실행·표현 액션 룰(출력, AI 도출). description 제거. status/provenance inert. (D-16-N/O)
2. mission = 선언 1칸 + body. what_we_do/why/direction 합침. (D-16-J/K)
3. core_value = label + body. definition·do/dont 제거. (D-16-M/L)
4. 본질 = 3종 창발적 전체(별도 노드 없음). 앵커 = 이름만. Foundation 단일 캔버스. (D-16-Q/R)
5. 모든 노드 = 토론으로 생성(AI 제안→사람 확정). 빈 폼·silent 금지. (D-16-P)
6. 캔버스별 채팅 = 적극 코치(개념 정리 + 고차원 제안). (D-16-H)
7. actor = 관계적 역할(사람 아님). 계층 트리 + 상속. 선 2종(계층/관계). (D-17-A)
8. service 인스펙터 = 5칸 질문형(누가 참여/왜 필요/뭐가 좋아지나 + 코어밸류 refs + 아이덴티티 refs). 옛 칸(what/scope/trigger/how/outcome/do/dont/target_side/body) 삭제. (D-17-B)
9. Services 오버뷰 = category/service/**feature**. service=인스펙터(드릴X), feature=드릴 타깃. (D-17-D)
10. 서비스→서비스 1급 엣지 없음. PRODUCT_SPEC §7 "유저저니 선" 폐기. (D-17-C)
11. feature 캔버스(옛 Service-Detail) = 행동 플로우차트. kind = step/decision/edge/note/rule/actor_ref. mission_ref/value_ref/identity_ref/metric/content/group 폐기. (D-17-G/H)
12. note = 신규 kind, 엣지 없음, 캔버스 전역 맥락 + AI 프레이밍 주입. (D-17-F)
13. rule = per-feature 운영 제약. policy ≠ identity. (D-17-E)
14. Entities = 신규 프로젝트 캔버스 + entity kind. AI 유지, 개념 맵(ERD 아님). dedup/역참조/채팅중제안/가벼운 인스펙터. (D-17-I/K)
15. "모든 선 사용자가 그림" 전역 룰 삭제. 선은 정의로 governed. AI 그리기 OK. 캔버스별 user-draw-only는 자체 선택. (D-17-J)
16. AI 채팅 컨텍스트 = 활성캔버스+선택+상위캔버스요약+엔티티레지스트리+온디맨드. CAG-first(seam 뒤). (D-17-L)

---

## 결정 (worklist 적용 규칙)

- **결정 1 — 하드 플로어 (✅ RESOLVED = 완화, `D-2026-06-18-A`):** `actor ≥2` 하드검증 폐기(operator/user 계층에서 자연 도출), `서비스 actor_ref ≥1` 유지("≥2 with operator" 문구 제거). 사용자 승인 2026-06-18. **CONCEPTS #13/#14, IDENTITY #9** 는 Tier ① 배치 끝난 뒤 이 결정대로 직접 편집.
- **결정 2 — NODE_DATA_AND_ARTIFACTS_PLAN:** 마라톤 전 플랜, 미착수 작업. **권장 = superseded 배너 + 보류(나중 재계획).** (assistant 권장, 사용자 확인 전제.)
- **결정 3 — 출하기록:** ROADMAP v0.10/v0.11 등 "이미 나간 기록"은 덮어쓰지 말고 **"superseded by D-…" 주석**. (기본값.)

---

## Tier ① — 개념 정본 (먼저)

> ✅ **DONE (2026-06-18)** — 배치 57곳 + 수동 12곳(CONCEPTS: 플로어·actor master 필드·is_root·sub-actor 잔재 / IDENTITY: 플로어·철학 섹션 재구성 / SPEC: self-loop 유저저니·read-only problem-first). 플로어 = **완화**(`D-2026-06-18-A`). DOMAIN·PRODUCT_SPEC 검수 통과. 최종 전체 재검수는 Tier ③ 후.

### CONCEPTS.md (19) — 가장 큼
- [ ] [C] mission 필드(what_we_do/why/direction) → 선언 1칸+body (D-16-J/K)
- [ ] [C] core_value 필드(definition/do/dont) → label+body (D-16-M/L)
- [ ] [C] identity 필드(description/do/dont) → label+액션룰 리스트 (D-16-N/O)
- [ ] [C] Canvases 표 → 오버뷰 category/service/feature; detail=feature 캔버스(step/decision/edge/note/rule/actor_ref); +Entities/entity (D-17-D/H/I)
- [ ] [C] Service typed fields(9칸) → 5칸 질문형 (D-17-B)
- [ ] [C] target_side 삭제 (D-17-B)
- [ ] [C] Services 드릴 모델(modal, category→service leaves) → category→service→feature, feature 드릴 (D-17-D)
- [ ] [C] rule(policy/permissions/actor_permissions) → per-feature 운영 제약, policy≠identity (D-17-E)
- [ ] [C] content/metric/group → feature 캔버스에서 폐기 (D-17-H)
- [ ] [C] mission_ref/value_ref/identity_ref(detail) → 폐기; value/identity=인스펙터 칩; actor_ref 유지 (D-17-B/H)
- [ ] [C] Symbol 섹션(5 candidate/4 alias/sub-actor) → 갱신; sub-actor 제거(계층) (D-17-A/B/H)
- [ ] [C] actor = class of people → 관계적 역할 + 계층 + 선 2종 (D-17-A)
- [ ] [O] **actor ≥2 baseline → 결정 1 대기**
- [ ] [O] **service ≥2 actor_ref(운영자 포함) → 결정 1 대기** (이미 ≥1, D-05-28-K)
- [ ] [C] decision 분기 "user-drawn edges" → 캔버스별 선택, 선은 정의 governed (D-17-J)
- [ ] [C] reference kinds intro / design principle 5 → refs 갱신 (D-17-B/H)
- [ ] [M] Foundation essence/anchor → 본질=창발 전체, 앵커=이름만 (D-16-Q/R)
- [ ] [M] feature/note/entity kind + build-through-discussion + active coach 추가 (D-16-H/P, D-17-D/F/I)
- [ ] [C] Design principle "AI-first do/dont" → build-through-discussion + 컨텍스트 봉투 (D-16-M/P, D-17-L)

### SPEC.md (13)
- [ ] [C] core_value definition+body → label+body (D-16-M)
- [ ] [C] identity description+body+status/provenance → label+액션룰; status inert (D-16-N/O)
- [ ] [O] anchor-radial "all edges user-drawn" → Foundation 자체 선택 (D-17-J)
- [ ] [C] Actors §Edges "all edges user-drawn" → per-canvas 선택 (D-17-J)
- [ ] [C] ServiceDetail §Edges "all edges user-drawn" → 정의-governed 참조 (D-17-J + 개명)
- [ ] [C] Service `problem` 인스펙터(target_side/what/value_created/outcome) → 5칸 (D-17-B)
- [ ] [O] typed-text 예시(mission.what_we_do, service.scope) → 현 필드명 (D-16-J, D-17-B)
- [ ] [C] Service "one purpose/modal header" 드릴 → feature 드릴; feature 캔버스 (D-17-D/G)
- [ ] [C] ServiceDetail 스텐실(metric/group/mission_ref/value_ref) → 폐기 (D-17-H)
- [ ] [M] rule/content "add or retire" 열린Q → rule=per-feature, note=신규, content 폐기 (D-17-E/F/H)
- [ ] [M] scope note "Services/Service-Detail implementation-defined" → 오버뷰+feature캔버스+Entities 핀 (D-17-B..K)
- [ ] [M] Entities 캔버스 없음 → §Entities 추가 (D-17-I/K)
- [ ] [O] decision "never auto-emit/user draws" → D-17-J 로 완화

### DOMAIN.md (7)
- [ ] [C] EssencePlanning target_side + actor edge → target_side 제거; 새 service 모델; actor 선 2종 (D-17-B/A)
- [ ] [C] EssenceExecution Service-Detail metric/content → feature 캔버스; metric/content 폐기 (D-17-G/H/D)
- [ ] [O] ubiquitous lang Canvas row(4 canvas) → feature+Entities; 이름 정합 (D-17-G/I)
- [ ] [C] Drill row "drill service→service-detail" → service=인스펙터, feature 드릴 (D-17-D)
- [ ] [M] kind inventory → feature/note/entity 추가 (D-17-D/F/I)
- [ ] [O] EssenceDiscovery typed-text 폼 → 축소 필드, active coach, 토론 생성 (D-16-J..O/H/P)
- [ ] [C] EssenceRetention foundation refs → core_value/identity 칩; *_ref 폐기 (D-17-B/H)

### PRODUCT_SPEC.md (11)
- [ ] [C] §7 "Service-to-service edges = User journey" → **삭제** (D-17-C)
- [ ] [O] §5 cycles 예시(service→service) → 일반 노드 예시 (D-17-C)
- [ ] [M] §8 "Three canvases" → Entities + Feature 캔버스 추가; 전체 계층 (D-17-D/I)
- [ ] [C] §8 identity = tone&manner → 일관 실행·표현 액션룰, 출력 (D-16-N/O)
- [ ] [C] §8 Service row(유저저니 선/modal/starts empty) → 저니 삭제; feature 드릴; 5칸 인스펙터 (D-17-B/C/D/G)
- [ ] [C] §8 Actor row "stakeholder map, pain points" → 관계적 역할, 선 2종 (D-17-A)
- [ ] [O] §9 Service-Detail interview → feature 캔버스; refs 폐기 (D-17-G/H)
- [ ] [O] §13 Mermaid Service-Detail → feature 캔버스 (D-17-G)
- [ ] [O] §4 Mermaid "Service-Detail visualisation" → feature 캔버스 (D-17-G)
- [ ] [M] §7 symbol kinds → feature(+entity) 추가; core_value/identity refs=인스펙터 (D-17-D/B)
- [ ] [O] §8 single-foundation 근거 → 본질=창발 전체, audience 아님 (D-16-Q/R)

### IDENTITY.md (10)
- [ ] [C] "sub-service" 계층 → category→service→feature (D-17-D)
- [ ] [C] Two Modes "Service Detail" 캔버스 → feature 캔버스 + Entities (D-17-E..I)
- [ ] [O] Mode 2 "sub-services" → features (D-17-D)
- [ ] [C] "Do/Don't pairs" → core_value/service 에서 제거 (D-16-M, D-17-B)
- [ ] [O] "top-level service must anchor to identity or value" → 5칸 인스펙터 refs (D-17-B)
- [ ] [C] Actor = class of people → 관계적 역할 (D-17-A)
- [ ] [M] "Class not individual" → 역할(사람 아님) + 계층 + 선 2종 (D-17-A)
- [ ] [M] Service = playground → 5칸 인스펙터 + feature 드릴 정합 (D-17-B/D)
- [ ] [O] **Service min baseline → 결정 1 대기** (필드(1) actor refs)
- [ ] [M] feature/Entities/note/rule/edges-by-definition 누락 (D-17-E/F/I/J)

---

## Tier ② — 상위 서술

> ✅ **DONE (2026-06-18)** — 배치 18곳 + 수동 5곳(PHILOSOPHY: P3 rename·Service Blueprint·Iteration Log 주석 / ARCHITECTURE: 전향 마커 / CHAT_ARCH: 스레드 keying ⚠). VISION·FOUNDATION_CONCEPT 검수 통과. **CHAT_ARCH 스레드 keying(service vs feature) = AI 채팅 논의로 이월**(D-17-D 드릴만 재배선, 스코프키 미핀). ARCHITECTURE 잔여 = 현재-코드 서술이라 유지(전향 마커만).

### VISION.md (4)
- [ ] [O] 3-phase Discovery "interviews → typed-text MD templates" → active coach 토론 생성 (D-16-P/H)
- [ ] [O] 3-phase Execution "Service-Detail" 경로 → category→service→feature→feature 캔버스 (D-17-D/E..H)
- [ ] [O] closing note "Service-Detail → Foundation" 드릴백 → feature 캔버스 (D-17-G)
- [ ] [O] reversibility 예시 "Service-Detail → Foundation" → feature 캔버스 (D-17-G)

### PHILOSOPHY.md (5)
- [ ] [C] P7 two-plane(한 2D 공간) → 별도 캔버스들 (D-16-R, D-17-C/9)
- [ ] [C] P6 "every arrow carries value" → 관계 엣지만; 계층 엣지는 무가치 (D-17-A)
- [ ] [C] v0.2 표 P7 "two bands" → 다중 캔버스 (D-16-R)
- [ ] [O] v0.2 표 P8 "3 node kinds" → 갱신된 kind 셋 (D-17-D/I)
- [ ] [C] v0.2 표 P3 "actor inputs/outputs" → identity-only, per-service=actor_ref (D-17-A)

### CHAT_ARCH.md (3)
- [ ] [O] ask item2 "per service-detail canvas" → per-feature detail 캔버스 (D-17-D)
- [ ] [O] Layer 3 표 "Service-Detail" row → "Feature(feature detail)" 개명 (D-17-G)
- [ ] [O] Layer 3 표 Actors/Services row → 오버뷰 feature 드릴 층 주석(낮음) (D-17-D)

### ARCHITECTURE.md (2)
- [ ] [C] "auto-edges=0" regression test → Foundation-local, 전역 법 아님 (D-17-J)
- [ ] [M] "16th kind / 15-kind" 틀 → feature/note/entity 대기 + group 폐기 명시 (D-17-D/F/H/I)

### FOUNDATION_CONCEPT.md (4)
- [ ] [C] 서비스 적용(mission_ref/value_ref/identity_ref + injection 엣지) → 인스펙터 칩, injection 엣지 없음 (D-17-B/H)
- [ ] [O] "(서비스디테일 rule kind = per-service)" → feature 캔버스 rule = per-feature (D-17-E/G)
- [ ] [C] identity node-format "열린 결정(①body②facet③catch-all)" → 닫힘: label+액션룰 (D-16-O)
- [ ] [M] 액터 구조 → 역할/계층/선 2종 한 줄 추가 (D-17-A)

---

## Tier ③ — 정리 (ROADMAP / glossary / CLAUDE / 플랜)

> ✅ **DONE (2026-06-18)** — 배치 43곳 + 수동 4곳(ROADMAP(plot) 5-canvas, CLAUDE 16th-kind, NODE_DATA 마커×2). ROADMAP(root)·glossary·FOUNDATION_PLAN·**ENTITIES_PLAN(B2~B5 unblock)** 검수 통과. NODE_DATA = 배너+park(결정 2, 미착수 플랜). **의도적 보류:** ARCHITECTURE 잔여=현재-코드 서술(코드 rename은 구현 시), CHAT_ARCH 스레드 keying=AI 채팅 논의 이월.

### noory-ai/plot/docs/ROADMAP.md (15)
- [ ] [O] B) work-item "15-kind invariant" → 팔레트 이미 확장(feature/note/entity) (D-17-D/F/I)
- [ ] [O] B) origin metadata service_id → feature_id (D-17-D)
- [ ] [M] B) MVP schema "draft" → build-through-discussion 정합 (D-16-P)
- [ ] [M] D) context_envelope(node_id)/N-hop → D-17-L 봉투 + 엔티티 레지스트리
- [ ] [O] D) Phase3 judge "identity tone" → 액션룰 준수, mission 근거 (D-16-N/O/K)
- [ ] [C] v0.10 Step1 mission what_we_do/why/direction → 선언+body (superseded 주석, 결정 3) (D-16-J/K)
- [ ] [C] v0.10 Step2 core_value definition / identity description / do·dont → 새 모델 (주석) (D-16-M/N/O/L)
- [ ] [C] v0.10 Step3 ref kinds on services/service_detail → 인스펙터 칩 + 폐기 (주석) (D-17-B/H)
- [ ] [C] v0.10 Step4 service what/scope/trigger/how/outcome/do/dont + sub-service → 5칸 + feature (주석) (D-17-B/D)
- [ ] [C] v0.10 Step5 metric → feature 캔버스에서 폐기 (주석) (D-17-H)
- [ ] [C] v0.10 Step6 rule policy/content → per-feature rule; content 폐기 (주석) (D-17-E/H)
- [ ] [C] v0.11 Phase A actor "class of people, motivation/pain, ≥2" → 관계적 역할 + 계층 + 선 2종 (주석) (D-17-A)
- [ ] [M] header SSOT 목록 → BIG_PICTURE_REVIEW + D-16/17 추가

### ROADMAP.md (루트) (4)
- [ ] [C] "Services 단일클릭=드릴" → service=인스펙터, feature 드릴 (D-17-D)
- [ ] [O] "ServiceDetail" 명칭 → Feature 캔버스 (D-17-G)
- [ ] [O] "15 kind / service.problem" → 팔레트 확장 + "왜 필요한가?" 필드 (D-17-B/D/F/I)
- [ ] [M] Entities 캔버스/entity kind 추가 (D-17-I)

### I18N_KO_GLOSSARY.md (4)
- [ ] [C] "User journey/유저저니" 용어 → 폐기 (D-17-C)
- [ ] [O] identity "description" 힌트 정정로그 → 필드 제거됨 주석 (D-16-O)
- [ ] [O] 측면→속성 로그 → identity 이제 액션룰 주석 (D-16-N/O)
- [ ] [M] feature/entity/note 한글 표준어 추가 (D-17-D/F/I)

### noory-ai/plot/CLAUDE.md (3)
- [ ] [C] 통신규칙3 "what_we_do" 예시 → 현 필드 (D-16-J)
- [ ] [C] 운영규칙7 "every line ... explicit consent" → 좁힘(AI Entities + AI 엣지) (D-17-J/I)
- [ ] [O] Gate 2 "×15" 카운트 → registry SSOT 가리킴 (D-17-D/F/I)

### FOUNDATION_PLAN.md (1)
- [ ] [O] T3 스코프 노트 "service.problem / 17 kinds" → 새 표현 (D-17-A/B)

### ENTITIES_PLAN.md (6) — B2~B5 가 D-17-K로 이미 해결됨, unblock
- [ ] [C] §B2 "Open/No answer pinned" → 해결: 강한 의미 dedup, 플레이북 책무 (D-17-K)
- [ ] [C] §B3 "Open/Not pinned" → 해결: 역참조 derived, read-only (D-17-K)
- [ ] [C] §B4 "Open ... unspecified" → 해결: 채팅중 제안→확정, auto-scan 아님 (D-17-K)
- [ ] [C] §B5 "Open/Not pinned" → 해결: 이름+무엇담나+어디쓰이나+거친관계 (D-17-K)
- [ ] [C] §C step6 inspector "Blocked-on-open" → unblock (D-17-K)
- [ ] [C] §C step8 "Blocked ... B2" → 해결 (D-17-K)

### NODE_DATA_AND_ARTIFACTS_PLAN.md (7) — 결정 2 (권장: 배너+보류)
- [ ] 전체 "마라톤 전 플랜, 전제 superseded" 배너 (D-16-H..R, D-17-A..L)
- [ ] [C] §3 Q1/§4 "body everywhere SSOT" → per-kind 필드 모델로 재스코프
- [ ] [O] §1.1 현 필드 리스트 → superseded 주석
- [ ] [O] §3 Q3/Phase B "15 kinds 템플릿" → 팔레트 재계산
- [ ] [C] §5 Phase A "service-detail (16)" → feature 캔버스, inventory 재계산
- [ ] [C] §3.1 metric 기반 산출물 → metric 폐기, 산출 소스 재도출
- [ ] [C] §3.1 foundation refs/injection 체현 → 인스펙터 칩에서 읽기
