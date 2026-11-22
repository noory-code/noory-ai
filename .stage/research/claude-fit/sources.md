# 출발점이 된 글 네 편

사용자가 2026-11-23 에 [M-00000006](../../roadmap/milestones/M-00000006.md) 의 출발점으로 준 글입니다.
요약은 W-00000397 에서 각 글을 끝까지 읽고 적었습니다. 인용은 원문 그대로이고, 나머지는 옮겨 쓴 요약입니다.
'Stage 에 비춰 본 점'은 가설이며, 확인한 사실과 추측을 구별해 적었습니다.

## 1. The components of agent memory

- 주소: https://www.anthropic.com/research/components-of-agent-memory
- 글쓴이와 날짜: Lance Martin, 2026-11-06 (Engineering)

### 요약

- 에이전트 기억을 '세션 사이에 사람이 읽을 수 있는 맥락으로 남는 지식'으로 정의합니다.
  가중치 변경, 문맥 내 학습, 압축(compaction)은 여기서 뺍니다.
- 층을 나눕니다. 원본 기록(검색 가능한 세션 기록)을 그때그때 남기고, 나중에 오래 갈 메모로 정리합니다.
  매 세션에 싣는 맨 위 층은 작게 두고 나머지는 필요할 때 읽거나 찾습니다.
  Claude Code 의 auto memory 는 `MEMORY.md` 의 처음 200줄 또는 25 KB 만 싣고, 그 파일은 색인 역할을 합니다.
- 정리 단계를 'dreaming' 이라 부릅니다. 세션 밖에서 기록을 되돌아보며 틀린 메모를 고치고 새 메모를 씁니다.
  Mt. Moon 예에서는 위치를 잘못 적은 메모를 원본 기록과 대조해 고친 뒤 진행이 회복됐습니다.
- 남길 것은 화면이나 환경이 보여 주지 않는 것(전략, 계획, 검증한 규칙)입니다. 다시 보면 아는 상태는 남길 가치가 낮습니다.
- 수치: CL-Bench 데이터베이스 과제에서 Opus 5.5 가 기억 없이 0.655, 기억과 함께 0.838.
  포켓몬 레드에서 Sonnet 3.7 은 메모 파일 413개로 배지 1개, Fable 5 는 약 10개로 배지 4개.
  Stainless 위키 과제는 dreaming 을 거치며 13% 에서 48%, Harvey LAB 은 계약 조건 수정 뒤 72% 에서 100%.
- 기억의 쓰임을 모델에게 알려 주면 도움이 되지만, '실패만 기록하라' 같은 고정 규칙은 강한 모델을 오히려 해칩니다.
  약한 모델(Sonnet 4.6)은 기억을 읽고 가설을 시험하라는 지시가 필요했습니다.
- 인용: "Injected memories use up valuable tokens, and an incorrect note can be carried into every session."
- 인용: "Dreaming gives Claude an opportunity to look _backward_ and use compute to organize its memory"

### Stage 에 비춰 본 점

- 확인한 사실: Stage 의 SessionStart 훅(`stage/hooks/stage_context.py`)은 이미 싣는 양을 묶어 둡니다.
  파일 한 조각은 기본 1400자, 기록 종류마다 3건, 한 줄 160자이고, 잘리면 어디를 더 읽으라고 적습니다.
  글의 '작은 맨 위 층 + 색인' 구조와 방향이 같습니다. 다만 전체 상한(모든 조각을 합친 크기)은 정해져 있지 않습니다.
- 확인한 사실: 실행 중 작업 기록은 `.stage/.runtime/` 에 있고 커밋되지 않습니다(`stage/operations/review.md`).
  카드에는 실행 보고의 몇 줄만 옮겨집니다. 글의 기준으로 보면 원본 기록이 세션 뒤에 사라지는 구조입니다.
- 가설: Stage 의 회고와 결정 기록은 dreaming 이 만드는 '정리된 메모'에 해당합니다.
  사용자가 지킬 강점으로 꼽은 것이 바로 이 층입니다. 글이 더하는 것은 정리된 메모를 원본과 대조해 고치는 단계입니다.
- 반대 관점: 글의 수치는 게임, 벤치마크, 위키처럼 정답을 채점할 수 있는 과제에서 나왔습니다.
  Stage 의 결정 기록은 사람의 판단이 원본이라, 모델이 '틀린 메모를 고친다'는 동작이 사람이 정한 결정을 덮어쓸 위험이 있습니다.
- 반대 관점: '고정 규칙이 강한 모델을 해친다'는 관찰은 Stage 의 금지 문구 목록이나 YAML 조건 같은 결정론적 지시와 부딪힙니다.
  어느 규칙이 하중을 받는지는 빼 보기 전에는 알 수 없습니다.

## 2. Scaling Managed Agents with stable interfaces

