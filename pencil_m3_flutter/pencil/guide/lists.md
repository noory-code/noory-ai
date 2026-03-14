# Lists

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/lists/overview |
| Guidelines | https://m3.material.io/components/lists/guidelines |
| Specs | https://m3.material.io/components/lists/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| List item | `ListTile` |
| Scrollable list | `ListView` / `ListView.builder()` |
| With checkbox | `CheckboxListTile` |
| With radio | `RadioListTile` |
| With switch | `SwitchListTile` |

## 언제 사용하나요?

- 동일한 형태의 항목을 연속으로 표시할 때 (설정, 연락처, 파일)
- 아이콘 + 텍스트 + 트레일링 액션 조합의 행 UI가 필요할 때
- 항목이 많아 스크롤이 필요한 긴 목록을 표시할 때
- 1~3줄 텍스트 밀도를 선택해 정보량을 조절할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 단일 열 전체 너비 목록 |
| Tablet (medium) | 단일 열 유지 또는 마스터-디테일 레이아웃 |
| Desktop/Web (expanded) | List-Detail 레이아웃 (목록 + 상세 패널 나란히) |

## Variants

- **1-line** — 제목만 표시
- **2-line** — 제목 + 부제목
- **3-line** — 제목 + 긴 부제목

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Lists Guide" 프레임을 만들어주세요.
모든 내용은 이 "Lists Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/lists/overview

---

