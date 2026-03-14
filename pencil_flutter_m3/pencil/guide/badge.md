# Badge

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/badges/overview |
| Guidelines | https://m3.material.io/components/badges/guidelines |
| Specs | https://m3.material.io/components/badges/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Small (dot) | `Badge` |
| Large (label) | `Badge(label: Text('3'))` |

## 언제 사용하나요?

- 아이콘 또는 네비게이션 아이템에 알림 수·상태를 표시할 때
- 읽지 않은 메시지, 장바구니 수량 등 1~4자 숫자를 나타낼 때
- 버튼이나 아이콘에 주의를 끌어야 할 때 (dot 배지)

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | NavigationBar 아이템에 Badge 사용 |
| Tablet (medium) | NavigationRail 아이템에 Badge 사용 |
| Desktop/Web (expanded) | NavigationDrawer 아이템에 Badge 사용 |

> Badge 자체는 크기 변화 없음. 부착되는 네비게이션 컴포넌트가 화면 크기에 따라 달라짐.

## Variants

- **Small** — 레이블 없는 점(dot), 단순 존재 여부 표시
- **Large** — 숫자/텍스트 레이블 포함

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Badge Guide" 프레임을 만들어주세요.
모든 내용은 이 "Badge Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/badges/overview

---

## 프레임 설정
- 이름: "Badge Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Badge"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · badges"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/badges/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 아이콘 또는 네비게이션 아이템에 알림 수·상태를 표시할 때
  · 읽지 않은 메시지, 장바구니 수량 등 1~4자 숫자를 나타낼 때
  · 버튼이나 아이콘에 주의를 끌어야 할 때 (dot 배지)

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Small (Dot) ──────────────────────┐
  │  회색 아이콘(24×24dp) 우상단에      │
  │  지름 6dp 원형 도트 배치            │
  │  도트 색상: Error (Error)         │
  │  아이콘 배경: 투명                  │
  │  레이블: "Small · dot only"        │
  └────────────────────────────────────┘

  ┌─ Large (Label) ────────────────────┐
  │  회색 아이콘(24×24dp) 우상단에      │
  │  pill 모양 배지 배치 (height 16dp)  │
  │  배지 배경: Error (Error)         │
  │  텍스트: "3"  (11sp, white, center) │
  │  가로 패딩: 4dp, corner radius 8dp  │
  │  레이블: "Large · with number"     │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Large Badge를 크게 그리고 번호 레이블 연결:
  1. Container — pill shape, Error, height 16dp, corner 8dp
  2. Label text — "3", 11sp, Surface, center
  3. Host icon — 아이콘 위에 우상단 offset 배치 (-4dp, -4dp)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | Small    | Large        |
  |------------------|----------|--------------|
  | Size (dot)       | 6×6 dp   | —            |
  | Height           | —        | 16 dp        |
  | Min width        | —        | 16 dp        |
  | Corner radius    | 3 dp     | 8 dp         |
  | Label font       | —        | 11sp         |
  | Horizontal pad   | —        | 4 dp         |
  | Color (bg)       | Error    | Error        |
  | Color (label)    | —        | On-Error     |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ──────────┐
  │  NavigationBar 아이콘에 Badge │
  │  → NavigationBar + Badge    │
  └──────────────────────────────┘

  ┌─ Tablet / medium ───────────┐
  │  NavigationRail 아이콘에 Badge│
  │  → NavigationRail + Badge   │
  └──────────────────────────────┘

  ┌─ Desktop / expanded ────────┐
  │  NavigationDrawer 아이템에   │
  │  → NavigationDrawer + Badge │
  └──────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Badge Guide" 프레임 안에 아래 2개를 그리고, 각각 리유저블 컴포넌트로 등록한다
- 가로 나란히 배치, gap 24px

  Badge/Small:
  · 지름 6dp 원형, fill: Error
  · 컴포넌트 이름: "Badge/Small"

  Badge/Large:
  · pill 모양: height 16dp, min-width 16dp, corner radius 8dp, fill: Error
  · 안에 "3" 텍스트 (11sp, On-Error, center), 좌우 패딩 4dp
  · 컴포넌트 이름: "Badge/Large"

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Small badge (dot)
  Badge(child: Icon(Icons.notifications))

  // Large badge (label)
  Badge(
    label: Text('3'),
    child: Icon(Icons.shopping_cart),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Small badge (dot) — 알림 아이콘에 점 배지
Badge(
  child: Icon(
    Icons.notifications,
    size: AppIconSize.base, // 20dp
    color: cs.onSurfaceVariant,
  ),
)

// Large badge (label) — 장바구니 수량 배지
Badge(
  label: Text('3'),
  backgroundColor: cs.error,
  textColor: cs.onError,
  child: Icon(
    Icons.shopping_cart,
    size: AppIconSize.base, // 20dp
  ),
)
```
