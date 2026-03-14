# Cards

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/cards/overview |
| Guidelines | https://m3.material.io/components/cards/guidelines |
| Specs | https://m3.material.io/components/cards/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Elevated | `Card` |
| Filled | `Card.filled()` |
| Outlined | `Card.outlined()` |

## 언제 사용하나요?

- 연관된 정보를 그룹화해 시각적으로 구분할 때
- 앨범, 연락처, 위치 등 구조화된 콘텐츠를 표시할 때
- 탭/클릭으로 상세 화면으로 이동하는 터치 타겟이 필요할 때
- 목록에서 개별 항목을 시각적으로 분리할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 카드, 세로 목록 배치 |
| Tablet (medium) | 2열 그리드 배치 |
| Desktop/Web (expanded) | 3열 이상 그리드 배치, 고정 최대 너비 권장 |

## Variants

- **Elevated** — 그림자로 부상된 느낌, 기본형
- **Filled** — 채워진 배경, 그림자 없음
- **Outlined** — 테두리로 구분, 배경 없음

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Cards Guide" 프레임을 만들어주세요.
모든 내용은 이 "Cards Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/cards/overview

---

## 프레임 설정
- 이름: "Cards Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Cards"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · cards"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/cards/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 연관된 정보를 그룹화해 시각적으로 구분할 때
  · 앨범, 연락처, 위치 등 구조화된 콘텐츠를 표시할 때
  · 탭/클릭으로 상세 화면으로 이동하는 터치 타겟이 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 가로 나란히 배치, gap 24px

  ┌─ Elevated ─────────────────────────┐
  │  너비: 200dp, 높이: 120dp           │
  │  배경: Surface (Surface)            │
  │  shadow: dp1 (elevation 1)          │
  │  corner radius: 12dp               │
  │  내부: 제목(14sp) + 본문(12sp)      │
  │  패딩: 16dp                        │
  └────────────────────────────────────┘

  ┌─ Filled ───────────────────────────┐
  │  너비: 200dp, 높이: 120dp           │
  │  배경: surfaceContainerHighest             │
  │  shadow: none                      │
  │  corner radius: 12dp               │
  │  내부: 제목(14sp) + 본문(12sp)      │
  │  패딩: 16dp                        │
  └────────────────────────────────────┘

  ┌─ Outlined ─────────────────────────┐
  │  너비: 200dp, 높이: 120dp           │
  │  배경: Surface (Surface)            │
  │  border: 1dp, Outline Variant (Outline)   │
  │  shadow: none                      │
  │  corner radius: 12dp               │
  │  내부: 제목(14sp) + 본문(12sp)      │
  │  패딩: 16dp                        │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Elevated Card를 크게 그리고 번호 레이블 연결:
  1. Container — corner 12dp, Surface 배경, elevation 1
  2. Thumbnail / media area (선택) — 상단 이미지 영역
  3. Header — 제목 텍스트 (14sp, bold)
  4. Subhead — 부제목 텍스트 (12sp)
  5. Body text — 본문 (12sp, On-Surface-Variant)
  6. Action area (선택) — 버튼 또는 아이콘

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | 값           |
  |------------------|--------------|
  | Corner radius    | 12 dp        |
  | Padding          | 16 dp        |
  | Elevation (Elevated) | dp1     |
  | Border (Outlined) | 1 dp       |
  | Color (Elevated) | Surface      |
  | Color (Filled)   | surfaceContainerHighest |
  | Color (Outlined) | Surface      |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비, 세로 목록 배치   │
  │  → Card (full width)       │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  2열 그리드 배치             │
  │  → Card in GridView        │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  3열 이상 그리드, 최대 너비   │
  │  → Card in GridView        │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Cards Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  Cards/Elevated — 그림자 카드:
  · 컴포넌트 이름: "Cards/Elevated"
  · 너비: 360dp, corner: 12dp, 패딩: 16dp
  · 배경: Surface Container Low, Elevation: Level 1
  · 내부: headline (14sp bold) + supportingText (12sp, On-Surface-Variant)

  Cards/Filled — 채워진 카드:
  · 컴포넌트 이름: "Cards/Filled"
  · 너비: 360dp, corner: 12dp, 패딩: 16dp
  · 배경: Surface Container Highest, Elevation: 0

  Cards/Outlined — 테두리 카드:
  · 컴포넌트 이름: "Cards/Outlined"
  · 너비: 360dp, corner: 12dp, 패딩: 16dp
  · 배경: Surface, 테두리: Outline Variant 1dp


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Elevated (기본)
  Card(child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Content'),
  ))

  // Filled
  Card.filled(child: Padding(...))

  // Outlined
  Card.outlined(child: Padding(...))

---

## Flutter Usage

> `Card`는 `AppTheme` 적용 시 `colorScheme`에서 색상과 elevation을 자동으로 가져온다.
> `color`, `elevation`을 직접 지정하는 건 기본값에서 벗어나는 **커스터마이징** 시에만 사용한다.

```dart
import 'package:flutter_design/flutter_design.dart';

// 기본 사용 — 테마가 색상 자동 적용
Card(
  child: Padding(
    padding: EdgeInsets.all(AppSpacing.base), // 12dp
    child: Text('카드 내용'),
  ),
)

// 커스터마이징 — 색상/elevation을 직접 지정해야 할 때
final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Elevated Card (기본)
Card(
  elevation: AppElevation.level1, // 1dp
  color: cs.surfaceContainerLow,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.md), // 16dp
  ),
  child: Padding(
    padding: EdgeInsets.all(AppSpacing.base), // 12dp
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('카드 제목', style: tt.titleMedium),
        SizedBox(height: AppSpacing.sm), // 4dp
        Text('설명 텍스트', style: tt.bodyMedium?.copyWith(
          color: cs.onSurfaceVariant,
        )),
      ],
    ),
  ),
)

// Outlined Card
Card.outlined(
  child: Padding(
    padding: EdgeInsets.all(AppSpacing.base), // 12dp
    child: Text('Outlined', style: tt.bodyMedium),
  ),
)
```
