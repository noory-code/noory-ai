# Menus

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/menus/overview |
| Guidelines | https://m3.material.io/components/menus/guidelines |
| Specs | https://m3.material.io/components/menus/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Dropdown menu | `DropdownMenu` |
| Popup menu | `PopupMenuButton` |
| Menu anchor | `MenuAnchor` |
| Cascading menu | `SubmenuButton` |

## 언제 사용하나요?

- 아이콘 버튼, 텍스트 필드에서 임시 선택지 목록을 펼칠 때
- 더보기(⋮) 버튼에서 보조 액션 목록을 보여줄 때
- 드롭다운 방식으로 하나의 값을 선택해야 할 때
- 길게 누르거나 우클릭으로 컨텍스트 메뉴를 보여줄 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | PopupMenuButton, 최대 너비 화면의 80% |
| Tablet (medium) | 동일, 터치 타겟 크기 유지 |
| Desktop/Web (expanded) | 우클릭 Context Menu 지원, Cascading 메뉴 활용 가능 |

## Variants

- **Dropdown** — 텍스트 필드 형태의 선택 메뉴
- **Popup** — 버튼에 붙는 팝업 목록
- **Cascading** — 서브메뉴 포함 계층 구조

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Menus Guide" 프레임을 만들어주세요.
모든 내용은 이 "Menus Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/menus/overview

---

## 프레임 설정
- 이름: "Menus Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Menus"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · menus"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/menus/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 아이콘 버튼에서 임시 선택지 목록을 펼칠 때
  · 더보기(⋮) 버튼에서 보조 액션 목록을 보여줄 때
  · 드롭다운 방식으로 하나의 값을 선택해야 할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 가로 나란히 배치, gap 24px

  ┌─ Dropdown Menu ────────────────────┐
  │  텍스트 필드 (너비 200dp, h 56dp)   │
  │  "Select option" + 드롭다운 화살표  │
  │  아래에 메뉴 패널 (w 200, h 160dp) │
  │  bg: Surface, corner 4dp           │
  │  shadow: dp2                       │
  │  아이템 3개 (height 48dp 각):      │
  │    "Option 1", "Option 2", "Option 3" │
  └────────────────────────────────────┘

  ┌─ Popup Menu ───────────────────────┐
  │  ⋮ 아이콘 버튼 (48×48dp)           │
  │  우하단에 메뉴 패널 (w 180, h 160) │
  │  bg: Surface, corner 4dp          │
  │  shadow: dp2                      │
  │  아이템 3개 (h 48dp 각):          │
  │    "Rename", "Delete", "Share"    │
  └────────────────────────────────────┘

  ┌─ Cascading Menu ───────────────────┐
  │  메뉴 패널 (w 180dp)               │
  │  아이템: "Share ▶"                │
  │  우측에 서브메뉴 패널 펼침          │
  │    "Email", "Message", "Copy link" │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Popup Menu를 크게 그리고 번호 레이블 연결:
  1. Menu container — Surface bg, corner 4dp, shadow dp2
  2. Menu item — height 48dp, hpad 12dp
  3. Leading icon (선택) — 24dp
  4. Item label — 14sp, On-Surface
  5. Trailing element (선택) — 단축키, 화살표
  6. Divider (선택) — 그룹 구분

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                    | 값                  |
  |------------------------|---------------------|
  | Item height            | 48 dp               |
  | Min width              | 112 dp              |
  | Max width              | 280 dp              |
  | Horizontal pad         | 12 dp               |
  | Corner radius          | 4 dp                |
  | Elevation              | Level 2             |
  | Label TextStyle (M3)   | labelLarge          |
  | Label color            | onSurface           |
  | Leading icon color     | onSurfaceVariant    |
  | Trailing text color    | onSurfaceVariant    |
  | Container bg           | surfaceContainer    |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  PopupMenuButton 활용       │
  │  → PopupMenuButton         │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  동일, 터치 타겟 크기 유지   │
  │  → PopupMenuButton         │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  우클릭 메뉴, Cascading 활용│
  │  → MenuAnchor + SubmenuButton │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Menus Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Menus/DropdownMenu — 텍스트 필드 연결형:
  · 컴포넌트 이름: "Menus/DropdownMenu"
  · 너비: 112~280dp, 배경: Surface Container, corner: 4dp
  · Elevation: Level 2
  · 아이템들: 높이 48dp, 수평 패딩 12dp

  Menus/MenuItem — 개별 아이템:
  · 컴포넌트 이름: "Menus/MenuItem"
  · 높이: 48dp, 수평 패딩: 12dp
  · 텍스트: 14sp, On-Surface
  · leading icon: 24dp, On-Surface-Variant (선택)
  · trailing text: On-Surface-Variant (단축키, 선택)


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Dropdown
  DropdownMenu(
    dropdownMenuEntries: [
      DropdownMenuEntry(value: 1, label: 'Option 1'),
      DropdownMenuEntry(value: 2, label: 'Option 2'),
    ],
    onSelected: (value) {},
  )

  // Popup
  PopupMenuButton(
    itemBuilder: (context) => [
      PopupMenuItem(value: 'rename', child: Text('Rename')),
      PopupMenuItem(value: 'delete', child: Text('Delete')),
    ],
    onSelected: (value) {},
  )

  // Cascading (MenuAnchor + SubmenuButton)
  MenuAnchor(
    menuChildren: [
      MenuItemButton(child: Text('Option 1'), onPressed: () {}),
      SubmenuButton(
        menuChildren: [
          MenuItemButton(child: Text('Sub 1'), onPressed: () {}),
        ],
        child: Text('More ▶'),
      ),
    ],
    builder: (context, controller, child) => IconButton(
      icon: Icon(Icons.more_vert),
      onPressed: () => controller.isOpen ? controller.close() : controller.open(),
    ),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Dropdown Menu
DropdownMenu<int>(
  menuStyle: MenuStyle(
    elevation: WidgetStatePropertyAll(AppElevation.level2),
    backgroundColor: WidgetStatePropertyAll(cs.surfaceContainer),
    shape: WidgetStatePropertyAll(
      RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.xs)),
    ),
  ),
  dropdownMenuEntries: const [
    DropdownMenuEntry(value: 1, label: 'Option 1'),
    DropdownMenuEntry(value: 2, label: 'Option 2'),
    DropdownMenuEntry(value: 3, label: 'Option 3'),
  ],
  onSelected: (value) {},
)

// Popup Menu (⋮ 버튼)
PopupMenuButton<String>(
  icon: Icon(Icons.more_vert, size: AppIconSize.md),
  itemBuilder: (context) => [
    PopupMenuItem(value: 'rename', child: Text('Rename', style: tt.labelLarge)),
    const PopupMenuDivider(),
    PopupMenuItem(value: 'delete', child: Text('Delete', style: tt.labelLarge)),
  ],
  onSelected: (value) {},
)

// Cascading (MenuAnchor + SubmenuButton)
MenuAnchor(
  menuChildren: [
    MenuItemButton(
      leadingIcon: Icon(Icons.edit, color: cs.onSurfaceVariant),
      child: Text('Edit', style: tt.labelLarge),
      onPressed: () {},
    ),
    SubmenuButton(
      menuChildren: [
        MenuItemButton(child: Text('Email'), onPressed: () {}),
        MenuItemButton(child: Text('Copy link'), onPressed: () {}),
      ],
      child: Text('Share ▶', style: tt.labelLarge),
    ),
  ],
  builder: (context, controller, child) => IconButton(
    icon: Icon(Icons.more_vert),
    onPressed: () => controller.isOpen ? controller.close() : controller.open(),
  ),
)
```