## 프레임 설정
- 이름: "Lists Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Lists"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · lists"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/lists/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 동일한 형태의 항목을 연속으로 표시할 때 (설정, 연락처, 파일)
  · 아이콘 + 텍스트 + 트레일링 액션 조합의 행 UI가 필요할 때
  · 1~3줄 텍스트 밀도를 선택해 정보량을 조절할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 세로 나열 (각각 width 360dp), gap 16px

  ┌─ 1-line ──────────────────────────────────────────────┐
  │  height: 56dp                                          │
  │  leading icon (48dp 영역): 24dp 아이콘, On-Surface-Variant       │
  │  title: "Item title"  (16sp, On-Surface)                │
  │  trailing icon: 24dp 화살표                           │
  │  hpad: 16dp                                           │
  └────────────────────────────────────────────────────────┘

  ┌─ 2-line ──────────────────────────────────────────────┐
  │  height: 72dp                                          │
  │  leading icon (48dp 영역): 24dp 아이콘                │
  │  title: "Item title"  (16sp, On-Surface)                │
  │  subtitle: "Supporting text"  (14sp, On-Surface-Variant)         │
  │  trailing icon: 24dp                                  │
  └────────────────────────────────────────────────────────┘

  ┌─ 3-line ──────────────────────────────────────────────┐
  │  height: 88dp                                          │
  │  leading image (40×40dp, corner 4dp)                  │
  │  title: "Item title"  (16sp, On-Surface)                │
  │  subtitle: 긴 텍스트 2줄  (14sp, On-Surface-Variant)             │
  │  trailing text: "시간" (12sp, On-Surface-Variant)               │
  └────────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- 2-line ListTile을 크게 그리고 번호 레이블 연결:
  1. Leading element — 아이콘 또는 이미지 (선택)
  2. Headline — 제목 (16sp)
  3. Supporting text — 부제목 (14sp)
  4. Trailing element — 아이콘, 텍스트, 체크 (선택)
  5. Divider — 하단 구분선 (선택)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                          | 1-line          | 2-line          | 3-line          |
  |------------------------------|-----------------|-----------------|-----------------|
  | Height                       | 56 dp           | 72 dp           | 88 dp           |
  | Horizontal pad               | 16 dp           | 16 dp           | 16 dp           |
  | Leading area (min width)     | 40 dp           | 40 dp           | 40 dp           |
  | Title TextStyle (M3)         | bodyLarge       | bodyLarge       | bodyLarge       |
  | Subtitle TextStyle (M3)      | —               | bodyMedium      | bodyMedium      |
  | Title color                  | onSurface       | onSurface       | onSurface       |
  | Subtitle color               | —               | onSurfaceVariant| onSurfaceVariant|
  | Leading/Trailing icon color  | onSurfaceVariant| onSurfaceVariant| onSurfaceVariant|

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  단일 열 전체 너비 목록     │
  │  → ListView + ListTile     │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  단일 열 또는 마스터-디테일  │
  │  → ListView + ListTile     │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  List-Detail 레이아웃       │
  │  → 목록 + 상세 패널 나란히  │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Lists Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  Lists/OneLineItem — 1줄 항목:
  · 컴포넌트 이름: "Lists/OneLineItem"
  · 높이: 56dp, 너비: 360dp
  · 배경: Surface, 수평 패딩: 16dp
  · Leading: 40×40dp 아이콘 영역, Headline: 16sp On-Surface
  · Trailing: 24dp 아이콘 (선택)

  Lists/TwoLineItem — 2줄 항목:
  · 컴포넌트 이름: "Lists/TwoLineItem"
  · 높이: 72dp, 너비: 360dp
  · Headline: 16sp On-Surface, Supporting: 14sp On-Surface-Variant

  Lists/ThreeLineItem — 3줄 항목:
  · 컴포넌트 이름: "Lists/ThreeLineItem"
  · 높이: 88dp, 너비: 360dp
  · Leading: 40×40dp 이미지 (corner 4dp), Trailing: 12sp On-Surface-Variant


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  ListTile(
    leading: Icon(Icons.inbox),
    title: Text('Item title'),
    subtitle: Text('Supporting text'),
    trailing: Icon(Icons.chevron_right),
    onTap: () {},
  )

  // Scrollable list
  ListView.builder(
    itemCount: items.length,
    itemBuilder: (context, index) => ListTile(title: Text(items[index])),
  )

  // With checkbox
  CheckboxListTile(
    value: isChecked,
    onChanged: (v) => setState(() => isChecked = v!),
    title: Text('Item title'),
  )

  // With switch
  SwitchListTile(
    value: isEnabled,
    onChanged: (v) => setState(() => isEnabled = v),
    title: Text('Item title'),
    subtitle: Text('Supporting text'),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// 2-line ListTile (M3 기본)
ListTile(
  contentPadding: EdgeInsets.symmetric(horizontal: AppSpacing.base),
  leading: Icon(Icons.inbox, size: AppIconSize.md, color: cs.onSurfaceVariant),
  title: Text('Item title', style: tt.bodyLarge),
  subtitle: Text('Supporting text', style: tt.bodyMedium),
  trailing: Icon(Icons.chevron_right, size: AppIconSize.md),
  titleAlignment: ListTileTitleAlignment.threeLine, // M3 기본
  onTap: () {},
)

// Scrollable list
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(
    contentPadding: EdgeInsets.symmetric(horizontal: AppSpacing.base),
    title: Text(items[index]),
  ),
)

// Divider 삽입
...ListTile.divideTiles(
  context: context,
  tiles: items.map((item) => ListTile(title: Text(item))),
),

// CheckboxListTile
CheckboxListTile(
  value: isChecked,
  onChanged: (v) => setState(() => isChecked = v!),
  title: Text('Item title', style: tt.bodyLarge),
  subtitle: Text('Supporting text', style: tt.bodyMedium),
  controlAffinity: ListTileControlAffinity.leading, // 체크박스 왼쪽
)

// SwitchListTile
SwitchListTile(
  value: isEnabled,
  onChanged: (v) => setState(() => isEnabled = v),
  title: Text('Item title', style: tt.bodyLarge),
)

// 앱 전역 테마 설정
ListTileTheme(
  data: ListTileThemeData(
    contentPadding: EdgeInsets.symmetric(horizontal: 16),
    titleTextStyle: tt.bodyLarge?.copyWith(color: cs.onSurface),
    subtitleTextStyle: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
    iconColor: cs.onSurfaceVariant,
  ),
  child: ListView(...),
)
```
