# 작업 아카이브

이 문서는 더 이상 현재 작업 흐름에 속하지 않는 작업 레코드의 인덱스를 소유한다.

작업 레코드 본문은 `items/`에 있다. 아카이브된 회고는 `retrospectives/`에 있다. 이 문서는 링크와 최소한의 식별 정보만 관리한다. 아카이브된 모든 항목은 여기에 행을 가진다. `Final status`는 항목의 `archived` 상태가 덮어쓴 최종 상태(`completed` 또는 `rejected`)를 기록한다.

| 작업 | Final status | 항목 | 제목 |
|---|---|---|---|
| W-00000001 | completed | [items/W-00000001.md](items/W-00000001/_story.md) | Repo-wide documentation cleanup |
| W-00000002 | completed | [items/W-00000002.md](items/W-00000002/_story.md) | Add venue field for dual-agent work routing |
| W-00000003 | completed | [items/W-00000003.md](items/W-00000003/_story.md) | Untrack .stage/.runtime/ from git |
| W-00000004 | completed | [items/W-00000004.md](items/W-00000004/_story.md) | Add complete Claude Code and Codex plugin support |
| W-00000005 | completed | [items/W-00000005.md](items/W-00000005/_story.md) | Archive completed work items W-00000001..W-00000004 |
| W-00000006 | completed | [items/W-00000006.md](items/W-00000006/_story.md) | Stage lifecycle skills, one-gate archive fix, and false-learning correction |
| W-00000007 | completed | [items/W-00000007.md](items/W-00000007/_story.md) | Stage skill system — co-locate single-owner scripts, sharpen triggers; audit-enforcement deferred |
| W-00000008 | completed | [items/W-00000008.md](items/W-00000008/_story.md) | Stage execution scripts (register/close) + PreToolUse enum-validity gate |
| W-00000010 | completed | [items/W-00000010.md](items/W-00000010/_story.md) | Configurable per-stage, per-strength review in settings.json |
| W-00000011 | completed | [items/W-00000011.md](items/W-00000011/_story.md) | Optional, field-driven review requirement on work items |
| W-00000009 | completed | [items/W-00000009.md](items/W-00000009/_story.md) | Make Plainly configuration project-owned under .plainly |
| W-00000012 | completed | [items/W-00000012.md](items/W-00000012/_story.md) | Separate Stage core operations from project policy |
| W-00000013 | completed | [items/W-00000013.md](items/W-00000013/_story.md) | Generate Stage documents in the user's language |
| W-00000014 | completed | [items/W-00000014.md](items/W-00000014/_story.md) | Make AI roles drive Stage work routing and handoffs |
| W-00000015 | completed | [items/W-00000015.md](items/W-00000015/_story.md) | Complete the role-routing contract left unfinished by B-00000001..3 |
| W-00000017 | completed | [items/W-00000017.md](items/W-00000016/W-00000017/_story.md) | Implement the unified work-card lifecycle (kanban moves, B family retires) |
| W-00000016 | completed | [items/W-00000016.md](items/W-00000016/_epic.md) | Design the unified work-card lifecycle (backlog cards are W items) |
| W-00000018 | completed | [items/W-00000018.md](items/W-00000018/_story.md) | Schema v4 official-zone design freeze |
| W-00000019 | completed | [items/W-00000019.md](items/W-00000019/_story.md) | Schema v4 topology registry (C2) |
| W-00000020 | completed | [items/W-00000020.md](items/W-00000020/_story.md) | Cross-venue delegation and review contract |
| W-00000021 | completed | [items/W-00000021.md](items/W-00000021/_story.md) | archive_work.py review-row removal misses hand-written rows |
| W-00000022 | completed | [items/W-00000022.md](items/W-00000022/_story.md) | close_work.py replaces the item's Verification section |
| W-00000023 | completed | [items/W-00000023.md](items/W-00000023/_story.md) | archive_work.py silently overwrites an existing archive retrospective on id collision |
| W-00000024 | completed | [items/W-00000024.md](items/W-00000024/_story.md) | No guard against duplicate retrospective ids across present and archive |
| W-00000025 | completed | [items/W-00000025.md](items/W-00000025/_story.md) | Close/archive ordering guard: refuse closure with uncommitted scope changes |
| W-00000027 | completed | [items/W-00000027.md](items/W-00000027/_story.md) | register_work --backlog appends index rows outside the table |
| W-00000028 | completed | [items/W-00000028.md](items/W-00000028/_story.md) | Commit gate misparses quoted arguments in git commit commands |
| W-00000029 | completed | [items/W-00000029.md](items/W-00000029/_story.md) | v4 migration delivered as a user-facing skill; no version strands a v3 user |
| W-00000030 | completed | [items/W-00000030.md](items/W-00000030/_story.md) | v4 template tree and Theme/Milestone templates (C3) |
| W-00000031 | completed | [items/W-00000031.md](items/W-00000031/_story.md) | 이 저장소에서 Stage 플러그인 로컬 비활성화 (C4 게이트 수술 안전망) |
| W-00000032 | completed | [items/W-00000032.md](items/W-00000032/_story.md) | C4a: schema_version dispatch — consumers registry-driven on v4, v3 unchanged |
| W-00000033 | completed | [items/W-00000033.md](items/W-00000033/_story.md) | C4b: legacy-root denial gate + lifecycle views (v4-only) |
| W-00000034 | completed | [items/W-00000034.md](items/W-00000034/_story.md) | C5: lifecycle CLIs v4-aware + stage-work milestone question |
| W-00000035 | completed | [items/W-00000035.md](items/W-00000035/_story.md) | C6a: stage-roadmap skill + decision chains + roadmap audits + session table |
| W-00000036 | completed | [items/W-00000036.md](items/W-00000036/_story.md) | C6b: milestone closure snapshot + revalidation + re-attribution gate |
| W-00000037 | completed | [items/W-00000037.md](items/W-00000037/_story.md) | C7: v3->v4 migration command + stage-migrate skill + v4 activation |
| W-00000038 | completed | [items/W-00000038.md](items/W-00000038/_story.md) | C8: exhaustive migration + v4 QA (adversarial fixtures) |
| W-00000039 | completed | [items/W-00000039.md](items/W-00000039/_story.md) | C9: rewrite concept-layer docs to v4 vocabulary |
| W-00000040 | completed | [items/W-00000040.md](items/W-00000040/_story.md) | Enum gate honors planned-card status enum |
| W-00000041 | completed | [items/W-00000041.md](items/W-00000041/_story.md) | Plainly 전달 원칙 강화 — baseline 합성·정직성·온보딩 인터뷰 |
| W-00000043 | completed | [items/W-00000043.md](items/W-00000042/W-00000043/_story.md) | acceptance 필드 — 기계 판정 종료 스키마 |
| W-00000044 | completed | [items/W-00000044.md](items/W-00000042/W-00000044/_story.md) | 독립 판정 필수화 — review 훅을 자율 항목 종료 게이트로 |
| W-00000045 | completed | [items/W-00000045.md](items/W-00000042/W-00000045/_story.md) | 집계 롤업 — parent 자식 전부 terminal 시 부모 양의 전진 |
| W-00000046 | completed | [items/W-00000046.md](items/W-00000042/W-00000046/_story.md) | 에스컬레이션·폭주 상한 — blocked 전환 + 시도/무진전/전역 상한 |
| W-00000047 | completed | [items/W-00000047.md](items/W-00000042/W-00000047/_story.md) | 드라이버 컴포넌트 — 선택→실행→검증→전진 루프 (게이트 밖) |
| W-00000042 | completed | [items/W-00000042.md](items/W-00000042/_epic.md) | 자율 실행 드라이버 — 계약 설계 |
| W-00000048 | completed | [items/W-00000048.md](items/W-00000048/_story.md) | unattended 드라이버 루프 — 서브트리 자율 완주 |
| W-00000049 | completed | [items/W-00000049.md](items/W-00000049/_story.md) | unattended 드라이버 — Codex 리뷰 지적 수정 (W-48 후속) |
| W-00000050 | completed | [items/W-00000050.md](items/W-00000050/_story.md) | Plainly 주입 문구에 언어 자연스러움 공통 규칙 추가 |
| W-00000051 | completed | [items/W-00000051.md](items/W-00000051/_story.md) | Stage 초기화가 .gitignore에 .stage/.runtime/ 등록 |
| W-00000052 | completed | [items/W-00000052.md](items/W-00000052/_story.md) | CLAUDE.md 언어 규칙에 .stage/ 예외 명시 |
| W-00000053 | completed | [items/W-00000053.md](items/W-00000053/_story.md) | .stage/ 안내 문서를 한국어로 전환 |
| W-00000054 | completed | [items/W-00000054.md](items/W-00000054/_story.md) | 승격 게이트가 셸로 실행한 스크립트의 official 쓰기를 막지 못함 |
| W-00000055 | completed | [items/W-00000055.md](items/W-00000055/_story.md) | Stage 검증 템플릿의 v3 잔재 경로 수정 |
| W-00000056 | completed | [items/W-00000056.md](items/W-00000056/_story.md) | 마이그레이션의 안내 산문 갱신 방식 결정 (Q-00000001) |
| W-00000058 | completed | [items/W-00000058.md](items/W-00000058/_story.md) | 안내 문서 갱신의 소유 경계 확정 |
| W-00000057 | completed | [items/W-00000057.md](items/W-00000057/_story.md) | 낡은 안내 문서 검사 + 갱신 명령 (DE-00000028, DE-00000029) |
| W-00000059 | completed | [items/W-00000059.md](items/W-00000059/_story.md) | 플레인리 스타일에 한국어 문장 규칙 추가 |
| W-00000060 | completed | [items/W-00000060.md](items/W-00000060/_story.md) | 플레인리가 주입하는 언어 규칙을 판정 가능하게 고침 |
| W-00000061 | completed | [items/W-00000061.md](items/W-00000061/_story.md) | 결정이 언제 공식이 되는지 정한다 |
| W-00000062 | completed | [items/W-00000062.md](items/W-00000062/_story.md) | 은퇴한 bug 종류의 검증 기준 한 줄 추가 |
| W-00000063 | completed | [items/W-00000063.md](items/W-00000063/_story.md) | 위임 실행 루프를 문서로 못 박는다 |
| W-00000064 | completed | [items/W-00000064.md](items/W-00000064/_story.md) | 보관할 때 그 작업의 남은 예약을 치운다 |
| W-00000065 | completed | [items/W-00000065.md](items/W-00000065/_story.md) | 훅이 무엇까지 막고 무엇은 못 막는지 밝힌다 |
| W-00000066 | completed | [items/W-00000066.md](items/W-00000066/_story.md) | P-00000001에 오늘 재발 증거와 더 나은 완화책을 붙인다 |
| W-00000067 | completed | [items/W-00000067.md](items/W-00000067/_story.md) | 설정 파일을 읽는 자리를 하나로 모은다 |
| W-00000026 | completed | [items/W-00000026.md](items/W-00000026/_story.md) | 설정 파일에 주석을 달 수 있게 한다 |
| W-00000068 | completed | [items/W-00000068.md](items/W-00000068/_story.md) | 버전을 올린 뒤 위임하면 막히는 것을 문서에 적는다 |
| W-00000071 | completed | [items/W-00000071.md](items/W-00000069/W-00000071/_story.md) | 드라이버가 실행자에게 대상 작업 항목을 전달한다 |
| W-00000072 | completed | [items/W-00000072.md](items/W-00000072/_story.md) | 실행자 환경 변수 — Windows 예시와 무인 모드 테스트 |
| W-00000070 | completed | [items/W-00000070.md](items/W-00000069/W-00000070/_story.md) | stage-drive 스킬 — 드라이버 진입점 |
| W-00000069 | completed | [items/W-00000069.md](items/W-00000069/_epic.md) | 드라이버를 이 저장소에서 처음으로 실제 실행한다 |
| W-00000074 | completed | [items/W-00000074.md](items/W-00000074/_story.md) | 스킬이 자기 플러그인의 스크립트를 가리키는 방법 |
| W-00000073 | completed | [items/W-00000073.md](items/W-00000076/W-00000073/_story.md) | 감독 모드 리뷰어가 실행자의 새 파일을 보지 못한다 |
| W-00000075 | completed | [items/W-00000075.md](items/W-00000076/W-00000075/_story.md) | 무인 모드가 기록 커밋 실패를 삼키고 부모 감사를 건너뛴다 |
| W-00000076 | completed | [items/W-00000076.md](items/W-00000076/_epic.md) | 무인 모드를 실전에 걸 수 있게 남은 결함을 닫는다 |
| W-00000080 | completed | [items/W-00000080.md](items/W-00000080/_story.md) | 글쓰기 규칙에 한국어가 동사로 푼다는 사실을 넣는다 |
| W-00000077 | completed | [items/W-00000077.md](items/W-00000079/W-00000077/_story.md) | 색인 스냅숏 주변의 남은 실패 처리 셋 |
| W-00000078 | completed | [items/W-00000078.md](items/W-00000079/W-00000078/_story.md) | 닫기 기록이 판정 근거와 검증 개수를 잃는다 |
| W-00000079 | completed | [items/W-00000079.md](items/W-00000079/_epic.md) | 드라이버와 닫기 도구의 실패 처리·기록을 마무리한다 |
| W-00000084 | completed | [items/W-00000084.md](items/W-00000084/_story.md) | 리뷰 지적을 받을지 말지 정하는 자리를 만든다 |
| W-00000081 | completed | [items/W-00000081.md](items/W-00000081/_story.md) | 드라이버가 도는 중에 사람이 커밋하면 그 커밋이 되돌아간다 |
| W-00000083 | completed | [items/W-00000083.md](items/W-00000083/_story.md) | 실행하는 쪽이 일을 못 했는데 성공으로 끝난다 |
| W-00000085 | completed | [items/W-00000085.md](items/W-00000085/_story.md) | 리뷰어가 카드의 성공 기준에 대고 판정하게 한다 |
| W-00000086 | completed | [items/W-00000086.md](items/W-00000086/_story.md) | 리뷰 지적 처리 단계를 스킬 문서에 적는다 |
| W-00000082 | completed | [items/W-00000082.md](items/W-00000082/_story.md) | 드라이버가 카드 하나를 직접 받게 한다 |
| W-00000088 | completed | [items/W-00000088.md](items/W-00000088/_story.md) | 무인 모드에서 차단된 리뷰 판정 출력을 보존한다 |
| W-00000089 | completed | [items/W-00000089.md](items/W-00000089/_story.md) | 리뷰어가 리뷰를 못 했는데 통과로 끝난다 |
| W-00000087 | completed | [items/W-00000087.md](items/W-00000087/_story.md) | codex 리뷰 명령에도 기준 판정 계약을 넘긴다 |
| W-00000091 | completed | [items/W-00000091.md](items/W-00000091/_story.md) | close_work 가 돌리는 리뷰에도 카드 경로를 준다 |
| W-00000090 | completed | [items/W-00000090.md](items/W-00000090/_story.md) | 세션 안에서 돌린 드라이버가 세션 환경을 리뷰어에게 흘린다 |
| W-00000093 | completed | [items/W-00000093.md](items/W-00000093/_story.md) | Stage 0.44.0 — 오늘 아크를 릴리스로 묶는다 |
| W-00000096 | completed | [items/W-00000096.md](items/W-00000096/_story.md) | 작업 로그가 세 역할의 공용 기록이 된다 |
| W-00000097 | completed | [items/W-00000097.md](items/W-00000097/_story.md) | 로그에 남은 항목이 다음 바퀴의 입력이 된다 |
| W-00000094 | completed | [items/W-00000094.md](items/W-00000094/_story.md) | 드라이버 한 바퀴를 역할 계약으로 다시 세운다 |
| W-00000095 | completed | [items/W-00000095.md](items/W-00000095/_story.md) | 드라이버가 관찰한 파일 목록이 리뷰 입력이 된다 |
| W-00000098 | completed | [items/W-00000098.md](items/W-00000098/_story.md) | 결정 기록이 계약의 적용 자리를 세어 적게 한다 |
| W-00000099 | completed | [items/W-00000099.md](items/W-00000099/_story.md) | 값을 쓸 자리가 없으면 조용히 넘어가는 것을 막는다 |
| W-00000100 | completed | [items/W-00000100.md](items/W-00000100/_story.md) | 무인 모드가 실패했을 때 그 사실을 제대로 남긴다 |
| W-00000101 | completed | [items/W-00000101.md](items/W-00000101/_story.md) | 드라이버가 끝날 때 자기가 띄운 실행자를 거둔다 |
| W-00000102 | completed | [items/W-00000102.md](items/W-00000102/_story.md) | 드라이버 설명 문서를 계약 다섯 층에 맞춘다 |
| W-00000103 | completed | [items/W-00000103/_story.md](items/W-00000103/_story.md) | 일감 규모 계층을 결정으로 확정하고 실행 단위로 쪼갠다 |
| W-00000104 | completed | [items/W-00000104/_epic.md](items/W-00000104/_epic.md) | Stage 가 일감을 규모로 관리한다 — 에픽·스토리·액션 |
| W-00000112 | completed | [items/W-00000112/_story.md](items/W-00000112/_story.md) | 대기 결정 다섯 건을 official 로 승격하고 결정 인덱스 누락을 메꾼다 |
| W-00000113 | completed | [items/W-00000113/_story.md](items/W-00000113/_story.md) | 드라이버 한 바퀴 계약을 실제 운행에 맞춘다 — 결정 준비 (P-00000003) |
| W-00000114 | completed | [items/W-00000114/_story.md](items/W-00000114/_story.md) | 계층 게이트가 카드 아닌 표면을 카드로 오판하지 않는다 |
| W-00000122 | completed | [items/W-00000122/_story.md](items/W-00000122/_story.md) | 겹치지 않는 Stage 작업을 병렬로 돌릴 수 있게 한다 — 설계 |
| W-00000123 | completed | [items/W-00000123/_epic.md](items/W-00000123/_epic.md) | 겹치지 않는 Stage 작업이 동시에 돈다 |
| W-00000115 | completed | [items/W-00000115/_epic.md](items/W-00000115/_epic.md) | 드라이버가 실패 경로에서도 계약대로 움직인다 |
| W-00000111 | completed | [items/W-00000111/_story.md](items/W-00000111/_story.md) | 계층 보관의 인덱스 계약을 한쪽으로 정한다 |
| W-00000120 | completed | [items/W-00000120/_story.md](items/W-00000120/_story.md) | 깊이 1 예외에서 카드 이름 모양을 다시 뺀다 |
| W-00000135 | completed | [items/W-00000135/_story.md](items/W-00000135/_story.md) | 병렬 정리가 도는 역할을 짐작하지 않고 기록에서 읽는다 |
| W-00000136 | completed | [items/W-00000136/_story.md](items/W-00000136/_story.md) | 훅을 띄우는 테스트가 프로젝트 변수를 스스로 걷는다 |
| W-00000137 | completed | [items/W-00000137/_story.md](items/W-00000137/_story.md) | stage 0.55.0 을 낸다 |
| W-00000138 | completed | [items/W-00000138/_story.md](items/W-00000138/_story.md) | 정직성 규칙이 스타일 선택과 무관하게 살아남는다 |
| W-00000139 | completed | [items/W-00000139/_story.md](items/W-00000139/_story.md) | 사용자에게 하는 말이 스타일 선택과 무관하게 존댓말로 선다 |
| W-00000140 | completed | [items/W-00000140/_story.md](items/W-00000140/_story.md) | v4 프로젝트가 자기 기존 결함 때문에 v5 마이그레이션에 막히지 않는다 |
| W-00000141 | completed | [items/W-00000141/_story.md](items/W-00000141/_story.md) | 설명 문서 갱신이 프로젝트가 쌓은 내용을 무엇으로 알아보는가 |
| W-00000142 | completed | [items/W-00000142/_story.md](items/W-00000142/_story.md) | 갱신이 설명하지 못하는 줄을 지우지 않는다 |
| W-00000146 | completed | [items/W-00000146/_story.md](items/W-00000146/_story.md) | 두 번째 바퀴의 리뷰가 무엇을 다시 보는가 |
| W-00000147 | completed | [items/W-00000147/_story.md](items/W-00000147/_story.md) | 시도가 오를 때 누가 실행하고 판정하는가 |
| W-00000144 | completed | [items/W-00000144/_story.md](items/W-00000144/_story.md) | 보관된 v5 카드를 게이트가 다시 열 수 있다 |
| W-00000150 | completed | [items/W-00000150/_story.md](items/W-00000150/_story.md) | stage 0.55.1 릴리스 |
| W-00000145 | completed | [items/W-00000145/_story.md](items/W-00000145/_story.md) | 결정 하나를 카드 여럿이 참조할 수 있는가 |
| W-00000148 | completed | [items/W-00000148/_story.md](items/W-00000148/_story.md) | 두 번째 바퀴의 리뷰를 좁힌 범위로 돌린다 |
| W-00000152 | completed | [items/W-00000152/_story.md](items/W-00000152/_story.md) | 카드 제목을 할 일로 쓰게 규칙을 바꾼다 |
| W-00000149 | completed | [items/W-00000149/_story.md](items/W-00000149/_story.md) | 드라이버가 부르는 명령에 모델 이름을 적는다 |
| W-00000151 | completed | [items/W-00000151/_story.md](items/W-00000151/_story.md) | decision_refs 가 무엇을 담는지 문서에 적는다 |
| W-00000143 | completed | [items/W-00000143/_story.md](items/W-00000143/_story.md) | 쌓이는 자리가 자동 갱신을 되찾는 길을 정한다 |
| W-00000153 | completed | [items/W-00000153/_story.md](items/W-00000153/_story.md) | 빈 목록 그릇을 갱신과 감사가 알아보게 한다 |
| W-00000156 | completed | [items/W-00000156/_story.md](items/W-00000156/_story.md) | 문서 규칙에 독자와 수준을 적는다 |
| W-00000092 | rejected | [items/W-00000092/_story.md](items/W-00000092/_story.md) | 드라이버가 실행자의 건강을 확인한다 — 사전 점검과 생존 감시 |
| W-00000155 | completed | [items/W-00000155/_story.md](items/W-00000155/_story.md) | 반려한 계획 카드를 보관으로 빼는 길을 만든다 |
| W-00000158 | completed | [items/W-00000158/_story.md](items/W-00000158/_story.md) | 카드가 저장하는 검사 명령을 좁게 고르는 규칙을 적는다 |
| W-00000160 | completed | [items/W-00000160/_story.md](items/W-00000160/_story.md) | 다른 도구가 저장소에 깔아 둔 Copilot 지침을 지운다 |
| W-00000159 | completed | [items/W-00000159/_story.md](items/W-00000159/_story.md) | Stage 가 무엇을 위한 물건인지 자기 말로 적는다 |
| W-00000161 | completed | [items/W-00000161/_story.md](items/W-00000161/_story.md) | 쓰기 직전에 무엇을 위한 일인지 다시 띄운다 |
| W-00000157 | completed | [items/W-00000157/_story.md](items/W-00000157/_story.md) | 드라이버 시험이 물려받은 환경 변수에 흔들리지 않게 한다 |
| W-00000167 | completed | [items/W-00000167/_story.md](items/W-00000167/_story.md) | 문장 규칙이 한 곳에서 나오고 쓰는 글 전부에 걸리게 한다 |
| W-00000168 | completed | [items/W-00000168/_story.md](items/W-00000168/_story.md) | 실행하는 쪽이 무엇을 스스로 하고 무엇을 보고하는지 계약으로 세운다 |
| W-00000171 | completed | [items/W-00000171/_story.md](items/W-00000171/_story.md) | 목적이 매 도구 호출마다 눈앞에 있고, 파일 목록은 막는 대신 알린다 |
| W-00000174 | completed | [items/W-00000174/_story.md](items/W-00000174/_story.md) | 커밋하는 자리도 쓰는 자리와 같은 규칙을 따르게 한다 |
| W-00000164 | completed | [items/W-00000164/_story.md](items/W-00000164/_story.md) | 카드 그릇이 층마다 무엇을 물을지 계약으로 세운다 |
| W-00000175 | completed | [items/W-00000175/_story.md](items/W-00000175/_story.md) | 밀린 결정을 공식으로 내리고 다시 안 쌓이게 한다 |
| W-00000179 | completed | [items/W-00000179/_story.md](items/W-00000179/_story.md) | 대기 결정 목록이 서랍과 같은 말을 하게 한다 |
| W-00000180 | completed | [items/W-00000180/_story.md](items/W-00000180/_story.md) | 릴리스에 자기 종류를 주고 클로드로 보낸다 |
| W-00000182 | completed | [items/W-00000182/_story.md](items/W-00000182/_story.md) | 드라이버가 성패를 무엇으로 재는지 바로잡는다 |
| W-00000181 | completed | [items/W-00000181/_story.md](items/W-00000181/_story.md) | 오늘 실린 stage 변경을 릴리스한다 |
| W-00000186 | completed | [items/W-00000186/_story.md](items/W-00000186/_story.md) | 실행자마다 체크아웃을 따로 둘지 정한다 |
| W-00000187 | completed | [items/W-00000187/_story.md](items/W-00000187/_story.md) | 무인 실행을 자기 작업 디렉터리에서 돌린다 |
| W-00000189 | completed | [items/W-00000189/_story.md](items/W-00000189/_story.md) | 카드를 등록할 때 안 센 것을 장치가 잡게 한다 |
| W-00000188 | completed | [items/W-00000188/_story.md](items/W-00000188/_story.md) | 대체된 결정이 자기가 대체됐다고 말하게 한다 |
| W-00000154 | rejected | [items/W-00000154/_story.md](items/W-00000154/_story.md) | 빈 그릇을 위치 대신 무엇으로 찾을지 정한다 |
| W-00000195 | completed | [items/W-00000195/_story.md](items/W-00000195/_story.md) | 제안과 계획에 남은 것을 전부 처분한다 |
| W-00000196 | completed | [items/W-00000196/_story.md](items/W-00000196/_story.md) | 닫힌 상태 기록이 자기가 닫혔다고 말하게 한다 |
| W-00000198 | completed | [items/W-00000198/_epic.md](items/W-00000198/_epic.md) | 끝난 기록을 살아 있는 서랍에서 빼낸다 |
| W-00000204 | completed | [items/W-00000204/_story.md](items/W-00000204/_story.md) | stage 0.57.0 을 낸다 |
| W-00000206 | completed | [items/W-00000206/_epic.md](items/W-00000206/_epic.md) | 일을 시작하기 전에 목적부터 캐낸다 |
| W-00000210 | completed | [items/W-00000210/_story.md](items/W-00000210/_story.md) | stage 0.58.0 을 낸다 |
| W-00000214 | completed | [items/W-00000214/_story.md](items/W-00000214/_story.md) | 초기화 스킬의 손 작업 문장이 현재 세대 트리를 가리키게 한다 |
| W-00000211 | rejected | [items/W-00000211/_story.md](items/W-00000211/_story.md) | 설명 문서 갱신이 설명 못 하는 줄을 안 덮게 한다 |
| W-00000213 | rejected | [items/W-00000213/_story.md](items/W-00000213/_story.md) | 감사가 대기 서랍과 보관함의 같은 기록을 잡게 한다 |
| W-00000215 | rejected | [items/W-00000215/_story.md](items/W-00000215/_story.md) | 목적 표시가 빈 카드에서 한 번을 안 쓰게 한다 |
| W-00000212 | completed | [items/W-00000212/_story.md](items/W-00000212/_story.md) | 보관 명령이 계층을 만나도 끝까지 가게 한다 |
| W-00000216 | completed | [items/W-00000216/_story.md](items/W-00000216/_story.md) | 감사가 두-자리 허가증을 잡는 동작을 시험으로 못 박는다 |
| W-00000223 | completed | [items/W-00000223/_story.md](items/W-00000223/_story.md) | 훅 시험이 어느 셸에서 돌려도 같은 결과를 낸다 |
| W-00000220 | rejected | [items/W-00000220/_story.md](items/W-00000220/_story.md) | 워크트리 실행 환경을 본 체크아웃과 같게 준비한다 |
| W-00000224 | completed | [items/W-00000224/_story.md](items/W-00000224/_story.md) | 감독 모드의 claude venue 실행을 세션 팀원에게 맡기기로 정한다 |
| W-00000217 | completed | [items/W-00000217/_story.md](items/W-00000217/_story.md) | 드라이버가 잘리거나 죽어도 하니스 안에서 이어 간다 |
| W-00000225 | completed | [items/W-00000225/_story.md](items/W-00000225/_story.md) | stage 0.59.0 을 낸다 |
| W-00000226 | completed | [items/W-00000226/_story.md](items/W-00000226/_story.md) | 드라이버 스킬이 명령 시간 한도가 어디서 나오는지 적는다 |
| W-00000227 | completed | [items/W-00000227/_story.md](items/W-00000227/_story.md) | 팀원 워크트리 자리를 무시 목록에 넣는다 |
| W-00000229 | rejected | [items/W-00000229/_story.md](items/W-00000229/_story.md) | 목적이 빈 카드에서는 그 위의 목적이라도 보여 준다 |
| W-00000228 | completed | [items/W-00000228/_story.md](items/W-00000228/_story.md) | 병렬 명령이 무인 모드를 그대로 넘긴다 |
| W-00000230 | completed | [items/W-00000230/_story.md](items/W-00000230/_story.md) | 무인 실행 결과를 본 가지로 들인다 |
| W-00000231 | completed | [items/W-00000231/_story.md](items/W-00000231/_story.md) | stage 0.60.0 을 낸다 |
| W-00000232 | completed | [items/W-00000232/_story.md](items/W-00000232/_story.md) | 팀원 실행 절차가 실제로 되는 방법을 적게 한다 |
| W-00000233 | completed | [items/W-00000233/_story.md](items/W-00000233/_story.md) | 일의 종류에 맞는 모델을 고르는 기준을 절차가 갖게 한다 |
| W-00000235 | completed | [items/W-00000235/_story.md](items/W-00000235/_story.md) | 드라이버가 실행 결과를 잃거나 겹치게 만들지 않는다 |
| W-00000234 | completed | [items/W-00000234/_story.md](items/W-00000234/_story.md) | 실행 결과를 들이는 명령이 게이트를 어떻게 지나는지 정한다 |
| W-00000238 | rejected | [items/W-00000238/_story.md](items/W-00000238/_story.md) | 실행 결과를 들이는 명령을 만든다 |
| W-00000239 | completed | [items/W-00000239/_story.md](items/W-00000239/_story.md) | 들이는 커밋이 담을 것을 실측에 맞게 다시 정한다 |
| W-00000205 | completed | [items/W-00000205/_story.md](items/W-00000205/_story.md) | 로드맵 결정이 처음부터 제자리에 쓰이게 한다 |
| W-00000240 | completed | [items/W-00000240/_story.md](items/W-00000240/_story.md) | stage 0.61.0 을 배포한다 |
| W-00000245 | completed | [items/W-00000245/_story.md](items/W-00000245/_story.md) | 회고의 배움이 규칙이 되는 절차를 만든다 |
| W-00000242 | completed | [items/W-00000242/_story.md](items/W-00000242/_story.md) | 막는 자리 열넷을 세고 겹치는 것을 합친다 |
| W-00000241 | completed | [items/W-00000241/_story.md](items/W-00000241/_story.md) | 드라이버를 책임별로 나눈다 |
| W-00000244 | completed | [items/W-00000244/_story.md](items/W-00000244/_story.md) | 열린 관측을 읽는 쪽을 만든다 |
| W-00000248 | rejected | [items/W-00000248/_story.md](items/W-00000248/_story.md) | 들이는 명령이 인덱스를 고칠 수 있게 결정을 잇는다 |
| W-00000252 | completed | [items/W-00000252/_story.md](items/W-00000252/_story.md) | 실행 결과를 들이는 명령을 만든다 |
| W-00000250 | completed | [items/W-00000250/_story.md](items/W-00000250/_story.md) | 무인 실행이 끝난 뒤 사람이 잇는 구간에서 게이트가 안 막게 한다 |
| W-00000253 | completed | [items/W-00000253/_story.md](items/W-00000253/_story.md) | 담을 경로 중 아직 없는 것을 걸러 낸다 |
| W-00000254 | completed | [items/W-00000254/_story.md](items/W-00000254/_story.md) | 세션 시작이 프로젝트 규칙 파일 이름을 싣게 한다 |
| W-00000255 | completed | [items/W-00000255/_story.md](items/W-00000255/_story.md) | 들이는 명령이 바뀐 규칙 파일을 알린다 |
| W-00000246 | completed | [items/W-00000246/_story.md](items/W-00000246/_story.md) | 세션 시작이 프로젝트 규칙을 싣게 한다 |
| W-00000249 | completed | [items/W-00000249/_story.md](items/W-00000249/_story.md) | 마일스톤 완료 기준을 여러 개 받게 한다 |
| W-00000247 | rejected | [items/W-00000247/_story.md](items/W-00000247/_story.md) | 인라인 인터프리터를 셸 인자로 넘겨도 게이트가 걸리게 한다 |
| W-00000256 | completed | [items/W-00000256/_story.md](items/W-00000256/_story.md) | 실행 전후의 카드 파일 목록을 대조해 달라졌으면 보고에 남긴다 |
| W-00000257 | completed | [items/W-00000257/_story.md](items/W-00000257/_story.md) | 세션 시작이 venue 별로 어떻게 돌리는지까지 말하게 한다 |
| W-00000243 | completed | [items/W-00000243/_story.md](items/W-00000243/_story.md) | 결정을 세우기 전에 최소 구현으로 확인하는 걸음을 넣는다 |
| W-00000251 | completed | [items/W-00000251/_story.md](items/W-00000251/_story.md) | 실행하는 쪽이 자기 카드의 파일 목록을 못 넓히게 한다 |
| W-00000258 | completed | [items/W-00000258/_story.md](items/W-00000258/_story.md) | 회고 번호를 카드 번호에서 만들지 말고 빈 번호를 잡는다 |
| W-00000259 | completed | [items/W-00000259/_story.md](items/W-00000259/_story.md) | 회고 번호를 세지 말고 카드 번호에서 만들고, 자리가 차 있으면 멈춘다 |
| W-00000260 | completed | [items/W-00000260/_story.md](items/W-00000260/_story.md) | 드라이버를 돌리기 전에 작업 트리를 비우라는 것을 규칙에 넣는다 |
| W-00000261 | completed | [items/W-00000261/_story.md](items/W-00000261/_story.md) | 한국어 쓰는 법을 한국어로, 낱말 목록이 아니라 규칙으로 다시 적는다 |
| W-00000262 | completed | [items/W-00000262/_story.md](items/W-00000262/_story.md) | Plainly의 한국어 지침을 비유 없이 다시 쓴다 |
| W-00000283 | completed | [items/W-00000283/_story.md](items/W-00000283/_story.md) | 범위를 넘은 호출의 훅 메시지를 대화창 한 줄과 에이전트 맥락으로 나눈다 |
| W-00000284 | completed | [items/W-00000284/_story.md](items/W-00000284/_story.md) | 리뷰가 사례로 거부하면 그 종류 전체를 막도록 실행·리뷰 계약을 고친다 |
| W-00000285 | completed | [items/W-00000285/_story.md](items/W-00000285/_story.md) | Codex 드라이버 명령에 gpt-6-sol 모델을 다시 적는다 |
| W-00000268 | completed | [items/W-00000268/_story.md](items/W-00000268/_story.md) | 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다 |
| W-00000269 | completed | [items/W-00000269/_story.md](items/W-00000269/_story.md) | 닫기 전 리뷰의 기준별 판정을 카드에 적는다 |
| W-00000270 | completed | [items/W-00000270/_story.md](items/W-00000270/_story.md) | 닫기 전 리뷰에 일반 검사와 따로 제한 시간을 준다 |
| W-00000286 | completed | [items/W-00000286/_story.md](items/W-00000286/_story.md) | 닫기 리뷰가 판정 파일을 쓰게 하고 Codex 명령을 gpt-6-astra high로 고정한다 |
| W-00000287 | completed | [items/W-00000287/_story.md](items/W-00000287/_story.md) | 실행자가 정한 것을 닫을 때 카드에 남긴다 |
| W-00000289 | completed | [items/W-00000289/_story.md](items/W-00000289/_story.md) | codex 명령이 설치된 컴패니언 스크립트를 찾아 쓴다 |
| W-00000290 | completed | [items/W-00000290/_story.md](items/W-00000290/_story.md) | 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구를 둔다 |
| W-00000291 | completed | [items/W-00000291/_story.md](items/W-00000291/_story.md) | 병렬 브랜치가 같은 기록 번호를 쓰지 않게 한다 |
| W-00000292 | completed | [items/W-00000292/_story.md](items/W-00000292/_story.md) | 실행 환경을 venue 와 나누고 클라우드 실행을 정책으로 허용한다 |
| W-00000293 | completed | [items/W-00000293/_story.md](items/W-00000293/_story.md) | 계획 카드 등록도 겹친 번호의 브랜치 이름을 보여 준다 |
| W-00000294 | completed | [items/W-00000294/_story.md](items/W-00000294/_story.md) | 닫기 도구가 감사와 같은 승격 기록 검사를 쓴다 |
| W-00000295 | completed | [items/W-00000295/_story.md](items/W-00000295/_story.md) | claude 리뷰어에게 판정 파일 쓰기와 시험 실행만 허락한다 |
| W-00000296 | completed | [items/W-00000296/_story.md](items/W-00000296/_story.md) | claude 리뷰어 권한에서 쓰이지 않는 Write 규칙을 뺀다 |
| W-00000297 | completed | [items/W-00000297/_story.md](items/W-00000297/_story.md) | 드라이버가 닫을 때도 긴 리뷰 제한 시간을 쓰게 한다 |
| W-00000300 | completed | [items/W-00000300/_story.md](items/W-00000300/_story.md) | 드라이버가 실행자가 바꾼 닫기 도구 몫의 카드 칸을 거절한다 |
| W-00000301 | completed | [items/W-00000301/_story.md](items/W-00000301/_story.md) | 보관한 뒤 대기 결정 목록을 옮겨진 카드에 맞춘다 |
| W-00000302 | completed | [items/W-00000302/_story.md](items/W-00000302/_story.md) | 리뷰 판정 검증을 닫기 도구와 드라이버가 한 함수로 나눠 쓴다 |
| W-00000303 | completed | [items/W-00000303/_story.md](items/W-00000303/_story.md) | 여러 판의 실행 보고를 판마다 커밋을 모아 옮긴다 |
| W-00000305 | completed | [items/W-00000305/_story.md](items/W-00000305/_story.md) | 판 사이에 완료 기준이 바뀌면 전체 리뷰로 다시 판정한다 |
| W-00000306 | completed | [items/W-00000306/_story.md](items/W-00000306/_story.md) | 사용량 한도로 끝난 리뷰는 시도를 쓰지 않는다 |
| W-00000307 | completed | [items/W-00000307/_story.md](items/W-00000307/_story.md) | 시도 횟수를 되돌릴 때 지난 판정과 쌓인 변경 경로도 지운다 |
| W-00000309 | completed | [items/W-00000309/_story.md](items/W-00000309/_story.md) | Claude 리뷰어의 파일 쓰기 제한을 실제 리뷰 경로에서 검증합니다 |
| W-00000310 | completed | [items/W-00000310/_story.md](items/W-00000310/_story.md) | 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다 |
| W-00000311 | completed | [items/W-00000311/_story.md](items/W-00000311/_story.md) | 범위 넘음 알림에서 고치지 않은 경로를 뺀다 |
| W-00000312 | completed | [items/W-00000312/_story.md](items/W-00000312/_story.md) | Stage 0.64.0 을 출시한다 — 리뷰 쓰기 검사와 범위 알림 정리 |
| W-00000313 | completed | [items/W-00000313/_story.md](items/W-00000313/_story.md) | rag 서버에 ruff·mypy 를 들이고 지적을 정리한다 |
| W-00000314 | completed | [items/W-00000314/_story.md](items/W-00000314/_story.md) | 번호 도구가 제목 줄에만 번호가 있는 기록도 센다 |
| W-00000315 | completed | [items/W-00000315/_story.md](items/W-00000315/_story.md) | 시도 횟수를 되돌릴 때 멈춘 판의 작업을 정리한다 |
| W-00000316 | completed | [items/W-00000316/_story.md](items/W-00000316/_story.md) | 마일스톤 완료 기준 앞의 목록 기호가 겹치지 않게 한다 |
| W-00000317 | completed | [items/W-00000317/_story.md](items/W-00000317/_story.md) | 실패한 리뷰가 남긴 파일이 다음 판에 섞이지 않게 한다 |
| W-00000318 | completed | [items/W-00000318/_story.md](items/W-00000318/_story.md) | 실행을 요구하는 기준의 판정에 실제로 돌렸는지를 남긴다 |
| W-00000319 | completed | [items/W-00000319/_story.md](items/W-00000319/_story.md) | CI 에서 드러난 Stage 의 Windows·작업 폴더 버그를 고친다 |
| W-00000320 | completed | [items/W-00000320/_story.md](items/W-00000320/_story.md) | Ubuntu 러너에서 Python 3.9 시험이 계속 돌게 한다 |
| W-00000321 | completed | [items/W-00000321/_story.md](items/W-00000321/_story.md) | Windows 셸 파서가 드라이브에 붙인 /dev/null 도 장치로 알아본다 |
| W-00000322 | completed | [items/W-00000322/_story.md](items/W-00000322/_story.md) | Stage 0.65.0 을 출시한다 — 버그 정리와 CI 복구 |
| W-00000288 | completed | [items/W-00000288/_story.md](items/W-00000288/_story.md) | 상태 기록의 work_items 연결 검사가 계획 칸 카드도 센다 |
| W-00000298 | completed | [items/W-00000298/_story.md](items/W-00000298/_story.md) | 실제 codex 플러그인으로 codex 명령 경로 찾기를 확인한다 |
| W-00000299 | completed | [items/W-00000299/_story.md](items/W-00000299/_story.md) | 클라우드에서 닫은 카드를 로컬 codex 로 표본 재검토한다 |
| W-00000272 | completed | [items/W-00000272/_epic.md](items/W-00000272/_epic.md) | Stage·Distill·Avatar로 기준 변경과 세션 인계를 연결한다 |
| W-00000323 | completed | [items/W-00000323/_story.md](items/W-00000323/_story.md) | codex 구독이 없는 동안 로컬 카드도 Claude가 실행하도록 환경을 선언한다 |
| W-00000324 | completed | [items/W-00000324/_story.md](items/W-00000324/_story.md) | codex 가 없는 동안 권한·닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다 |
| W-00000325 | completed | [items/W-00000325/_story.md](items/W-00000325/_story.md) | 루트 CLAUDE.md 에서 코드로 알 수 있는 내용을 지운다 |
| W-00000326 | completed | [items/W-00000326/_epic.md](items/W-00000326/_epic.md) | 일감마다 맞는 모델과 에포트 레벨을 Stage 가 고르게 한다 |
| W-00000332 | completed | [items/W-00000332/_story.md](items/W-00000332/_story.md) | 범위 넘음 알림에서 프로젝트 밖 경로와 같은 명령에서 정한 변수 경로를 뺀다 |
| W-00000333 | completed | [items/W-00000333/_story.md](items/W-00000333/_story.md) | stage 0.66.0 을 낸다 |
| W-00000334 | completed | [items/W-00000334/_story.md](items/W-00000334/_story.md) | 세션 시작 글에 인라인 코드 규칙을 싣는다 |
| W-00000304 | completed | [items/W-00000304/_story.md](items/W-00000304/_story.md) | worktree에 들어간 Claude 세션에서 훅이 그 worktree를 작업 루트로 판정하게 한다 |
| W-00000308 | completed | [items/W-00000308/_story.md](items/W-00000308/_story.md) | worktree 진입 판정 수정(W-00000304)을 담은 stage 패치를 출시하고 설치본을 업데이트한다 |
| W-00000335 | completed | [items/W-00000335/_story.md](items/W-00000335/_story.md) | cd 로 들어간 폴더 아래에서도 같은 명령에서 정한 변수 경로를 풀어 범위 알림에서 뺀다 |
| W-00000336 | completed | [items/W-00000336/_story.md](items/W-00000336/_story.md) | stage 0.66.1 을 낸다 |
| W-00000337 | completed | [items/W-00000337/_story.md](items/W-00000337/_story.md) | DE-00000082 를 공식 결정 기록으로 올린다 |
| W-00000263 | completed | [items/W-00000263/_epic.md](items/W-00000263/_epic.md) | 플레인리 스타일을 클로드 코드 output style 로 내보낸다 |
| W-00000338 | completed | [items/W-00000338/_story.md](items/W-00000338/_story.md) | 등록 게이트도 같은 명령에서 정한 변수 경로를 풀어서 판정한다 |
| W-00000339 | completed | [items/W-00000339/_story.md](items/W-00000339/_story.md) | 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다 |
| W-00000340 | completed | [items/W-00000340/_story.md](items/W-00000340/_story.md) | 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다 |
| W-00000341 | completed | [items/W-00000341/_story.md](items/W-00000341/_story.md) | stage 0.66.2 를 낸다 |
| W-00000342 | completed | [items/W-00000342/_story.md](items/W-00000342/_story.md) | 게이트가 셸 명령의 상대 경로를 셸이 실제로 있는 폴더에서 읽는다 |
| W-00000343 | completed | [items/W-00000343/_story.md](items/W-00000343/_story.md) | stage 0.66.3 을 낸다 |
| W-00000344 | completed | [items/W-00000344/_story.md](items/W-00000344/_story.md) | 플레인리를 켜면 스타일이 바로 적용되게 하고 비교 실험을 기본 평가 명령으로 옮긴다 |
| W-00000345 | completed | [items/W-00000345/_story.md](items/W-00000345/_story.md) | plainly 0.8.0 을 낸다 |
| W-00000346 | completed | [items/W-00000346/_story.md](items/W-00000346/_story.md) | 게이트가 변수로 쓴 cd 와 && 로 이어진 cd 를 따라가서 쓰기 대상을 읽는다 |
| W-00000347 | completed | [items/W-00000347/_story.md](items/W-00000347/_story.md) | stage 0.66.4 를 낸다 |
| W-00000348 | completed | [items/W-00000348/_story.md](items/W-00000348/_story.md) | rag 플러그인에 개발을 멈췄다고 표시하기 |
| W-00000349 | completed | [items/W-00000349/_story.md](items/W-00000349/_story.md) | --scope 를 여러 번 넘기면 모든 경로를 카드에 담기 |
| W-00000350 | completed | [items/W-00000350/_story.md](items/W-00000350/_story.md) | stage 0.66.5 를 낸다 |
| W-00000351 | completed | [items/W-00000351/_story.md](items/W-00000351/_story.md) | flutter-cask 와 pencil-m3-flutter 에 개발을 멈췄다고 표시하기 |
| W-00000354 | completed | [items/W-00000354/_story.md](items/W-00000354/_story.md) | Stage 테스트가 자식 프로세스 출력을 UTF-8로 읽게 고치기 |
| W-00000352 | completed | [items/W-00000352/_story.md](items/W-00000352/_story.md) | 자식 프로세스 출력을 로캘 인코딩이 아니라 UTF-8 로 읽기 |
| W-00000353 | completed | [items/W-00000353/_story.md](items/W-00000353/_story.md) | 카드 번호에서 만든 회고 번호를 다른 카드가 쓰고 있으면 주인을 따라가 빈 번호를 잡기 |
| W-00000355 | completed | [items/W-00000355/_story.md](items/W-00000355/_story.md) | stage 0.66.6 을 낸다 |
| W-00000356 | completed | [items/W-00000356/_story.md](items/W-00000356/_story.md) | evonest 가 Windows 한국어 로캘에서도 동작하고 테스트가 통과하게 고치기 |
| W-00000357 | completed | [items/W-00000357/_story.md](items/W-00000357/_story.md) | evonest 의 mypy 검사가 Windows 에서도 통과하게 고치기 |
| W-00000358 | completed | [items/W-00000358/_story.md](items/W-00000358/_story.md) | 훅 명령이 Windows에서는 python을 부르게 고친다 |
| W-00000360 | completed | [items/W-00000360/_story.md](items/W-00000360/_story.md) | 훅 고침 브랜치에 main을 합쳐 PR #69의 충돌을 푼다 |
| W-00000359 | completed | [items/W-00000359/_story.md](items/W-00000359/_story.md) | 리뷰 명령을 셸 문법 없이 Python 스크립트로 실행하기 |
| W-00000361 | completed | [items/W-00000361/_story.md](items/W-00000361/_story.md) | PR #71 브랜치에 main을 합쳐 충돌을 푼다 |
| W-00000362 | completed | [items/W-00000362/_story.md](items/W-00000362/_story.md) | Stage 0.67.0 과 evonest 1.2.1 을 낸다 |
| W-00000363 | completed | [items/W-00000363/_story.md](items/W-00000363/_story.md) | 카드 한 장에 드는 문서와 절차에서 덜어낼 것을 정한다 |
| W-00000368 | completed | [items/W-00000368/_story.md](items/W-00000368/_story.md) | 닫기와 보관을 한 번에 하게 고친다 |
| W-00000369 | completed | [items/W-00000369/_story.md](items/W-00000369/_story.md) | 닫을 때 카드에 붙는 출력을 판정 한 줄로 줄인다 |
| W-00000370 | completed | [items/W-00000370/_story.md](items/W-00000370/_story.md) | 카드에서 회고 칸을 없애고 유지 카드는 두 가지만 묻는다 |
| W-00000364 | completed | [items/W-00000364/_story.md](items/W-00000364/_story.md) | 두 번 넘게 겪은 실수 세 가지를 규칙 문서에 올린다 |
| W-00000365 | completed | [items/W-00000365/_story.md](items/W-00000365/_story.md) | 다음에 할 일의 순서를 .stage 로 옮긴다 |
| W-00000373 | completed | [items/W-00000373/_story.md](items/W-00000373/_story.md) | 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다 |
| W-00000366 | completed | [items/W-00000366/_story.md](items/W-00000366/_story.md) | 도면의 위 두 층을 쓰고 도면 자리를 한 곳으로 정한다 |
| W-00000374 | completed | [items/W-00000374/_story.md](items/W-00000374/_story.md) | Windows 에서 리뷰어가 PowerShell 도구로도 테스트를 실행하게 하기 |
| W-00000375 | completed | [items/W-00000375/_story.md](items/W-00000375/_story.md) | PR #85 브랜치에 main 을 합쳐 충돌을 푼다 |
| W-00000376 | completed | [items/W-00000376/_story.md](items/W-00000376/_story.md) | PR 브랜치에서 CI 가 같은 테스트를 한 번만 실행하게 하기 |
| W-00000367 | completed | [items/W-00000367/_story.md](items/W-00000367/_story.md) | 여러 세션이 목록 파일과 카드 번호에서 부딪히지 않게 설계한다 |
| W-00000379 | completed | [items/W-00000379/_story.md](items/W-00000379/_story.md) | Stage CI 의 테스트를 여러 잡으로 나눠 PR 결과가 빨리 나온다 |
| W-00000378 | completed | [items/W-00000378/_story.md](items/W-00000378/_story.md) | 카드와 기록을 등록할 때 번호를 원격에 잡는다 |
| W-00000371 | completed | [items/W-00000371/_story.md](items/W-00000371/_story.md) | 회고에 남길 칸을 정한다 |
| W-00000377 | completed | [items/W-00000377/_story.md](items/W-00000377/_story.md) | 목록 파일을 union 으로 합치고 줄을 지우는 목록은 카드에서 만든다 |
| W-00000380 | completed | [items/W-00000380/_story.md](items/W-00000380/_story.md) | Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축 |
| W-00000385 | completed | [items/W-00000385/_story.md](items/W-00000385/_story.md) | 메인 세션이 서브세션에 일과 번호 묶음을 나눠 주는 방법을 설계한다 |
| W-00000387 | completed | [items/W-00000387/_story.md](items/W-00000387/_story.md) | 다른 브랜치에서 이미 시작했거나 끝난 카드는 시작하지 않는다 |
| W-00000383 | completed | [items/W-00000383/_story.md](items/W-00000383/_story.md) | 옛 목록 파일이 남은 프로젝트를 옮길 때 그 파일을 지운다 |
| W-00000388 | completed | [items/W-00000388/_story.md](items/W-00000388/_story.md) | 메인 세션이 서브세션에 일을 맡기고 닫는 절차와 번호 묶음을 만든다 |
| W-00000384 | completed | [items/W-00000384/_story.md](items/W-00000384/_story.md) | 릴리스와 변경 기록 줄 추가가 겹칠 때 union 병합 결과를 확인한다 |
| W-00000381 | completed | [items/W-00000381/_story.md](items/W-00000381/_story.md) | Windows 에서 검사와 리뷰의 시간 제한이 실제로 끊게 한다 |
| W-00000382 | completed | [items/W-00000382/_story.md](items/W-00000382/_story.md) | 드라이버가 저장소 상태를 볼 때 띄우는 git 프로세스를 줄인다 |
| W-00000390 | completed | [items/W-00000390/_story.md](items/W-00000390/_story.md) | 서브세션 브리핑에 범위 넘기 보고와 Windows 확인 방법을 넣는다 |
| W-00000392 | completed | [items/W-00000392/_story.md](items/W-00000392/_story.md) | 릴리스된 변경 기록 절에 나중에 끼어든 줄을 찾는다 |
| W-00000389 | completed | [items/W-00000389/_story.md](items/W-00000389/_story.md) | W-00000381, W-00000382, W-00000384 에서 사용자가 정한 것을 기록에 남긴다 |
| W-00000393 | completed | [items/W-00000393/_story.md](items/W-00000393/_story.md) | release_plugin.py 가 Windows 에서도 UTF-8 로 출력하게 한다 |
| W-00000391 | completed | [items/W-00000391/_story.md](items/W-00000391/_story.md) | 드라이버의 닫기와 보류 호출, 리뷰어 실행에도 프로세스 트리 시간 제한을 건다 |
| W-00000395 | completed | [items/W-00000395/_story.md](items/W-00000395/_story.md) | 새 코드 파일은 도면 레이어 표에 넣는다는 규칙을 올린다 |
| W-00000396 | completed | [items/W-00000396/_story.md](items/W-00000396/_story.md) | 릴리스된 절 점검이 기준 버전 이후만 보게 한다 |
| W-00000394 | completed | [items/W-00000394/_story.md](items/W-00000394/_story.md) | 한국어 Windows 에서 close_work 시험과 검사 출력이 깨지지 않게 한다 |
| W-00000386 | completed | [items/W-00000386/_story.md](items/W-00000386/_story.md) | 실행자 모델이 사용량 한도에 걸리면 같은 venue의 다른 모델로 넘어가는 순서를 둔다 |
| W-00000397 | completed | [items/W-00000397/_story.md](items/W-00000397/_story.md) | 출발점이 된 글 네 편을 연구 자료로 남긴다 |
| W-00000398 | completed | [items/W-00000398/_story.md](items/W-00000398/_story.md) | 로드맵 기록 번호도 잡아 둔 번호와 다른 브랜치 번호를 피한다 |
| W-00000399 | completed | [items/W-00000399/_story.md](items/W-00000399/_story.md) | Stage 의 통제 장치와 그것이 담은 가정을 목록으로 만든다 |
| W-00000402 | completed | [items/W-00000402/_story.md](items/W-00000402/_story.md) | 서브세션을 기본으로 쓰고 카드에는 실행 방식을 적지 않는 일하는 방식을 정한다 |
| W-00000404 | completed | [items/W-00000404/_story.md](items/W-00000404/_story.md) | stage-orchestrate 스킬과 역할별 브리핑을 만든다 |
| W-00000403 | completed | [items/W-00000403/_story.md](items/W-00000403/_story.md) | 실행 방식 지시(B11)를 빼 보고 하중을 본다 |
| W-00000401 | completed | [items/W-00000401/_story.md](items/W-00000401/_story.md) | 닫기 리뷰가 실제로 실행해 보고 회의적으로 판정하게 하는 방법을 정한다 |
| W-00000400 | completed | [items/W-00000400/_story.md](items/W-00000400/_story.md) | 세션 시작에 싣는 층을 작게 두고 기억을 잘 꺼내 쓰는 구조를 정한다 |
| W-00000406 | completed | [items/W-00000406/_story.md](items/W-00000406/_story.md) | 첫 실전에서 드러난 stage-orchestrate 의 빈 곳을 메운다 |
| W-00000405 | completed | [items/W-00000405/_story.md](items/W-00000405/_story.md) | 뺀 장치의 하중을 커밋된 기록으로 잴 수 있게 한다 |
| W-00000408 | completed | [items/W-00000408/_story.md](items/W-00000408/_story.md) | 닫기 리뷰어가 실행해서 판정하고 판정 방법이 카드에 남는다 |
| W-00000409 | completed | [items/W-00000409/_story.md](items/W-00000409/_story.md) | 세션의 맨 위 층이 기록에서 만든 색인을 싣는다 |
| W-00000410 | completed | [items/W-00000410/_story.md](items/W-00000410/_story.md) | 지난 카드들의 보고에 남은 작은 고침 넷을 넣는다 |
| W-00000415 | completed | [items/W-00000415/_story.md](items/W-00000415/_story.md) | 쌓인 규칙 후보를 처음으로 한 목록에 묶는다 |
| W-00000411 | completed | [items/W-00000411/_epic.md](items/W-00000411/_epic.md) | 지휘와 닫기 절차, 리뷰 증거에 남은 빈 곳을 메운다 |
| W-00000414 | completed | [items/W-00000414/_story.md](items/W-00000414/_story.md) | 지금의 닫기 리뷰어를 결함이 기록된 과거 변경으로 잰다 |
| W-00000417 | completed | [items/W-00000417/_story.md](items/W-00000417/_story.md) | 세션 시작의 고정 규칙 문장을 줄여 색인의 자리를 만든다 |
| W-00000416 | completed | [items/W-00000416/_story.md](items/W-00000416/_story.md) | 닫기 리뷰어가 저장소 밖을 읽거나 고친 것을 되돌려 숨기지 못한다 |
