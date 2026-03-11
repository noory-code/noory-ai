# Spacing

## M3 링크

| 페이지 | URL |
|--------|-----|
| Layout | https://m3.material.io/foundations/layout/understanding-layout/overview |
| Spacing | https://m3.material.io/foundations/layout/applying-layout/compact |

## 토큰 정의

| 토큰 | 값 | 용도 |
|------|-----|------|
| $spacing/0 | 0 dp | 간격 없음 |
| $spacing/xs | 2 dp | 아이콘 내부 패딩, 칩 내부 최소 간격 |
| $spacing/sm | 4 dp | 아이콘 gap, 칩 내부 |
| $spacing/md | 8 dp | 리스트 아이템 간격, 아이콘 gap |
| $spacing/base | 12 dp | 기본 패딩, 카드 내부 패딩 |
| $spacing/lg | 16 dp | 콘텐츠 여백, 섹션 내 간격 |
| $spacing/xl | 20 dp | 버튼 수평 패딩 |
| $spacing/2xl | 24 dp | 카드 패딩, 섹션 간격 |
| $spacing/3xl | 32 dp | 섹션 간 간격 |
| $spacing/4xl | 40 dp | 페이지 좌우 패딩, 섹션 헤더 간격 |

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Spacing Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/foundations/layout/understanding-layout/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다. 이미 등록되어 있다면 값을 확인하고 아래와 다르면 수정한다:

| 변수명 | 값 |
|--------|-----|
| $spacing/0 | 0 |
| $spacing/xs | 2 |
| $spacing/sm | 4 |
| $spacing/md | 8 |
| $spacing/base | 12 |
| $spacing/lg | 16 |
| $spacing/xl | 20 |
| $spacing/2xl | 24 |
| $spacing/3xl | 32 |
| $spacing/4xl | 40 |

---

## 프레임 설정
- 이름: "Spacing Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Spacing"  (32px, bold, On-Surface)
- 부제목: "Design Token · Spacing Scale"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/foundations/layout"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 0 (0dp) — 간격 없음
  · xs (2dp) — 아이콘 내부 패딩, 칩 내부 최소 간격
  · sm (4dp) — 아이콘 gap, 칩 내부
  · md (8dp) — 리스트 아이템 간격, 아이콘 gap
  · base (12dp) — 기본 패딩, 카드 내부 패딩
  · lg (16dp) — 콘텐츠 여백, 섹션 내 간격
  · xl (20dp) — 버튼 수평 패딩
  · 2xl (24dp) — 카드 패딩, 섹션 간격
  · 3xl (32dp) — 섹션 간 간격
  · 4xl (40dp) — 페이지 좌우 패딩, 섹션 헤더 간격

---

## 섹션 3 — Token Scale
- 소제목: "Token Scale"  (20px, 600)
- 10개 토큰을 수직 나열, 각 행:

  [토큰명 레이블 120px] [시각 바 (너비=값×4px, 높이 24px, bg=Primary, opacity 0.8)] [값 텍스트]

  · $spacing/0    → 0dp   → 바 없음 (점선 표시)
  · $spacing/xs   → 2dp   → 바 너비 8px
  · $spacing/sm   → 4dp   → 바 너비 16px
  · $spacing/md   → 8dp   → 바 너비 32px
  · $spacing/base → 12dp  → 바 너비 48px
  · $spacing/lg   → 16dp  → 바 너비 64px
  · $spacing/xl   → 20dp  → 바 너비 80px
  · $spacing/2xl  → 24dp  → 바 너비 96px
  · $spacing/3xl  → 32dp  → 바 너비 128px
  · $spacing/4xl  → 40dp  → 바 너비 160px

---

## 섹션 4 — Usage Examples
- 소제목: "Usage Examples"  (20px, 600)
- 3개 예시 카드 가로 배치, gap 24px:

  ┌─ 버튼 수평 패딩 ─────────┐
  │  [← 20dp →][Label][← 20dp →]  │
  │  $spacing/xl = 20dp      │
  └──────────────────────────┘

  ┌─ 리스트 아이템 간격 ──────┐
  │  아이콘 [8dp gap] 텍스트  │
  │  $spacing/md = 8dp        │
  └──────────────────────────┘

  ┌─ 페이지 여백 ────────────┐
  │  [← 40dp →] 콘텐츠       │
  │  $spacing/4xl = 40dp     │
  └──────────────────────────┘

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 토큰 | 값 | 주요 용도 |
  |------|-----|----------|
  | $spacing/0 | 0 dp | 간격 없음 |
  | $spacing/xs | 2 dp | 아이콘 내부, 칩 최소 |
  | $spacing/sm | 4 dp | 아이콘 gap, 칩 내부 |
  | $spacing/md | 8 dp | 아이템 간격, 아이콘 gap |
  | $spacing/base | 12 dp | 기본 패딩 |
  | $spacing/lg | 16 dp | 콘텐츠 여백 |
  | $spacing/xl | 20 dp | 버튼 패딩 |
  | $spacing/2xl | 24 dp | 카드 패딩 |
  | $spacing/3xl | 32 dp | 섹션 간격 |
  | $spacing/4xl | 40 dp | 페이지 여백 |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppSpacing 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // EdgeInsets
  padding: EdgeInsets.all(AppSpacing.base)                               // 12dp
  padding: EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.base) // 20, 12dp

  // SizedBox gaps
  SizedBox(height: AppSpacing.md)    // 8dp — 리스트 아이템 간격
  SizedBox(height: AppSpacing.lg)    // 16dp — 콘텐츠 여백
  SizedBox(height: AppSpacing.x4l)   // 40dp — 페이지 여백

  // Gap (flutter_gap 패키지)
  Gap(AppSpacing.sm)    // 4dp
  Gap(AppSpacing.base)  // 12dp
  Gap(AppSpacing.x2l)   // 24dp

  // 컬러와 함께 사용
  Container(
    padding: EdgeInsets.all(AppSpacing.base),
    color: Theme.of(context).colorScheme.surfaceContainerHighest,
  )
