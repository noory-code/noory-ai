# Side Sheets

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/side-sheets/overview |
| Guidelines | https://m3.material.io/components/side-sheets/guidelines |
| Specs | https://m3.material.io/components/side-sheets/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Modal | 커스텀 구현 또는 third-party 패키지 |
| Persistent | `Scaffold.endDrawer` 또는 커스텀 레이아웃 |

> Flutter에 Side Sheet 전용 위젯 없음. `endDrawer` 또는 커스텀 `AnimatedContainer`로 구현.

## 언제 사용하나요?

- 태블릿/데스크탑처럼 넓은 화면에서 메인 콘텐츠 옆에 부가 패널이 필요할 때
- 필터, 설정, 상세 정보처럼 메인 콘텐츠를 가리지 않고 보여줄 때
- Bottom Sheet의 세로 공간이 부족한 large 화면에서 대안으로 사용할 때
- 폼 입력, 검토 패널처럼 컨텍스트를 유지하며 사이드 작업이 필요할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | **사용 안 함** → Bottom Sheet 사용 |
| Tablet (medium) | Modal Side Sheet 사용 가능 |
| Desktop/Web (expanded) | **Persistent Side Sheet** — 메인 콘텐츠 옆 고정 |

## Variants

- **Modal** — 스크림 위에 겹쳐 표시
- **Persistent** — 메인 콘텐츠와 나란히 표시

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Side Sheets Guide" 프레임을 만들어주세요.

모든 내용은 이 "Side Sheets Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/side-sheets/overview

---

## 프레임 설정
- 이름: "Side Sheets Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Side Sheets"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · side-sheets"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/side-sheets/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 태블릿/데스크탑에서 메인 콘텐츠 옆에 부가 패널이 필요할 때
  · 필터, 설정, 상세처럼 메인 콘텐츠를 가리지 않고 보여줄 때
  · Bottom Sheet의 세로 공간이 부족한 large 화면의 대안

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Modal Side Sheet (1024×800dp) ────┐
  │  왼쪽: 메인 콘텐츠 (680dp)         │
  │  scrim: #000 32%                   │
  │  오른쪽: Side Sheet (344dp)        │
  │    배경: Surface Container Low      │
  │    상단 corner: 16dp (left side)   │
  │    상단 헤더: 제목 + 닫기 X         │
  │    내용: 필터 옵션 목록            │
  └────────────────────────────────────┘

  ┌─ Persistent Side Sheet (1024×800dp)┐
  │  왼쪽: 메인 콘텐츠 (680dp)         │
  │  오른쪽: Side Sheet (344dp)        │
  │    배경: Surface Container Low      │
  │    scrim 없음 (항상 표시)           │
  │    left border: 1dp, Outline       │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Modal Side Sheet를 크게 그리고 번호 레이블 연결:
  1. Scrim — 메인 콘텐츠 위 반투명 오버레이 (#000 32%)
  2. Container — surfaceContainerLow 배경, left corner 16dp
  3. Header — 제목 titleLarge + 닫기 아이콘 24dp (onSurface)
  4. Content area — 스크롤 가능 영역
  5. Action area (선택) — 하단 버튼 영역

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성               | 값                      | 토큰                              |
  |-------------------|-------------------------|-----------------------------------|
  | Width             | 256–400 dp              | —                                 |
  | Left corner (modal)| 16 dp                 | AppRadius.lg                      |
  | Header height     | 56 dp                   | —                                 |
  | Header TextStyle  | titleLarge              | textTheme.titleLarge              |
  | Container bg      | surfaceContainerLow     | colorScheme.surfaceContainerLow   |
  | Header icon color | onSurface               | colorScheme.onSurface             |
  | Scrim (modal)     | black 32%               | Colors.black54                    |
  | Divider (persistent)| outlineVariant        | colorScheme.outlineVariant        |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  사용 안 함                 │
  │  → Bottom Sheet 사용        │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Modal Side Sheet 사용     │
  │  → Scaffold.endDrawer      │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Persistent Side Sheet     │
  │  → 커스텀 Row 레이아웃      │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Side Sheets Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  SideSheet/Modal — 스크림 포함:
  · 컴포넌트 이름: "SideSheet/Modal"
  · 너비: 344dp, 높이: 전체 화면
  · 배경: Surface Container Low
  · 좌측 상단 corner: 16dp
  · 헤더: 56dp, 수평 패딩 24dp, 제목 24sp On-Surface
  · Scrim: rgba(0,0,0,0.32)

  SideSheet/Persistent — 메인 콘텐츠 옆 고정:
  · 컴포넌트 이름: "SideSheet/Persistent"
  · 너비: 344dp, scrim 없음
  · 배경: Surface Container Low
  · 좌측 구분선: Outline 1dp


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Modal (endDrawer 활용)
  Scaffold(
    endDrawer: SizedBox(
      width: 344,
      child: Drawer(child: Column(...)),
    ),
  )

  // Persistent (Row 레이아웃)
  Row(children: [
    Expanded(child: mainContent),
    SizedBox(width: 344, child: sideSheetContent),
  ])

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Modal Side Sheet — endDrawer 활용
Scaffold(
  endDrawer: SizedBox(
    width: 344,
    child: Drawer(
      backgroundColor: cs.surfaceContainerLow,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(AppRadius.lg),     // 16dp
          bottomLeft: Radius.circular(AppRadius.lg),
        ),
      ),
      child: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: AppSpacing.xl, vertical: AppSpacing.md,
              ),
              child: Row(
                children: [
                  Text('필터', style: tt.titleLarge),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, size: AppIconSize.md),
                    color: cs.onSurface,
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            const Divider(),
            // 필터 옵션 목록
            Expanded(child: ListView(children: [/* 옵션 */])),
          ],
        ),
      ),
    ),
  ),
)

// Persistent Side Sheet — Row 레이아웃으로 구현
Row(
  children: [
    Expanded(child: mainContent),
    Container(
      width: 344,
      decoration: BoxDecoration(
        color: cs.surfaceContainerLow,
        border: Border(
          left: BorderSide(color: cs.outlineVariant),
        ),
      ),
      child: sideSheetContent,
    ),
  ],
)
```
