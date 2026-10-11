# 서비스마다 어디까지 확인할 수 있었나요

확인일은 2026-10-05입니다. 사용자께서 '뮤즈'는 메타라고 확인해 주셨습니다.
아래 표는 공개된 동작과 관찰 범위를 비교합니다. 성능 순위는 아닙니다.
실제 실험과 개선 대상은 사용자가 정한 [Claude와 Codex](purpose.md#available-ai)입니다.
다른 서비스의 자료는 설계를 참고할 근거로 남깁니다.
OpenAI Agents SDK 분석은 Codex 제품을 분석하거나 실행한 결과가 아닙니다.

| 대상 | 이번에 확인한 구조 | 확인하지 못한 부분 | 우리가 바꿔 볼 수 있는 것 |
|---|---|---|---|
| OpenAI | Agents SDK가 입력·도구·종료를 처리합니다. Responses API는 대화 상태와 압축한 문맥을 이어갈 수 있습니다. | ChatGPT와 Codex 제품 전체의 내부 흐름, 서버 내부 처리 | 직접 만든 앱의 입력 구성, 도구, 종료 규칙, 기록 |
| Anthropic | Python Agent SDK가 CLI와 통신합니다. 도구 전후 훅과 권한 콜백을 실제 실행했습니다. | CLI의 모든 내부 호출, 사용량에 나타난 Haiku의 역할 | 지침, 도구 전후 관찰, 입력 수정, 작업 결과 검사 |
| Google | Gemini Interactions API는 추론 상태를 잇는 signature와 사람이 읽는 summary를 구별합니다. | Gemini 소비자 앱 전체 구조, 암호화된 상태 내부 | API 버전에 맞춘 대화 보존, 도구 반환, 문맥 관리 |
| xAI | 서버 도구는 제공자가 실행합니다. 클라이언트 도구는 앱이 실행하고 결과를 돌려줍니다. | Grok 소비자 앱 전체 구조, 서버 도구 내부 | 앱의 도구 실행, 작업 전체 한도, 결과 확인 |
| Meta | Muse는 VM과 브라우저에서 행동합니다. Muse의 행동 제안과 별도 Sentinel의 허용 판단을 나눕니다. | 내부 모델 배치와 전체 소스, 발표한 보호 장치의 실제 효과 | 직접 만드는 시스템에서 제안·허용·실행을 나누고 목적과 상태를 남기는 설계 |

OpenAI 근거: [SDK 분석](findings/2026-10-05-openai-agents.md), [대화 상태](https://developers.openai.com/api/docs/guides/conversation-state), [Compaction](https://developers.openai.com/api/docs/guides/compaction).
Anthropic 근거: [SDK 분석](findings/2026-10-05-claude-sdk.md), [실제 기록](findings/2026-10-05-pilot.md).
Google 근거: [Thinking](https://ai.google.dev/gemini-api/docs/thinking).
xAI 근거: [서버·클라이언트 도구 혼합](https://docs.x.ai/developers/tools/advanced-usage).
Meta 근거: [Muse 소개](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/), [구조 설명](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse).

## 문장만 보존하면 충분하지 않을 수 있습니다

OpenAI의 대화 상태 문서는 응답 항목과 `phase`를 보존하도록 안내합니다.
문맥 압축 결과에는 사람이 읽을 수 없는 항목도 들어갈 수 있습니다.
Google도 추론 상태와 그 요약을 다른 필드로 제공합니다.
따라서 화면에 보이는 문장만 저장하면 원래 API가 요구한 상태를 잃을 수 있습니다.
이는 해당 API 계약에서 이끌어 낸 해석입니다. 우리 대화가 멈춘 원인을 입증하지는 않습니다.

## 도구 한도를 작업 전체 한도로 오해하지 않아야 합니다

xAI 문서에서 `max_turns`는 한 요청 안의 서버 실행을 제한합니다.
클라이언트 도구를 처리한 뒤 새 요청을 보내면 횟수가 다시 시작합니다.
따라서 앱에서 작업 전체의 시간과 호출 수를 관리해야 하는지 따로 확인해야 합니다.
이 동작을 다른 회사의 같은 이름 옵션에도 적용하면 안 됩니다.

## 메타에서 배울 지점

Meta의 설명에서 Muse는 행동을 제안하고 Sentinel은 허용 여부를 정합니다.
상태 보관과 자격 증명도 실행 영역 밖에서 관리한다고 설명합니다.
여기서 얻는 연구 질문은 '누가 더 똑똑한가'보다 구체적입니다.
**판단 하나를 여러 책임으로 나누면 어떤 오류를 각각 막을 수 있을까요?**
다만 이는 공급자가 설명한 설계입니다. 직접 실행해 효과를 확인하지는 않았습니다.

Muse 서비스와 Muse Spark 모델을 구별해야 합니다.
[Muse Spark 1.3 발표](https://research.meta.ai/blog/introducing-muse-spark-1-3)는 모델 개선과 도구 사용량 감소를 주장합니다.
그 성능 수치를 우리 실험의 예상 이익으로 사용하지 않습니다.
같은 글이 공개 가중치를 후속 계획으로 설명한다고 해서 Llama의 공개 범위를 Muse에 그대로 적용할 수도 없습니다.

## 공통으로 얻은 결론

다섯 회사 모두 같은 내부 구조라고 입증한 것은 아닙니다.
하지만 조사한 자료에는 모델 바깥에서 문맥을 보존하고, 도구를 실행하고, 계속할지 결정하는 절차가 나타납니다.
이 절차는 모델을 학습시키지 않고도 연구할 수 있는 범위입니다.
