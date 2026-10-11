# 연구자료와 확인한 범위

S01부터 S14까지는 **2026-10-04**, S15부터 S27까지는 **2026-10-05**에 확인했습니다.
게시일과 확인일을 구별합니다.
아래 자료는 공식 문서, 개발사의 연구 발표, 논문, 공개 소스입니다.
API 동작을 설명하는 문서는 해당 제품의 계약을 확인하는 데 씁니다.
개발사의 성능 주장은 독립된 검증 결과와 구별합니다.
원문 전문은 저장하지 않았습니다. 다시 조사할 때 링크와 절 제목으로 확인합니다.

<a id="s01"></a>
## S01 OpenAI의 에이전트 실행

- 원문: [Running agents](https://developers.openai.com/api/docs/guides/agents/running-agents)
- 종류: 공식 개발 문서. 게시일은 확인하지 못했습니다.
- 확인한 절: `The agent loop`, `Choose one conversation strategy`.
- 확인한 내용: SDK는 모델 응답을 보고 도구를 실행하거나 다른 에이전트로 넘깁니다. 최종 응답이면 실행을 끝냅니다. 대화 상태를 이어가는 방식도 설명합니다.
- 한계: SDK 계약이며 ChatGPT나 Codex 앱 내부 전체를 공개한 자료는 아닙니다.
- 연구에 쓰는 이유: 모델이 만든 선택과 프로그램이 수행한 실행을 구별합니다.

<a id="s02"></a>
## S02 Anthropic의 에이전트 구성

- 원문: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- 종류: 공식 엔지니어링 글. 최초 게시일 2024-12-19.
- 확인한 절: `What are agents?`, `Building blocks`, `Agents`.
- 확인한 내용: 정해진 경로를 따르는 작업과 모델이 경로를 고르는 작업을 구별합니다. 검색·도구·기억을 연결하고 실행 결과를 다시 받는 구조를 설명합니다.
- 한계: 페이지도 당시 도구 환경이 달라졌다고 알립니다. 구조를 이해하는 자료로 쓰며 최신 제품 명세로 취급하지 않습니다.
- 연구에 쓰는 이유: 사람이 정한 순서와 모델이 고른 순서를 따로 기록합니다.

<a id="s03"></a>
## S03 Anthropic의 문맥 관리

- 원문: [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- 종류: 공식 엔지니어링 글. 게시일 2025-09-29.
- 확인한 절: `Context retrieval and agentic search`, `Context engineering for long-horizon tasks`.
- 확인한 내용: 자료를 미리 가져오거나 필요할 때 읽는 방식, 대화를 줄이는 방식, 외부 메모를 사용하는 방식을 설명합니다.
- 한계: 운영 경험과 권고입니다. 모든 모델이나 작업에서 같은 효과를 보장하지 않습니다.
- 연구에 쓰는 이유: 저장, 검색, 선택, 요약, 전달을 별개 동작으로 봅니다.

<a id="s04"></a>
## S04 모델이 설명한 이유와 실제 계산의 차이

- 원문: [Tracing the thoughts of a large language model](https://www.anthropic.com/research/tracing-thoughts-language-model)
- 종류: 개발사의 해석 가능성 연구 소개. 게시일 2025-03-27.
- 확인한 절: 개요, `Mental math`, `Are Claude’s explanations always faithful?`.
- 확인한 내용: 특정 모델과 작은 과제에서 내부 계산과 모델의 자기 설명이 달라지는 사례를 보고합니다.
- 한계: 관찰 방법은 전체 계산 일부만 설명합니다. 그 결과를 모든 모델의 모든 답변에 일반화할 수 없습니다.
- 연구에 쓰는 이유: 자기 설명을 실행 증거와 같은 것으로 취급하지 않습니다.

<a id="s05"></a>
## S05 토큰 생성과 캐시

- 원문: [How caching works](https://huggingface.co/docs/transformers/cache_explanation)
- 종류: Transformers 공식 구현 문서. 게시일은 확인하지 못했습니다.
- 확인한 절: 개요, `Attention matrices`, `Cache class`.
- 확인한 내용: 자기회귀 생성에서 다음 토큰은 앞선 문맥에 의존합니다. KV 캐시는 이전 attention 계산에서 얻은 일부 값을 재사용합니다.
- 한계: 특정 상용 서비스의 서버 구현, 캐시 적중 여부, 청구 방식을 알려주지는 않습니다.
- 연구에 쓰는 이유: 같은 입력을 다시 전달한 것과 같은 계산을 다시 수행한 것을 구별합니다.

<a id="s06"></a>
## S06 Gemini가 호출 사이에 보존하는 상태

- 원문: [Thought signatures](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures)
- 종류: 공식 API 문서. 확인한 페이지는 Generate Content API의 문서입니다.
- 확인한 절: `How it works`, `Signatures in function calling parts`.
- 확인한 내용: 명시된 모델의 다단계 함수 호출에서는 응답에 붙은 서명을 다음 요청에 그대로 넘겨야 합니다. 공식 SDK가 이를 처리하는 조건도 설명합니다.
- 한계: 서명은 내부 사고를 사람이 읽게 해 주는 자료가 아닙니다. 다른 API나 모델에 같은 규칙을 가정하지 않습니다.
- 연구에 쓰는 이유: 대화 문자열 외에도 이어갈 상태가 있음을 확인합니다.

<a id="s07"></a>
## S07 Grok의 도구 호출

- 원문: [Function Calling](https://docs.x.ai/developers/tools/function-calling)
- 종류: 공식 API 문서. 게시일은 확인하지 못했습니다.
- 확인한 절: `How It Works`, `Handling Tool Calls`.
- 확인한 내용: 모델이 사용자 정의 도구의 호출을 요청하면 애플리케이션이 실행하고 결과를 돌려줍니다. 서버가 실행하는 내장 도구와도 구별합니다.
- 한계: 소비자용 Grok 앱의 전체 구조를 설명하지 않습니다.
- 연구에 쓰는 이유: 모델과 도구 실행자의 책임을 나눕니다.

<a id="s08"></a>
## S08 긴 입력에서 자료 위치가 미치는 영향

- 원문: [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/)
- 종류: TACL 게재 논문. 2024년. 이번 조사에서는 초록을 확인했습니다.
- 확인한 내용: 논문이 시험한 문서 질의응답과 키값 검색에서 관련 정보의 위치에 따라 성능이 달라졌습니다.
- 한계: 당시 시험한 모델과 과제의 결과입니다. 2026년 모델의 실패율이나 최적 배치를 제공하지 않습니다. 본문 세부 조건 검토는 남아 있습니다.
- 연구에 쓰는 이유: 입력 길이뿐 아니라 순서를 통제할 실험 근거입니다.

<a id="s09"></a>
## S09 Jev를 만든 문제의식

- 원문: [Introducing System One Models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- 종류: 창업자의 제품 발표. 게시일 2026-09-15.
- 확인한 절: 도입, `Frontiers, Old and New`, `Workflow evals`, `Hallucination and Type-safety`.
- 확인한 내용: 대화 능력의 발전이 자동화로 충분히 이어지지 않았다는 문제의식을 설명합니다. 구조가 정해진 판단을 내는 모델, 병렬 출력, RLCD라는 학습법을 소개합니다.
- 한계: 비교 실험의 기준 답으로 다른 대형 모델의 평균 예측을 사용했다고 밝힙니다. 구조가 맞는 출력과 사실에 맞는 판단은 구별해야 합니다. 전체 학습법과 가중치를 재현할 자료는 이 글에서 확인하지 못했습니다.
- 연구에 쓰는 이유: 기존 작업 방식의 어느 전제를 다시 검토했는지 살펴봅니다. 제품 복제를 목표로 삼지 않습니다.

<a id="s10"></a>
## S10 Jev의 confidence가 뜻하는 것

- 원문: [Confidence](https://docs.typesafe.ai/confidence)
- 종류: 공식 API 개념 문서. 게시일은 확인하지 못했습니다.
- 확인한 내용: Choice와 Score의 confidence는 반환한 확률에서 계산합니다. Choice는 선택지 개수도 반영합니다. Noul은 별도의 confidence 없이 yes 확률을 반환합니다.
- 한계: confidence라는 이름만으로 개별 답이 맞을 확률이라고 해석하면 안 됩니다. 임계값은 실제 과제에서 검증해야 합니다.
- 연구에 쓰는 이유: API가 주는 점수의 정의와 우리가 원하는 성공 확률을 구별합니다.

<a id="s11"></a>
## S11 Jev가 공개한 실패 사례

- 원문: [Jev 1.13 model jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
- 종류: 개발사가 공개한 모델 한계. 페이지 검토일 2026-10-02.
- 확인한 내용: 표현을 지나치게 문자 그대로 읽는 문제, 정확한 계산의 한계, 선택지 순서 영향, 입력 속 지시문에 영향받는 문제를 설명합니다.
- 한계: 특정 버전의 공급자 설명입니다. 우리 작업에서의 빈도는 측정하지 않았습니다.
- 연구에 쓰는 이유: 범용 모델의 일을 다른 모델로 옮겨도 새 실패가 생길 수 있음을 검토합니다.

<a id="s12"></a>
## S12 기억을 관리하는 판단을 분리한 사례

- 원문: [Jev-Mem](https://arxiv.org/html/2609.23986v1)
- 종류: arXiv 사전 공개 논문. v1, 2026-09-21. 동료 심사 완료 여부는 확인하지 못했습니다.
- 확인한 부분: 초록, 도입, 구조 설명.
- 확인한 내용: 무엇을 저장하고 연결할지, 무엇을 검색하고 언제 멈출지를 답변 생성과 나눠 다룹니다.
- 한계: 보고된 성능을 재현하지 않았습니다. 실험·부록 전체의 상세 검토는 남아 있습니다. 이 구조가 현재 저장소의 RAG에 적합하다고 결론 내리지 않습니다.
- 연구에 쓰는 이유: '기억'이라는 큰 기능 속의 선택들을 따로 살펴볼 사례입니다.

<a id="s13"></a>
## S13 Jev의 외부 평가

- 원문: [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/html/2609.37647v1)
- 종류: arXiv 사전 공개 논문. v1, 2026-09-29. 동료 심사 완료 여부는 확인하지 못했습니다.
- 확인한 부분: 초록, 평가 방식, 비용·지연과 한계 설명.
- 확인한 내용: 여러 분류 과제를 평가하며 출력 방식과 임계값에 따라 결과가 달라짐을 보고합니다.
- 한계: 비교 대상 일부는 추론형 대화 실행이 아니라 다음 토큰 확률을 사용합니다. 우리 작업이나 한국어의 우열을 입증하지 않습니다. 재현 실험은 수행하지 않았습니다.
- 연구에 쓰는 이유: 모델 이름뿐 아니라 비교한 실행 방식을 함께 기록합니다.

<a id="s14"></a>
## S14 확률과 실제 정답률을 맞추는 연구

- 원문: [On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html)
- 종류: ICML 논문. 2017년. 이번 조사에서는 초록과 서지 정보를 확인했습니다.
- 확인한 내용: 신경망의 확률이 실제 정답률과 어긋날 수 있으며, 사후 보정 방법을 평가합니다.
- 한계: 현재 LLM의 모든 판단에 그대로 적용되는 보장은 없습니다. 검증용 자료에서 보정한 뒤 분리된 자료로 평가해야 합니다.
- 연구에 쓰는 이유: 숫자로 자신감을 말한 것과 경험적으로 검증한 확률을 구별합니다.

<a id="s15"></a>
## S15 Claude Agent SDK의 Python 소스

- 원문: [고정한 커밋의 저장소](https://github.com/anthropics/claude-agent-sdk-python/tree/9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b)
- 종류: 공식 공개 소스. 저장소의 LICENSE는 MIT입니다. 번들 CLI까지 같은 라이선스라는 뜻은 아닙니다.
- 버전: SDK `0.2.163`, 선언된 번들 CLI `2.1.289`.
- 확인한 부분: `query.py`, `_internal/client.py`, `_internal/query.py`, `_internal/transport/subprocess_cli.py`, `types.py`, 관련 테스트 일부와 버전 파일.
- 확인한 내용: CLI 실행과 통신, 훅·권한 콜백 처리, 결과 형식을 추적했습니다. 모든 도구 호출이 권한 콜백을 거치는 것은 아닙니다.
- 후속 확인: [CLI 예비 실험](findings/2026-10-05-pilot.md)에서 권한 콜백을 건너뛰는 경로를 확인했습니다.
- 한계: SDK 자체의 테스트 스위트와 모델 간 성능 비교는 실행하지 않았습니다. 모델의 내부 판단 과정을 공개한 저장소로 취급하지 않습니다.
- 자세한 근거: [파일과 줄이 연결된 소스 분석](findings/2026-10-05-claude-sdk.md).

<a id="s16"></a>
## S16 OpenAI Agents SDK의 Python 소스

- 원문: [고정한 커밋의 저장소](https://github.com/openai/openai-agents-python/tree/d3304cff56f1be2325d00e0f172534d613697f88)
- 종류: 공식 공개 소스. 커밋 `d3304cff56f1be2325d00e0f172534d613697f88`로 고정했습니다.
- 확인한 부분: `run.py`, `agent.py`, `run_internal/run_loop.py`, `run_internal/turn_resolution.py`의 호출·입력·종료 경로입니다.
- 확인한 내용: 호출 전 입력 필터와 관찰 훅, FunctionTools 결과를 재호출 없이 반환하는 설정을 확인했습니다.
- 한계: SDK를 실행하거나 전체 소스를 읽지는 않았습니다. ChatGPT나 Codex의 내부 구현을 확인한 결과가 아닙니다.
- 자세한 근거: [입력 준비와 종료 경로 분석](findings/2026-10-05-openai-agents.md).

<a id="s17"></a>
## S17 에이전트 평가 방법

- 원문: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, 2026-01-09.
- 확인한 부분: 평가 구성, 연구 에이전트 평가, 문제와 채점 기준 작성, 실행 기록 검토.
- 확인한 내용: 실행 기록과 실제 결과를 구별합니다. 반복 평가와 사람이 기록을 검토할 필요를 설명합니다.
- 한계: 개발사의 경험 보고입니다. 우리 채점 기준을 검증해 주는 근거는 아닙니다.

<a id="s18"></a>
## S18 검색 실패를 단계별로 분석한 연구

- 원문: [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://arxiv.org/html/2608.01913v1), 2026년 사전 공개 논문.
- 확인한 부분: 연구 방법, 4.2~4.5의 근거 확보·활용·반복 검색 분석과 한계.
- 확인한 내용: 근거를 못 찾은 경우, 찾고도 활용하지 못한 경우, 도구 형식이 맞지 않은 경우를 구별합니다.
- 한계: 동료 심사 여부를 확인하지 못했습니다. 원본 실행을 재현하지 않았고 모든 부록을 읽지는 않았습니다. 정답 판정과 근거 집합의 한계가 있습니다.

<a id="s19"></a>
## S19 OpenAI 대화 상태

- 원문: [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state).
- 확인한 부분: 수동 기록, Responses API의 상태 관리, 응답 항목과 `phase` 보존 안내.
- 확인한 내용: 보이는 문장 외에도 다음 호출에 보존할 항목이 있습니다.
- 한계: 이 대화의 중단 원인이 해당 필드 때문이라는 증거는 없습니다.

<a id="s20"></a>
## S20 OpenAI 문맥 압축

- 원문: [Compaction](https://developers.openai.com/api/docs/guides/compaction).
- 확인한 부분: 서버 압축, 별도 compact 호출, 결과를 다음 요청에 전달하는 방법.
- 확인한 내용: 압축 결과에 사람이 해석할 수 없는 항목이 포함될 수 있습니다.
- 한계: 압축 전후의 과제 품질을 직접 비교하지 않았습니다. 원문이 언제나 완벽히 보존된다는 주장으로 사용하지 않습니다.

<a id="s21"></a>
## S21 Gemini의 현재 추론 상태 표현

- 원문: [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking).
- 확인한 부분: Interactions API의 thought 단계, signature와 summary, 스트리밍 형식.
- 확인한 내용: 추론 상태와 사람이 읽는 요약을 구별합니다. Legacy generateContent API와 구조가 다릅니다.
- 한계: 실제 API 호출은 하지 않았습니다. S06의 예전 API 설명과 섞지 않습니다.
- 조사 중 발견: 이전 thought-signatures URL은 새 Thinking 문서로 이동하라는 안내만 반환했습니다. 검색 결과의 예전 본문을 현재 문서로 취급하지 않았습니다.

<a id="s22"></a>
## S22 xAI의 서버·클라이언트 도구

- 원문: [Advanced Usage](https://docs.x.ai/developers/tools/advanced-usage).
- 확인한 부분: 두 종류의 도구를 함께 쓰는 방법과 `max_turns`의 범위.
- 확인한 내용: 클라이언트 도구 실행은 앱에 넘기며, 다음 요청에서는 서버 측 횟수 제한이 다시 시작합니다.
- 한계: Grok 앱 전체의 실행 정책은 확인하지 않았습니다.

<a id="s23"></a>
## S23 Meta Muse 서비스

- 원문: [Introducing Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/), 2026-09-08 발표, 페이지에 09-30도 표시됩니다.
- 확인한 부분: 작동 방식, VM과 브라우저, 권한과 작업 기록 설명.
- 확인한 내용: Muse Spark를 사용하는 개인 에이전트이며 별도 실행 환경을 갖는다고 설명합니다.
- 한계: 공급자 발표입니다. 서비스를 직접 사용하거나 보호 효과를 검증하지 않았습니다.

<a id="s24"></a>
## S24 Meta Muse의 실행 구조

- 원문: [How We Built Safety Into Muse](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse), 2026-09-08.
- 확인한 부분: 실행 영역, Sentinel, connector, 상태와 자격 증명을 나눈 구조.
- 확인한 내용: 행동 제안, 실행 허용, 실제 도구 실행을 서로 다른 책임으로 설명합니다.
- 한계: 공개 소스 분석이나 침투 시험을 수행한 결과가 아닙니다. 모든 우회를 막는다고 확정하지 않습니다.

<a id="s25"></a>
## S25 Muse Spark 모델과 서비스의 구별

- 원문: [Introducing Muse Spark 1.3](https://research.meta.ai/blog/introducing-muse-spark-1-3).
- 확인한 부분: 코딩, 사용 경로, 후속 계획.
- 확인한 내용: 모델의 개선을 설명하며 공개 가중치 배포를 후속 계획으로 언급합니다.
- 한계: 공급자의 효율 향상 수치를 재현하지 않았습니다. Llama와 Muse의 공개 범위를 동일하게 취급하지 않습니다.

<a id="s26"></a>
## S26 Claude Code의 비용과 보조 작업

- 원문: [Manage costs effectively](https://code.claude.com/docs/en/costs).
- 확인한 부분: 비용 집계 설명, Background token usage.
- 확인한 내용: 비용은 토큰으로 계산한 추정값이며 대화 요약 같은 보조 기능도 사용량을 발생시킬 수 있습니다.
- 한계: 이번 로그의 Haiku 호출이 특정 기능을 수행했다는 직접 증거는 아닙니다.

<a id="s27"></a>
## S27 Claude Code의 보조 모델 설정

- 원문: [Model configuration](https://code.claude.com/docs/en/model-config).
- 확인한 부분: 환경 변수 설명.
- 확인한 내용: `ANTHROPIC_DEFAULT_HAIKU_MODEL`이 haiku 선택과 일부 보조 기능에 쓰인다고 설명합니다.
- 한계: 환경 변수를 변경하거나 비공개 호출 내용을 읽지 않았습니다. 이번 호출의 용도는 확정하지 않습니다.

<a id="s28"></a>
## S28 플러그인에 포함할 수 있는 기능

- 원문: [OpenAI Package your plugin](https://developers.openai.com/plugins/build/plugins), [Claude Code Plugins overview](https://code.claude.com/docs/en/plugins), [OpenAI의 Claude 플러그인 제출 안내](https://developers.openai.com/plugins/guides/submit-claude-plugin).
- 확인일: 2026-10-05.
- 확인한 부분: 플러그인 구성, 스킬·MCP·훅 포함 방법, 기존 manifest 지원, 로컬 사용과 공개 제출의 차이.
- 확인한 내용: MCP는 플러그인에 포함할 수 있습니다. MCP 없이 스킬과 보조 스크립트를 제공할 수도 있습니다.
- 한계: 공개 제출 절차의 원격 서버 요구를 로컬 Codex 사용에 적용하지 않습니다. 새 패키지를 설치해 호환성을 시험하지 않았습니다.

<a id="s29"></a>
## S29 Claude Code와 Codex의 훅

- 원문: [Codex Hooks](https://developers.openai.com/codex/hooks), [Claude Code Hooks reference](https://code.claude.com/docs/en/hooks).
- 확인일: 2026-10-05.
- 확인한 부분: 명령 훅, `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`과 중단 처리, 반환값과 지원 차이. Codex의 압축 후 `SessionStart` 문맥 전달도 확인했습니다.
- 확인한 내용: 두 환경 모두 정상 응답 종료 때 계속 진행하도록 요청할 수 있습니다. Codex는 prompt·agent 훅을 실행하지 않으며, 도구 출력 교체 계약도 Claude와 다릅니다.
- 한계: 훅이 프로세스 종료 뒤 스스로 세션을 재시작한다는 보장은 없습니다. 설치된 각 버전에서 모든 계약을 통합 시험하지 않았습니다.

<a id="s30"></a>
## S30 로컬 MCP와 원격 MCP

- 원문: [Codex MCP](https://developers.openai.com/codex/mcp), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [MCP Architecture overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture).
- 확인일: 2026-10-05. MCP 구조 설명은 URL에 표시된 `2026-07-28` 버전을 읽었습니다.
- 확인한 부분: 로컬 stdio, 원격 Streamable HTTP, 플러그인에 포함한 서버와 클라이언트의 역할.
- 확인한 내용: 두 호스트에서 로컬 프로세스로 도구를 제공할 수 있습니다. MCP 사용 자체가 클라우드 배포를 요구하지 않습니다.
- 한계: 같은 서버 코드를 써도 저장 경로·동시 접근·프로세스 수명은 따로 설계해야 합니다. MCP가 판단의 정확도나 복구를 보장하지는 않습니다.

<a id="s31"></a>
## S31 긴 작업을 여러 세션에서 이어가는 실행 환경

- 원문: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Anthropic, 2025-11-26.
- 확인일: 2026-10-05.
- 확인한 부분: 초기 환경 구성, 기능 목록, 진행 기록, Git 이력과 새 세션 시작 때의 검증.
- 확인한 내용: Anthropic은 대화 압축만으로 긴 개발 작업을 안정적으로 이어가기 어려웠다고 보고합니다. 다음 세션이 진행 기록과 이력을 읽고, 현재 동작도 검사하도록 구성한 사례를 설명합니다.
- 연구에서의 해석: 인계 기록을 읽는 일과 현재 상태를 확인하는 일을 구별해야 합니다. 기록이 짧다는 사실만으로 다음 행동의 근거가 충분해지지 않습니다.
- 한계: 공급자의 웹 앱 개발 사례입니다. 우리 Stage나 현재 Claude·Codex의 일반적인 성능을 입증하지 않습니다. 이 문서의 구현 예시를 그대로 제품 규칙으로 채택하지 않습니다.

## 추가 자료를 읽을 때 기록할 것

- 제목, 작성 주체, URL, 게시일, 확인일, 버전과 읽은 절을 적습니다.
- 출처가 입증하는 주장과 입증하지 못하는 주장을 각각 적습니다.
- 성능 수치는 과제, 데이터, 비교 방식, 반복 횟수와 함께 가져옵니다.
- 초록만 읽었다면 그대로 적습니다. 전문을 검토했다고 표시하지 않습니다.
- 새 자료가 기존 결론과 충돌하면 [가설](hypotheses.md)과 [진행 기록](progress.md)에 반영합니다.
