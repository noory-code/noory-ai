# Dialogs

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/dialogs/overview |
| Guidelines | https://m3.material.io/components/dialogs/guidelines |
| Specs | https://m3.material.io/components/dialogs/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Basic dialog | `AlertDialog` |
| Full-screen dialog | `Dialog.fullscreen()` |
| Custom dialog | `Dialog` + `showDialog()` |

## 언제 사용하나요?

- 삭제, 결제 등 되돌릴 수 없는 고위험 액션을 확인받을 때
- 사용자가 반드시 확인해야 하는 중요한 정보를 표시할 때
- 하나의 작업에 집중된 단순한 폼/입력이 필요할 때
- 현재 화면 흐름을 잠시 중단하고 결정을 요구할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Full-screen Dialog (복잡한 폼), Basic Dialog (확인) |
| Tablet (medium) | Basic Dialog, 최대 너비 560dp |
| Desktop/Web (expanded) | Basic Dialog, 중앙 배치, 최대 너비 560dp |

> Full-screen Dialog는 모바일 전용. 태블릿/데스크탑에서는 일반 Dialog 사용.

## Variants

- **Basic** — 제목 + 내용 + 버튼 (AlertDialog)
- **Full-screen** — 복잡한 작업을 위한 전체 화면 (모바일 전용)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Dialogs Guide" 프레임을 만들어주세요.
모든 내용은 이 "Dialogs Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/dialogs/overview

---

## 프레임 설정
- 이름: "Dialogs Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Dialogs"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · dialogs"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/dialogs/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 삭제, 결제 등 되돌릴 수 없는 고위험 액션을 확인받을 때
  · 사용자가 반드시 확인해야 하는 중요한 정보를 표시할 때
  · 현재 화면 흐름을 잠시 중단하고 결정을 요구할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Basic Dialog ─────────────────────┐
  │  너비: 312dp (최대 560dp)           │
  │  배경: surfaceContainerHigh        │
  │  corner: 28dp                      │
  │  상단 아이콘 (선택): 24dp, center   │
  │    일반: secondary / 위험: error    │
  │  제목: "Delete item?"              │
  │    (headlineSmall, onSurface)      │
  │  본문: "This action cannot..."     │
  │    (bodyMedium, onSurfaceVariant)  │
  │  scrim: black 32%                  │
  │  하단 버튼 2개 (우측 정렬):         │
  │    Cancel (TextButton)             │
  │    Delete (FilledButton)           │
  └────────────────────────────────────┘

  ┌─ Full-screen Dialog ───────────────┐
  │  너비: 360dp (전체), 높이: 800dp   │
  │  배경: Surface                     │
  │  상단 앱바: 닫기(X) + 제목 + 저장  │
  │  스크롤 콘텐츠 영역                │
  │  레이블: "Full-screen (모바일 전용)"│
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Basic Dialog를 크게 그리고 번호 레이블 연결:
  1. Scrim — black 32% (barrierColor)
  2. Container — corner 28dp, surfaceContainerHigh
  3. Icon (선택) — 24dp, center (secondary 또는 error)
  4. Headline — headlineSmall, onSurface, center
  5. Supporting text — bodyMedium, onSurfaceVariant
  6. Action buttons — 우측 정렬, TextButton + FilledButton

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                  | 값                   | 토큰                          |
  |----------------------|----------------------|-------------------------------|
  | Min width            | 280 dp               | —                             |
  | Max width            | 560 dp               | —                             |
  | Corner radius        | 28 dp                | AppRadius.xl                  |
  | Padding (all sides)  | 24 dp                | AppSpacing.xl                 |
  | Icon size            | 24 dp                | AppIconSize.md                |
  | Headline TextStyle   | headlineSmall        | textTheme.headlineSmall       |
  | Body TextStyle       | bodyMedium           | textTheme.bodyMedium          |
  | Headline color       | onSurface            | colorScheme.onSurface         |
  | Body color           | onSurfaceVariant     | colorScheme.onSurfaceVariant  |
  | Container color      | surfaceContainerHigh | colorScheme.surfaceContainerHigh |
  | Icon color (일반)    | secondary            | colorScheme.secondary         |
  | Icon color (위험)    | error                | colorScheme.error             |
  | Scrim                | black 32%            | Colors.black54                |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Basic 또는 Full-screen     │
  │  → AlertDialog / Dialog.fullscreen │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Basic Dialog, 최대 560dp   │
  │  → AlertDialog             │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Basic Dialog, 중앙 배치     │
  │  → AlertDialog             │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Dialogs Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Dialogs/Basic — 기본 다이얼로그:
  · 컴포넌트 이름: "Dialogs/Basic"
  · 너비: 280~560dp, 배경: Surface Container High, corner: 28dp
  · 아이콘 영역: 24dp 아이콘, 수평 중앙 (선택)
  · 제목: 24sp, On-Surface, 패딩: 24dp
  · 내용: 14sp, On-Surface-Variant
  · 버튼 영역: 하단 우측 정렬, TextButton + FilledButton

  Dialogs/Basic/WithIcon — 아이콘 포함 다이얼로그:
  · 컴포넌트 이름: "Dialogs/Basic/WithIcon"
  · 너비: 280~560dp, 배경: Surface Container High, corner: 28dp
  · 아이콘: 24dp, 수평 중앙, Secondary 또는 Error 색상
  · 제목: 24sp, On-Surface, 중앙 정렬
  · 내용: 14sp, On-Surface-Variant
  · 버튼 영역: 하단 우측 정렬, TextButton + FilledButton

  Dialogs/FullScreen — 전체 화면:
  · 컴포넌트 이름: "Dialogs/FullScreen"
  · 전체 화면형 (모바일 전용)
  · 상단 앱바: 닫기(X) + 제목 + 저장 버튼

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Basic Dialog
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      backgroundColor: cs.surfaceContainerHigh,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(28),
      ),
      icon: Icon(Icons.warning_amber_rounded, color: cs.error),
      title: Text('Delete item?', style: tt.headlineSmall),
      content: Text(
        'This action cannot be undone.',
        style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text('Cancel')),
        FilledButton(onPressed: () {}, child: Text('Delete')),
      ],
    ),
  );

  // Full-screen Dialog (모바일 전용)
  Navigator.push(context, MaterialPageRoute(
    fullscreenDialog: true,
    builder: (context) => Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: Icon(Icons.close), onPressed: () => Navigator.pop(context)),
        title: Text('New item'),
        actions: [TextButton(onPressed: () {}, child: Text('Save'))],
      ),
      body: Placeholder(),
    ),
  ));

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Basic Dialog — 기본 확인/취소
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    backgroundColor: cs.surfaceContainerHigh,
    elevation: AppElevation.level3, // 6dp
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(AppRadius.xl), // 28dp
    ),
    icon: Icon(Icons.warning_amber_rounded, color: cs.error),
    title: Text('항목을 삭제할까요?', style: tt.headlineSmall),
    contentPadding: EdgeInsets.fromLTRB(
      AppSpacing.xl, AppSpacing.sm, AppSpacing.xl, AppSpacing.xl,
    ),
    content: Text(
      '이 작업은 되돌릴 수 없습니다.',
      style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
    ),
    actionsPadding: EdgeInsets.symmetric(
      horizontal: AppSpacing.xl, vertical: AppSpacing.sm,
    ),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: const Text('취소'),
      ),
      FilledButton(
        onPressed: () => Navigator.pop(context, true),
        child: const Text('삭제'),
      ),
    ],
  ),
);

