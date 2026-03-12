---
name: change-logo
description: >
  Replace the app logo in the design guide .pen file.
  Triggers when the user asks to change, replace, or update the logo,
  app icon, or brand mark in the Pencil design guide.
user-invocable: true
allowed-tools:
  - mcp__pencil__get_editor_state
  - mcp__pencil__batch_get
  - mcp__pencil__batch_design
  - mcp__pencil__get_screenshot
---

# Change Logo

디자인 가이드의 로고 컴포넌트를 교체한다.

## 로고 규격

- **형태**: 정사각형 (권장 192×192)
- **배경**: 투명 또는 앱 Primary 컬러
- **배치**: `Logo` 이름의 reusable 컴포넌트 — 모든 인스턴스가 동시 업데이트됨

## Step 1 — 현재 파일 확인

```
mcp__pencil__get_editor_state()
```

현재 열린 `.pen` 파일이 앱 디자인 가이드인지 확인한다.
`material-design-guide.lib.pen`이면 사용자에게 앱 전용 파일을 열도록 안내한다.

## Step 2 — 로고 소스 결정

사용자에게 확인:

- **이미지 파일 경로 제공** → 해당 이미지를 fill로 적용
- **AI 생성 요청** → 앱 이름 기반으로 AI 로고 생성
- **텍스트/이니셜만** → 텍스트 기반 로고 생성

## Step 3 — 로고 노드 탐색

```
mcp__pencil__batch_get(patterns=["Logo"])
```

`Logo` 이름의 reusable 컴포넌트 노드 ID를 찾는다.

- 노드가 없으면: `mcp__pencil__batch_design`으로 192×192 reusable 프레임 `Logo` 신규 생성
- 노드가 있으면: 해당 노드 ID 사용

## Step 4 — 로고 교체

### Case A: AI 생성

```
G(<logoNodeId>, "ai", "<appname> app logo square minimal")
```

### Case B: 이미지 파일

```
mcp__pencil__batch_design
U(<logoNodeId>, { fill: { type: "image", url: "<file_path>" } })
```

### Case C: 텍스트 이니셜

```
mcp__pencil__batch_design
bg=I(<logoNodeId>, { type: "frame", width: "fill_container", height: "fill_container", fill: "$primary" })
label=I(<logoNodeId>, { type: "text", content: "<initials>", fontSize: 72, fill: "$onPrimary", textAlign: "center" })
```

## Step 5 — 결과 확인

```
mcp__pencil__get_screenshot(<logoNodeId>)
```

스크린샷으로 결과를 확인하고 사용자에게 보여준다.
만족스럽지 않으면 Step 4로 돌아가 재시도한다.
