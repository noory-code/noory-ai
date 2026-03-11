# Bottom Sheets

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/bottom-sheets/overview |
| Guidelines | https://m3.material.io/components/bottom-sheets/guidelines |
| Specs | https://m3.material.io/components/bottom-sheets/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Modal | `showModalBottomSheet()` |
| Persistent | `ScaffoldState.showBottomSheet()` |
| Base | `BottomSheet` |

## 언제 사용하나요?

- 사용자의 주의가 필요한 선택지를 Modal로 제시할 때
- 메인 콘텐츠를 가리지 않고 부가 정보를 하단에 지속 표시할 때
- 공유, 필터, 상세 정보 등 보조 작업 흐름에 사용할 때
- 메뉴나 다이얼로그 대신 더 많은 옵션을 제공할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Bottom Sheet 사용 (modal 또는 persistent) |
| Tablet (medium) | Bottom Sheet 또는 Side Sheet로 대체 고려 |
| Desktop/Web (expanded) | Side Sheet 또는 Dialog로 대체 권장 |

> 넓은 화면에서 Bottom Sheet는 좁은 너비로 중앙에 표시되거나 Side Sheet로 대체됨.

## Variants

- **Modal** — 다른 영역 터치 차단, 포커스 집중
- **Persistent** — 다른 화면 요소와 동시에 상호작용 가능

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Bottom Sheets Guide" 프레임을 만들어주세요.
모든 내용은 이 "Bottom Sheets Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/bottom-sheets/overview

---

## 프레임 설정
- 이름: "Bottom Sheets Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Bottom Sheets"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · bottom-sheets"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/bottom-sheets/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 사용자의 주의가 필요한 선택지를 Modal로 제시할 때
  · 메인 콘텐츠를 가리지 않고 부가 정보를 하단에 지속 표시할 때
  · 공유, 필터, 상세 정보 등 보조 작업 흐름에 사용할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Modal ────────────────────────────┐
  │  너비: 360dp                        │
  │  배경: 반투명 scrim (#000, 32%)     │
  │  위에 sheet (높이 320dp) 그리기:    │
  │    배경: Surface (Surface)          │
  │    상단 corner: 28dp                │
  │    drag handle: 가운데 32×4dp 바    │
  │    handle 색상: Outline Variant             │
  │    내용: 텍스트 3줄 (선택 옵션)      │
  │  레이블: "Modal"                   │
  └────────────────────────────────────┘

  ┌─ Persistent ───────────────────────┐
  │  너비: 360dp, 전체 높이: 640dp      │
  │  하단 200dp: sheet 영역             │
  │  상단 440dp: 메인 콘텐츠 (회색)     │
  │  sheet 배경: Surface (Surface)      │
  │  sheet 상단 corner: 28dp           │
  │  drag handle: 가운데 32×4dp 바      │
  │  레이블: "Persistent"              │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Modal Bottom Sheet를 크게 그리고 번호 레이블 연결:
  1. Scrim — 반투명 오버레이, #000 32%
  2. Container — surfaceContainerLow 배경, top corner 28dp
  3. Drag handle — 32×4dp, onSurfaceVariant, 상단 center
  4. Header (선택) — 제목 텍스트 (titleMedium, onSurface)
  5. Content area — 스크롤 가능 영역

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성               | 값                      | 토큰                              |
  |-------------------|-------------------------|-----------------------------------|
  | Top corner radius  | 28 dp                   | AppRadius.xl                      |
  | Drag handle width  | 32 dp                   | —                                 |
  | Drag handle height | 4 dp                    | —                                 |
  | Drag handle color  | onSurfaceVariant        | colorScheme.onSurfaceVariant      |
  | Min height         | 정의 없음               | —                                 |
  | Max height         | 화면의 90%              | —                                 |
  | Container bg       | surfaceContainerLow     | colorScheme.surfaceContainerLow   |
  | Header TextStyle   | titleMedium             | textTheme.titleMedium             |
  | Scrim              | black 32%               | Colors.black54                    |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Bottom Sheet 사용          │
  │  → showModalBottomSheet()  │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Bottom 또는 Side Sheet     │
  │  → Side Sheet 고려          │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Dialog 또는 Side Sheet 권장 │
  │  → showDialog()            │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Bottom Sheets Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  BottomSheet/Modal — 스크림 포함:
  · 컴포넌트 이름: "BottomSheet/Modal"
  · 너비: 360dp, 배경: Surface Container Low
  · 상단 corner: 28dp
  · 드래그 핸들: 32×4dp, On-Surface-Variant, 수평 중앙 상단 (핸들 상단 패딩 22dp)
  · 콘텐츠 패딩: 수평 16dp
  · Scrim: rgba(0,0,0,0.32)

  BottomSheet/Persistent — 스크림 없음:
  · 컴포넌트 이름: "BottomSheet/Persistent"
  · 너비: 360dp, 배경: Surface Container Low
  · 상단 corner: 28dp
  · 드래그 핸들: 32×4dp, On-Surface-Variant, 수평 중앙 상단


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Modal Bottom Sheet
  showModalBottomSheet(
    context: context,
    builder: (context) => const SizedBox(
      height: 300,
      child: Center(child: Text('Content')),
    ),
  );

  // Persistent Bottom Sheet
  Scaffold.of(context).showBottomSheet(
    (context) => const SizedBox(height: 200),
  );

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Modal Bottom Sheet — 기본 (테마 자동 적용)
showModalBottomSheet(
  context: context,
  backgroundColor: cs.surfaceContainerLow,
  shape: const RoundedRectangleBorder(
    borderRadius: BorderRadius.vertical(
      top: Radius.circular(AppRadius.xl), // 28dp
    ),
  ),
  builder: (context) => Padding(
    padding: EdgeInsets.fromLTRB(
      AppSpacing.lg, AppSpacing.md, AppSpacing.lg, AppSpacing.x2l,
    ),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 32,
          height: 4,
          decoration: BoxDecoration(
            color: cs.onSurfaceVariant.withValues(alpha: AppOpacity.pressed),
            borderRadius: BorderRadius.circular(AppRadius.xs),
          ),
        ),
        SizedBox(height: AppSpacing.lg),
        Text('옵션 선택', style: tt.titleMedium),
      ],
    ),
  ),
);

// isScrollControlled — 화면 높이 90%까지 확장 (긴 목록, 폼)
showModalBottomSheet(
  context: context,
  isScrollControlled: true,
  useSafeArea: true,  // 홈 인디케이터 영역 자동 처리
  builder: (context) => DraggableScrollableSheet(
    expand: false,
    initialChildSize: 0.5,
    minChildSize: 0.25,
    maxChildSize: 0.9,
    builder: (context, scrollController) => ListView.builder(
      controller: scrollController,
      itemCount: 20,
      itemBuilder: (context, index) => ListTile(title: Text('항목 $index')),
    ),
  ),
);

// Persistent Bottom Sheet
Scaffold.of(context).showBottomSheet(
  (context) => const SizedBox(height: 200, child: Placeholder()),
);
```