- 주소: https://www.anthropic.com/research/managed-agents
- 글쓴이와 날짜: Lance Martin, Gabe Cemaj, Michael Cohen, 2026-04-08 (Engineering). 본문 제목은 "Decoupling the brain from the hands".

### 요약

- 하네스는 Claude 가 혼자 못 하는 일에 대한 가정을 담고, 그 가정은 모델이 나아지면 낡습니다.
  Sonnet 4.5 의 context anxiety 때문에 넣은 컨텍스트 리셋은 Opus 4.5 에서 "dead weight" 가 됐습니다.
- 세 부분을 따로 바꿀 수 있게 나눕니다. 세션(일어난 모든 일의 덧붙이기 전용 기록), 하네스(Claude 를 부르고
  도구 호출을 나르는 루프), 샌드박스(코드가 도는 곳). 하네스가 죽어도 기록의 마지막 사건부터 다시 시작합니다.
- 인터페이스는 작습니다: `execute(name, input) → string`, `provision`, `wake`, `getSession`, `emitEvent`, `getEvents`.
- 세션은 Claude 의 컨텍스트 창이 아닙니다. 압축이나 기억 도구의 요약은 되돌릴 수 없는 선택이라 필요한 정보를 잃을 수 있고,
  그래서 원본을 세션 기록에 남기고 무엇을 실을지는 하네스가 그때 고릅니다.
- 자격 증명은 샌드박스 밖에 둡니다(git 토큰은 원격 설정에, MCP 호출은 금고에서 자격을 꺼내는 프록시로).
- 프로비저닝을 필요할 때 하는 도구 호출로 옮겨 첫 토큰까지의 시간이 p50 약 60%, p95 90% 넘게 줄었습니다.
  기억의 품질을 잰 수치는 없습니다.
- 인용: "harnesses encode assumptions about what Claude can’t do on its own."
- 인용: "the session is durable and available for interrogation"

### Stage 에 비춰 본 점

- 가설: Stage 의 카드, 결정, 회고는 git 에 남는 '세션 밖 기록'이라 이미 이 글의 세션 기록과 비슷한 역할을 합니다.
  빠진 쪽은 위 1번과 같이 작업 중의 원본 기록입니다.
- 확인한 사실: 클라우드 실행에서는 Stage 훅도 `.stage/.runtime/` 도 없어서 실행 보고를 커밋 본문에 씁니다
  (`stage/operations/cloud-execution.md`). 원본을 실행 환경과 떼어 git 에 두는 방향이라는 점에서 이 글과 맞습니다.
- 가설: venue 중립은 이 글의 '하네스를 바꿔 끼울 수 있게' 와 같은 생각입니다. 실행자(claude, codex, agy)를 바꿔도
  카드와 기록이 그대로면 됩니다.
- 반대 관점: 이 글은 기반 시설(지연 시간, 장애 복구, 보안)의 글이고, 작업의 목적이나 판정은 다루지 않습니다.
  Stage 에 옮길 수 있는 것은 '원본을 지우지 말라'와 '가정은 낡는다' 두 원칙 정도입니다.

## 3. Building a C compiler with a team of parallel Claudes

- 주소: https://www.anthropic.com/research/building-c-compiler
- 글쓴이와 날짜: Nicholas Carlini, 2026-02-05 (Engineering)

### 요약

- 세션이 끝나면 Claude Code 를 다시 띄우는 루프로, 사람 없이 에이전트 16개가 약 2,000 세션, 약 2만 달러로
  Rust 로 된 약 10만 줄 C 컴파일러를 만들었습니다. x86, ARM, RISC-V 에서 Linux 6.9 를 빌드합니다.
- 조정 장치는 단순합니다. 공용 bare git 저장소, 에이전트마다 별도 컨테이너, `current_tasks/` 의 텍스트 파일 잠금,
  git 충돌이 나면 다른 일을 고르기. 지휘하는 에이전트도 에이전트 사이의 대화도 없습니다.
  중복 제거, 성능, 코드 품질, 문서 같은 전담 역할은 따로 두었습니다.
- 검사가 주된 통제 수단입니다. 좋은 테스트 묶음을 찾고, 검증기를 쓰고, CI 로 기존 테스트를 깨는 커밋을 막았습니다.
  출력은 모델이 읽기 좋게 몇 줄로 줄이고 오류에 `ERROR` 를 붙이고, `--fast` 로 표본만 돌리게 했습니다.
- 모든 에이전트가 같은 버그에 막혔을 때는 GCC 를 정답 기준(oracle)으로 써서 파일 일부만 자기 컴파일러로 빌드하고
  delta debugging 으로 실패한 짝을 좁혔습니다.
- 에이전트에게 README 와 진행 파일, 실패한 접근의 기록을 계속 고치게 했습니다.
- 한계: 16비트 x86 코드 생성은 GCC 를 부르고, 어셈블러와 링커가 없고, 새 기능이 기존 기능을 자주 깼습니다.
- 인용: "the task verifier is nearly perfect, otherwise Claude will solve the wrong problem."
- 인용: "For autonomous systems, it is easy to see tests pass and assume the job is done, when this is rarely the case."

