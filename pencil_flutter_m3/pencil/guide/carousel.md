# Carousel

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/carousel/overview |
| Guidelines | https://m3.material.io/components/carousel/guidelines |
| Specs | https://m3.material.io/components/carousel/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Carousel | `CarouselView` (Flutter 3.19+) |
| Uncontained | `CarouselView` |
| Hero | `CarouselView` |

## 언제 사용하나요?

- 이미지, 카드, 미디어 컬렉션을 가로 스크롤로 탐색할 때
- 쇼핑, 앨범, 추천 콘텐츠처럼 탐색 중심 UI에 사용할 때
- PageView보다 양쪽 항목이 살짝 보이는 형태가 필요할 때
- 콘텐츠 피드 내에서 연속된 시각 항목을 보여줄 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Multi-browse 또는 Uncontained Carousel |
| Tablet (medium) | Hero Carousel 또는 더 넓은 아이템 너비 사용 |
| Desktop/Web (expanded) | 그리드 레이아웃으로 대체 고려, 또는 넓은 Hero Carousel |

## Variants

- **Multi-browse** — 여러 항목을 동시에 표시
- **Uncontained** — 양쪽으로 항목이 넘침
- **Hero** — 하나의 항목을 크게 강조
- **Full-screen** — 전체 화면 슬라이드

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Carousel Guide" 프레임을 만들어주세요.
모든 내용은 이 "Carousel Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/carousel/overview

---

## 프레임 설정
- 이름: "Carousel Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Carousel"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · carousel"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/carousel/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 이미지, 카드, 미디어 컬렉션을 가로 스크롤로 탐색할 때
  · 쇼핑, 앨범, 추천 콘텐츠처럼 탐색 중심 UI에 사용할 때
  · PageView보다 양쪽 항목이 살짝 보이는 형태가 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 가로 나란히 배치, gap 16px

  ┌─ Multi-browse ───────────────────┐
  │  가로 스크롤 영역 (너비 360dp)     │
  │  작은 카드 3개 가로 나열           │
  │  각 카드: 100×100dp, corner 8dp  │
  │  배경: Secondary Container (Secondary Cont.) │
  │  카드 간격: 8dp                   │
  └───────────────────────────────────┘

  ┌─ Uncontained ────────────────────┐
  │  가로 스크롤, 카드가 화면 끝 넘침  │
  │  첫 카드: 240dp, 나머지 살짝 보임  │
  │  corner: 12dp                    │
  └───────────────────────────────────┘

  ┌─ Hero ───────────────────────────┐
  │  큰 카드 1개 중앙 (280dp)         │
  │  양쪽에 소형 카드 부분 노출       │
  │  corner: 16dp                    │
  └───────────────────────────────────┘

  ┌─ Full-screen ────────────────────┐
  │  카드 1개가 화면 전체 너비 차지    │
  │  360×480dp                       │
  │  corner: 0dp                     │
  └───────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Multi-browse Carousel을 크게 그리고 번호 레이블 연결:
  1. Scroll container — 가로 스크롤 영역, padding 12dp
  2. Item card — 개별 카드, corner radius, surfaceContainerLow 배경
  3. Item image — 카드 내부 이미지 (ClipRRect로 corner 적용)
  4. Item label (선택) — 카드 하단 텍스트 (titleSmall, onSurface)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                  | Multi-browse        | Hero                | 토큰                              |
  |----------------------|---------------------|---------------------|-----------------------------------|
  | Item corner radius   | 8 dp                | 16 dp               | AppRadius.xs / AppRadius.lg       |
  | Item gap             | 8 dp                | 8 dp                | —                                 |
  | Scroll direction     | Horizontal          | Horizontal          | —                                 |
  | Visible items        | 3+                  | 1 (+ partial)       | —                                 |
  | Item bg              | surfaceContainerLow | surfaceContainerLow | colorScheme.surfaceContainerLow   |
  | Label TextStyle      | titleSmall          | titleSmall          | textTheme.titleSmall              |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Multi-browse 또는 Uncontained│
  │  → CarouselView            │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Hero Carousel 또는 넓은 아이템│
  │  → CarouselView            │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  그리드 레이아웃 또는 Hero   │
  │  → GridView 또는 CarouselView│
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Carousel Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Carousel/Item/Unselected — 비선택 아이템:
  · 컴포넌트 이름: "Carousel/Item/Unselected"
  · 크기: 186×194dp, corner: 16dp
  · 배경: Surface Container
  · 간격: 8dp

  Carousel/Item/Selected — 선택 아이템:
  · 컴포넌트 이름: "Carousel/Item/Selected"
  · 크기: 272×194dp, corner: 16dp
  · 배경: Surface Container


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  CarouselView(
    itemExtent: 200,
    children: [
      Container(color: Colors.purple[100]),
      Container(color: Colors.blue[100]),
      Container(color: Colors.green[100]),
    ],
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Multi-browse Carousel — 기본 (Flutter 3.19+)
CarouselView(
  itemExtent: 200,
  itemSnapping: false,
  padding: EdgeInsets.symmetric(horizontal: AppSpacing.base),
  children: List.generate(5, (i) => ClipRRect(
    borderRadius: BorderRadius.circular(AppRadius.sm),  // 8dp
    child: Container(
      color: cs.surfaceContainerLow,
      alignment: Alignment.center,
      child: Text('Item $i', style: tt.titleSmall),
    ),
  )),
)

// Hero Carousel — 단일 항목 강조 (itemSnapping: true)
CarouselView(
  itemExtent: 300,
  shrinkExtent: 200,  // 스크롤 시 양쪽 아이템 축소 크기
  itemSnapping: true,
  children: List.generate(3, (i) => ClipRRect(
    borderRadius: BorderRadius.circular(AppRadius.lg),  // 16dp
    child: Stack(
      fit: StackFit.expand,
      children: [
        Container(color: cs.primaryContainer),
        Positioned(
          bottom: AppSpacing.base,
          left: AppSpacing.base,
          child: Text('Slide ${i + 1}', style: tt.titleMedium),
        ),
      ],
    ),
  )),
)

// CarouselController — 프로그래매틱 제어
final controller = CarouselController();
CarouselView(
  controller: controller,
  itemExtent: 200,
  children: [/* items */],
)
// 다음 항목으로 이동
ElevatedButton(
  onPressed: () => controller.nextItem(),
  child: const Text('다음'),
)
```