// barrierDismissible — 고위험 액션은 false (배경 탭으로 닫기 방지)
showDialog(
  context: context,
  barrierDismissible: false,
  builder: (context) => AlertDialog(
    title: const Text('결제를 진행할까요?'),
    content: const Text('이 작업은 즉시 결제됩니다.'),
    actions: [
      TextButton(onPressed: () => Navigator.pop(context), child: const Text('취소')),
      FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('결제')),
    ],
  ),
);

// scrollable — 콘텐츠가 길 때 (이용약관 등)
AlertDialog(
  scrollable: true,
  title: const Text('이용약관'),
  content: const Text('...긴 내용...'),
  actions: [
    TextButton(onPressed: () => Navigator.pop(context), child: const Text('닫기')),
  ],
)

// actionsAlignment — 버튼 정렬 변경 (기본: MainAxisAlignment.end)
AlertDialog(
  actionsAlignment: MainAxisAlignment.spaceEvenly,
  actions: [
    TextButton(onPressed: () => Navigator.pop(context), child: const Text('나중에')),
    FilledButton(onPressed: () {}, child: const Text('업데이트')),
  ],
)

// Full-screen Dialog — 복잡한 폼 (모바일 전용)
// Option 1: Navigator.push + fullscreenDialog: true (권장)
Navigator.push(
  context,
  MaterialPageRoute(
    fullscreenDialog: true,
    builder: (context) => Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text('새 항목 만들기'),
        actions: [
          TextButton(onPressed: () {}, child: const Text('저장')),
        ],
      ),
      body: const Placeholder(),
    ),
  ),
);

// Option 2: Dialog.fullscreen() 생성자 (Flutter 3.10+)
showDialog(
  context: context,
  builder: (context) => Dialog.fullscreen(
    child: Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text('새 항목 만들기'),
        actions: [
          TextButton(onPressed: () {}, child: const Text('저장')),
        ],
      ),
      body: const Placeholder(),
    ),
  ),
);
```
