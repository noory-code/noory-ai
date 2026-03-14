# Opacity

## M3 링크

| 페이지 | URL |
|--------|-----|
| Interaction States | https://m3.material.io/foundations/interaction/states/overview |
| State Layers | https://m3.material.io/foundations/interaction/states/state-layers |

## 토큰 정의 (M3 State Layer Opacity)

| 토큰 | 값 | M3 State | 설명 |
|------|-----|---------|------|
| $opacity/disabled | 0.38 | Disabled | 비활성 상태 (콘텐츠에 적용) |
| $opacity/hover | 0.08 | Hovered | 마우스 오버 State Layer |
| $opacity/focus | 0.12 | Focused | 포커스 State Layer |
| $opacity/pressed | 0.12 | Pressed | 터치/클릭 State Layer |
| $opacity/dragged | 0.16 | Dragged | 드래그 State Layer |

> State Layer: 컴포넌트 위에 색상(On-Surface 또는 Primary)을 특정 불투명도로 오버레이하여 상태를 표현.

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Opacity Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/foundations/interaction/states/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다:

| 변수명 | 값 |
|--------|-----|
| $opacity/disabled | 0.38 |
| $opacity/hover | 0.08 |
| $opacity/focus | 0.12 |
| $opacity/pressed | 0.12 |
| $opacity/dragged | 0.16 |

---

## 프레임 설정
- 이름: "Opacity Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Opacity"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · State Layer Opacity"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/foundations/interaction/states/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · disabled (0.38) — 비활성화된 컴포넌트의 콘텐츠(텍스트, 아이콘) 투명도
  · hover (0.08) — 마우스가 위에 있을 때 State Layer 색상
  · focus (0.12) — 키보드/접근성 포커스 시 State Layer 색상
  · pressed (0.12) — 터치 또는 클릭 시 State Layer 색상
  · dragged (0.16) — 드래그 인터랙션 시 State Layer 색상

---

## 섹션 3 — State Layer 시각화
- 소제목: "State Layer Visualization"  (20px, 600)
- 설명: "State Layer = On-Surface(또는 Primary) 색상을 특정 opacity로 컴포넌트 위에 오버레이"  (14px, On-Surface-Variant)
- 5개 카드 가로 나열, gap 16px, 카드 크기 120×80dp:

  각 카드 구조:
  - 배경 (bottom): Surface Container (80dp 전체)
  - State Layer (top): On-Surface 색상, 해당 opacity
  - 중앙 텍스트: 상태명  (14px, bold, On-Surface)
  - 하단 텍스트: opacity 값  (12px, Primary)

  · Disabled — opacity 0.38
  · Hover — opacity 0.08
  · Focus — opacity 0.12
  · Pressed — opacity 0.12
  · Dragged — opacity 0.16

---

## 섹션 4 — Disabled State 특별 규칙
- 소제목: "Disabled State"  (20px, 600)
- 설명 박스 (background: Error Container, radius 12dp, padding 16dp):
  "Disabled는 State Layer가 아닙니다.
  컨테이너: On-Surface × 0.12 (배경)
  콘텐츠 (텍스트, 아이콘): On-Surface × 0.38 ($opacity/disabled)
  → 항상 두 레이어 모두 적용해야 M3 스펙에 맞습니다."

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 토큰 | 값 | State | State Layer 색상 |
  |------|-----|-------|----------------|
  | $opacity/disabled | 0.38 | Disabled | — (콘텐츠에 직접 적용) |
  | $opacity/hover | 0.08 | Hovered | On-Surface 또는 Primary |
  | $opacity/focus | 0.12 | Focused | On-Surface 또는 Primary |
  | $opacity/pressed | 0.12 | Pressed | On-Surface 또는 Primary |
  | $opacity/dragged | 0.16 | Dragged | On-Surface 또는 Primary |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppOpacity 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // Disabled content
  Opacity(
    opacity: AppOpacity.disabled, // 0.38
    child: Text('Disabled Label'),
  )

  // State Layer (M3 방식)
  final cs = Theme.of(context).colorScheme;
  ButtonStyle(
    overlayColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.hovered))
        return cs.onSurface.withValues(alpha: AppOpacity.hover);    // 0.08
      if (states.contains(WidgetState.focused))
        return cs.onSurface.withValues(alpha: AppOpacity.focus);    // 0.12
      if (states.contains(WidgetState.pressed))
        return cs.onSurface.withValues(alpha: AppOpacity.pressed);  // 0.12
      return null;
    }),
  )

  // InkWell custom splash
  InkWell(
    splashColor: cs.primary.withValues(alpha: AppOpacity.pressed),  // 0.12
    hoverColor:  cs.primary.withValues(alpha: AppOpacity.hover),    // 0.08
    focusColor:  cs.primary.withValues(alpha: AppOpacity.focus),    // 0.12
    child: ...,
  )
