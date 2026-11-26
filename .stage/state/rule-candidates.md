---
through: R-00000421
---
# Rule candidates

회고의 `## Rule candidate` 를 한 목록으로 묶은 것이다. 형식과 올리는 기준은 설치된 Stage 플러그인의
`skills/stage-retrospective/rule-promotion.md` ("Consolidating candidates")가 소유한다. 두 번 이상 본
`proposed: promote` 줄은 사용자에게 묻지 않고 규칙이 되고, 한 번 본 `proposed: promote` 줄은 사용자가 판정한다
(DE-00000104). 규칙 파일이 이미 말하는 후보는 여기에 없다.

- **기록의 자리나 배치를 바꾸는 변경은 그 자리를 읽는 코드와 화면의 테스트부터 센다.** (seen 2: R-00000241, R-00000373) — proposed: promote
- **사용자에게 묻거나 토론할 때는 질문 하나에 답 하나(표 하나)만 두고, 큰 그림부터 말한다.** (seen 2: R-00000371, R-00000402; O-00000061 도 적었다) — proposed: promote
- **acceptance 명령에 한 사람의 기기 경로를 저장하지 않고 저장소 기준 상대 경로만 쓴다.** (seen 2: R-00000282; R-00000282 states its second occurrence) — proposed: promote
- **숫자에서 개선 제안을 낼 때 그 자리를 지금 모양으로 만든 커밋이나 주석을 먼저 읽는다.** (seen 2: R-00000334; R-00000334 states its second occurrence) — proposed: promote
- **리뷰어에게 허용하는 규칙을 바꾸면 실제 `claude` 로 허용되는 경우와 거절되는 경우를 모두 실행해 본다.** (seen 2: R-00000374; R-00000374 states its second occurrence) — proposed: promote
- **절차를 바꾸거나 다른 세션이 따를 새 길을 적은 카드는 그 길로 실제 일을 한 번 해 본 뒤에 닫는다.** (seen 3: R-00000404, R-00000418, R-00000420. O-00000061 도 적었다) — proposed: promote
- **병렬 실행의 출력을 `tail -N` 같은 것으로 자르지 않는다.** (seen 1: R-00000246; caught by a person: 감독이 결과를 찾다 알아챘다) — proposed: promote
- **관측에 "통과했다"를 적을 때는 막힌 쪽과 같은 무게로 증거를 남긴다.** (seen 1: R-00000247) — proposed: hold
- **알림이나 오류 문구를 새로 지을 때 그 말이 이미 다른 뜻으로 쓰이고 있는지 본다.** (seen 1: R-00000255; caught by the close reviewer) — proposed: hold
- **카드에 "이것이 첫 판단이다"라고 쓰기 전에 그 질문을 이미 소유한 문서가 있는지 연다.** (seen 1: R-00000258) — proposed: hold
- **대신 쓰는 경로를 고를 때는 바뀌기 전 경로가 다루던 경우를 모두 실측한다.** (seen 1: R-00000326; caught by the close reviewer) — proposed: hold
- **결정을 정하는 카드는 닫을 때 그 결정을 지금 올릴지 나중에 올릴지 정하고, 나중이면 이유를 Follow-up 에 적는다.** (seen 1: R-00000337. 회고는 같은 날 한 번에 찾은 다섯 건을 센다) — proposed: hold
- **텍스트를 출력하는 Stage 스크립트는 `main()` 에서 stdout 을 UTF-8 로 맞춘다.** (seen 1: R-00000393; caught by CI) — proposed: hold
- **출력 디코딩을 바꾸기 전에 `test_subprocess_text_encoding.py` 가 지키는 계약을 읽고 그 시험을 먼저 돌린다.** (seen 1: R-00000394; caught by CI. O-00000061 도 적었다) — proposed: hold
- **함수를 다른 파일로 옮기기 전에 시험이 그 이름을 가로채는 자리를 센다.** (seen 1: R-00000243) — proposed: hold
- **셸을 거치는 문자열에 백틱을 쓰지 않는다.** (seen 1: R-00000251) — proposed: hold
- **돌릴 수 없는 검사는 지침에 적지 않고 셀 수 있는 것을 준다.** (seen 1: R-00000261) — proposed: hold
- **플러그인 계약을 바꿀 때는 그 계약을 읽는 스크립트까지 센다.** (seen 1: R-00000266) — proposed: hold
- **카드 기준을 넓힐 때는 넓힌 종류마다 그 문제가 실제로 일어나는지 먼저 재현한다.** (seen 1: R-00000268) — proposed: hold
- **스토리가 채우는 에픽의 성공 기준을 하나도 가리킬 수 없으면 최상위 스토리로 등록한다.** (seen 1: R-00000272) — proposed: hold
- **같은 모양의 예외 결정이 세 번 이상 쌓이면 정책 후보로 올린다.** (seen 1: R-00000292) — proposed: hold
- **닫기·등록 같은 쓰기 도구가 받아들이는 값은 감사가 받아들이는 값과 같은 함수로 판정한다.** (seen 1: R-00000294) — proposed: hold
- **권한을 실험할 때는 규칙을 하나씩 주어 어느 규칙이 허락하는지 가른다.** (seen 1: R-00000296) — proposed: hold
- **상태를 되돌리는 검사는 판정 사슬의 단락 평가 밖에서 항상 돌린다.** (seen 1: R-00000300; caught by the close reviewer) — proposed: hold
- **쓰기 도구 몫의 칸은 다른 행위자가 바꾸면 문장으로 막지 않고 거절하고 되돌린다.** (seen 1: R-00000300) — proposed: hold
- **결정 레코드를 근거로 삼을 때는 그 레코드의 Follow-up 을 닫은 카드까지 읽는다.** (seen 1: R-00000323) — proposed: hold
- **Stage 의 게이트나 번호 할당 동작을 근거로 위험을 말하기 전에 해당 스크립트를 먼저 읽는다.** (seen 1: R-00000325) — proposed: hold
- **카드를 닫기 전에 브랜치에 main 을 합쳐 충돌이 없는지 확인한다.** (seen 1: R-00000360) — proposed: hold
- **무엇을 줄일지 정하기 전에 어디서 생기는지 먼저 센다.** (seen 1: R-00000363) — proposed: hold
- **기록의 상태를 바꾼 뒤에는 그 상태를 읽는 쪽의 출력을 한 번 직접 본다.** (seen 1: R-00000365) — proposed: hold
- **구조를 설명하는 문장을 쓰기 전에 그 구조를 코드에서 세어 본다.** (seen 1: R-00000366) — proposed: hold
- **충돌이나 오류의 개수를 줄이는 안은 줄어든 개수만 보지 않고 결과가 맞는지를 사람이 만든 결과와 비교한다.** (seen 1: R-00000367) — proposed: hold
- **양식을 고치면 프로젝트의 양식 사본도 `refresh_guidance.py` 로 맞춘다.** (seen 1: R-00000370) — proposed: hold
- **클라우드 하위 세션은 원격 브랜치를 만들기 전에 지울 수 있는지 확인하거나 원격에 남는 일을 메인 세션에 맡긴다.** (seen 1: R-00000377) — proposed: hold
- **성능 카드의 성공 기준에는 측정한 노이즈 폭을 함께 적는다.** (seen 1: R-00000380) — proposed: hold
- **세션이나 실행기에 일을 넘기기 전에 `stage-handoff` 의 위임 계약을 읽는다.** (seen 1: R-00000385) — proposed: hold
- **번호를 고르는 규칙을 바꿀 때는 번호를 고르는 모든 자리를 센다.** (seen 1: R-00000398) — proposed: hold
- **장치를 빼 보는 카드는 시작 전에 하중을 볼 기록이 커밋돼 있는지와 뺀 뒤 그 장치를 지날 일이 있는지 확인한다.** (seen 1: R-00000403) — proposed: hold