### Stage 에 비춰 본 점

- 확인한 사실: Stage 는 기록 번호를 원격에 `refs/stage-ids/<id>` 로 잡아 두고(DE-00000092), 병렬 세션은 각자 브랜치에서 일합니다.
  `current_tasks/` 잠금 파일과 같은 종류의 장치입니다.
- 대비: 이 글에는 지휘자가 없고, M-00000006 의 (라)는 메인 세션이 지휘하고 서브세션이 만듭니다(DE-00000094).
  이 글의 방식이 통한 조건은 '거의 완벽한 검증기'였습니다. Stage 의 카드는 대부분 그런 검증기가 없어서
  지휘와 독립 판정이 그 자리를 메운다고 볼 수 있습니다. 반대로 검증기가 있는 카드라면 지휘를 줄여도 되는지 시험할 만합니다.
- 가설: 이 글의 '실패한 접근 기록'은 Stage 의 회고와 관찰 기록에 해당합니다.
- 반대 관점: 2만 달러와 2,000 세션은 하나의 잘 정의된 목표(컴파일러)에 쓴 비용입니다.
  사람이 목적을 정하고 판정하는 Stage 의 일감에는 같은 규모의 무인 반복이 맞지 않을 수 있습니다.

## 4. Harness design for long-running application development

- 주소: https://www.anthropic.com/research/harness-design-long-running-apps
- 글쓴이와 날짜: Prithvi Rajasekaran, 2026-03-24 (Engineering)

### 요약

- 만드는 쪽(generator)과 판정하는 쪽(evaluator)을 나누고, 이를 계획자(planner)까지 셋으로 늘렸습니다.
- 자기 평가는 믿기 어렵습니다. 에이전트는 자기의 평범한 결과물을 칭찬합니다. 판정자를 회의적으로 맞추는 쪽이
  만드는 쪽을 자기비판적으로 만드는 것보다 훨씬 다루기 쉽다고 합니다. 몇 개의 예시로 점수 흔들림을 줄였습니다.
- 판정자는 Playwright 로 실제 페이지와 앱을 눌러 보며 기준마다 점수를 매기고, 하나라도 문턱 아래면 그 단계를 떨어뜨립니다.
- 각 단계 전에 만드는 쪽과 판정자가 '완료'의 뜻과 시험할 동작을 계약으로 정하고, 파일로 주고받습니다.
- 계획자는 짧은 요청을 높은 수준의 제품 명세로 늘리되, 세부를 정하면 오류가 이어지므로 높은 수준에 머뭅니다.
- 컨텍스트 리셋과 구조화된 인계는 Sonnet 4.5 에 필요했고 Opus 4.5 에서는 빼고 자동 압축을 썼습니다.
  Opus 4.6 판에서는 단계 구분을 없애고 판정을 끝에 한 번만 했습니다.
- 비용: 혼자 돌린 실행 9달러/20분, 전체 하네스 200달러/6시간. 판정자의 가치는 과제가 모델이 혼자 안정적으로 하는 범위의
  어디에 있느냐에 달려 있다고 합니다.
- 인용: "every component in a harness encodes an assumption about what the model can't do on its own."
- 인용: "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue."

### Stage 에 비춰 본 점

- 확인한 사실: Stage 는 이미 만드는 쪽과 닫기 리뷰어를 나눕니다. 클라우드에서는 다른 venue 대신 Claude 대역이 리뷰하고,
  카드의 Verification 에 같은 모델 리뷰였다고 적습니다(`stage/operations/cloud-execution.md`).
  글의 기준으로는 같은 모델이라도 판정을 회의적으로 맞추고 실제로 실행해 보게 하는 것이 핵심이고, 이것이 M-00000006 의 (다)입니다.
- 가설: '계획자는 높은 수준에 머문다'는 M-00000006 의 '상세한 실행 방식 설계를 뒤로 미룬다'와 같은 방향입니다.
  단계 계약(완료의 뜻과 시험할 동작)은 카드의 성공 기준과 검사에 해당합니다.
- 가설: '장치를 하나씩 빼 본다'는 방법이 M-00000006 의 (가)와 W-00000399(장치와 가정 목록)의 직접 출처입니다.
- 반대 관점: 글쓴이도 판정자가 여전히 "inclined to be generous" 한 LLM 이라고 적습니다. 같은 모델의 회의적 판정만으로는
  모델 계열 공통의 맹점을 못 잡을 수 있고, 이것이 Stage 가 venue 교차 리뷰를 유지할 이유가 됩니다.
- 반대 관점: 20배 넘는 비용 차이는 판정자가 공짜가 아님을 보여 줍니다. 판정 장치도 빼 보기의 대상이 될 수 있습니다.
