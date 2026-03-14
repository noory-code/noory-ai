# M3 Expressive Guide — Context 노드 내용

이 파일은 `material-design-guide.lib.pen`의 **"M3 Expressive Guide"** 프레임 안에
`context` 타입 노드로 삽입될 내용이다.

이 파일을 import한 `.pen` 파일에서 디자인할 때, AI는 이 Context를 자동으로 참조한다.

---

## Context 노드에 들어갈 텍스트

```
# M3 Expressive Design Guide

이 라이브러리를 import해서 디자인할 때 아래 규칙을 반드시 따르세요.
/pencil-material:design-guide 스킬을 사용하면 이 가이드가 자동으로 적용됩니다.

## 핵심 원칙

### 색상
- 항상 Color Role 변수 사용: $primary, $onPrimary, $surface, $onSurface, $primaryContainer 등
- 절대 색상 하드코딩 금지 (#6750A4 등)
- 라이트/다크 테마 모두 자동 대응됨

### 버튼 계층 (화면당 Filled는 1개만)
1. Filled → 가장 중요한 주요 액션 1개
2. FilledTonal → 보조 액션
3. Elevated → 평면 레이아웃에서 구분 필요할 때
4. Outlined → 중간 강조 액션
5. Text → 가장 낮은 강조, 보조/인라인

### FAB
- 화면당 1개만
- 가장 중요한 단일 액션에만 사용
- Extended FAB: 레이블이 필요할 때

### 내비게이션
- Mobile 2~5 destinations → NavigationBar (하단 고정)
- Tablet/Desktop → NavigationRail (좌측)
- 5개 이상 destinations → NavigationDrawer

### TextField
- 기본: Filled (대부분의 상황)
- Outlined: 복잡한 배경 위에서만

### Cards
- Elevated: 평면 surface 위
- Filled: 미묘한 그룹핑
- Outlined: 복잡한 배경 위

### 컴포넌트 ID 참조
이 라이브러리의 컴포넌트를 ref로 사용할 때:
- Frame/Mobile/390: dnJUo
- TopAppBar/Small: Mv3K9
- NavigationBar/3Items: ItYES
- FAB/Default: 9XN45
- Buttons/Filled/Rounded/lg: SgybC
- TextFields/Filled/Empty: 1gP7O
- Lists/TwoLineItem: X6KcN
- Switch/On: 4cwpx
전체 목록: /pencil-material:design-guide 스킬 참조
```

---

## Pencil batch_design 삽입 코드

`M3 Expressive Guide` 프레임(ID: `xrgHM`)에 Context 노드를 추가하는 operations:

```javascript
guideContext=I("xrgHM", {
  type: "context",
  width: 800,
  height: 400,
  content: "# M3 Expressive Design Guide\n\n이 라이브러리를 import해서 디자인할 때 아래 규칙을 반드시 따르세요.\n/pencil-material:design-guide 스킬을 사용하면 이 가이드가 자동으로 적용됩니다.\n\n## 핵심 원칙\n\n### 색상\n- 항상 Color Role 변수 사용: $primary, $onPrimary, $surface, $onSurface 등\n- 절대 색상 하드코딩 금지\n\n### 버튼 계층 (화면당 Filled는 1개만)\n1. Filled → 주요 액션 1개\n2. FilledTonal → 보조 액션\n3. Elevated → 평면 레이아웃 구분\n4. Outlined → 중간 강조\n5. Text → 최저 강조\n\n### FAB\n- 화면당 1개만, 가장 중요한 단일 액션\n\n### 내비게이션\n- Mobile 2~5개: NavigationBar (하단 고정)\n- Tablet/Desktop: NavigationRail\n- 5개 이상: NavigationDrawer\n\n### 컴포넌트 ID\n- Frame/Mobile/390: dnJUo\n- TopAppBar/Small: Mv3K9\n- NavigationBar/3Items: ItYES\n- FAB/Default: 9XN45\n- Buttons/Filled/Rounded/lg: SgybC\n- TextFields/Filled/Empty: 1gP7O\n전체 목록: /pencil-material:design-guide 스킬 참조"
})
```
