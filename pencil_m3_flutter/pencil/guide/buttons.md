# Buttons

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/buttons/overview |
| Guidelines | https://m3.material.io/components/buttons/guidelines |
| Specs | https://m3.material.io/components/buttons/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Elevated | `ElevatedButton` |
| Elevated + Icon | `ElevatedButton.icon()` |
| Filled | `FilledButton` |
| Filled + Icon | `FilledButton.icon()` |
| Filled Tonal | `FilledButton.tonal()` |
| Filled Tonal + Icon | `FilledButton.tonalIcon()` |
| Outlined | `OutlinedButton` |
| Outlined + Icon | `OutlinedButton.icon()` |
| Text | `TextButton` |
| Text + Icon | `TextButton.icon()` |

## 언제 사용하나요?

- **Filled** — 화면에서 가장 중요한 주요 액션 (저장, 완료 등)
- **Filled Tonal** — 주요 액션보다 한 단계 낮은 보조 액션
- **Elevated** — 평면적인 레이아웃에서 버튼을 시각적으로 구분할 때
- **Outlined** — 중간 강조의 액션, 배경 없이 윤곽선으로 구분할 때
- **Text** — 가장 낮은 강조, 보조 액션이나 인라인 링크

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 버튼 또는 고정 크기 버튼 |
| Tablet (medium) | 고정 크기, 콘텐츠 너비에 맞게 |
| Desktop/Web (expanded) | 고정 크기, 좌측 정렬 또는 폼 하단 배치 |

> 모든 화면에서 동일한 위젯 사용. 레이아웃(너비, 위치)만 조정.

## Variants

- Type: Elevated / Filled / FilledTonal / Outlined / Text
- Shape: Rounded (AppRadius.full = 9999dp) / Rect (AppRadius.sm = 12dp)
- Size: Small (AppButtonSize.sm = 32dp) / Medium (AppButtonSize.md = 40dp) / Large (AppButtonSize.lg = 48dp)
- Icon: Label only / Icon+Label

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Buttons Guide" 프레임을 만들어주세요.
모든 내용은 이 "Buttons Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/buttons/overview

---

## 프레임 설정
- 이름: "Buttons Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Buttons"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · buttons"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/buttons/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · Filled — 가장 중요한 주요 액션 (저장, 완료)
  · Filled Tonal — 주요 액션보다 한 단계 낮은 보조 액션
  · Elevated — 평면 레이아웃에서 시각 구분이 필요할 때
  · Outlined — 중간 강조, 테두리로 구분
  · Text — 가장 낮은 강조, 보조 액션

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- 5개 타입을 각각 행(그룹)으로 배치, 타입 간 gap 32px
- 각 타입 행 안에서 Label only 6개(Rounded×3 + Rect×3) / Icon+Label 6개를 가로 나열, gap 12px

  ─── Elevated ──────────────────────────────────────────────────────────────
  Label only (좌→우):
  ┌──Rounded/sm──┐  ┌──Rounded/md──┐  ┌──Rounded/lg──┐  ┌──Rect/sm──┐  ┌──Rect/md──┐  ┌──Rect/lg──┐
  │h:32dp full   │  │h:40dp full   │  │h:48dp full   │  │h:32dp 12dp│  │h:40dp 12dp│  │h:48dp 12dp│
  │bg:SurfContLow│  │bg:SurfContLow│  │bg:SurfContLow│  │bg:SurfCont│  │bg:SurfCont│  │bg:SurfCont│
  │label:Primary │  │label:Primary │  │label:Primary │  │label:Prim │  │label:Prim │  │label:Prim │
  │pad:16dp,12sp │  │pad:24dp,14sp │  │pad:32dp,16sp │  │pad:16dp   │  │pad:24dp   │  │pad:32dp   │
  │Elevation L1  │  │Elevation L1  │  │Elevation L1  │  │Elev L1    │  │Elev L1    │  │Elev L1    │
  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  └───────────┘  └───────────┘
  Icon+Label (위 6개 각각에 좌측 아이콘 18/18/20dp 추가, gap 8dp):
  Rounded/sm/Icon  Rounded/md/Icon  Rounded/lg/Icon  Rect/sm/Icon  Rect/md/Icon  Rect/lg/Icon

  ─── Filled ────────────────────────────────────────────────────────────────
  Label only:
  ┌──Rounded/sm──┐  ┌──Rounded/md──┐  ┌──Rounded/lg──┐  ┌──Rect/sm──┐  ┌──Rect/md──┐  ┌──Rect/lg──┐
  │h:32dp full   │  │h:40dp full   │  │h:48dp full   │  │h:32dp 12dp│  │h:40dp 12dp│  │h:48dp 12dp│
  │bg:Primary    │  │bg:Primary    │  │bg:Primary    │  │bg:Primary │  │bg:Primary │  │bg:Primary │
  │label:OnPrim  │  │label:OnPrim  │  │label:OnPrim  │  │label:OnPrim│  │label:OnPrim│  │label:OnPrim│
  │pad:16dp,12sp │  │pad:24dp,14sp │  │pad:32dp,16sp │  │pad:16dp   │  │pad:24dp   │  │pad:32dp   │
  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  └───────────┘  └───────────┘
  Icon+Label: Rounded/sm/Icon  Rounded/md/Icon  Rounded/lg/Icon  Rect/sm/Icon  Rect/md/Icon  Rect/lg/Icon

  ─── FilledTonal ────────────────────────────────────────────────────────────
  Label only:
  ┌──Rounded/sm──┐  ┌──Rounded/md──┐  ┌──Rounded/lg──┐  ┌──Rect/sm──┐  ┌──Rect/md──┐  ┌──Rect/lg──┐
  │h:32dp full   │  │h:40dp full   │  │h:48dp full   │  │h:32dp 12dp│  │h:40dp 12dp│  │h:48dp 12dp│
  │bg:SecCont    │  │bg:SecCont    │  │bg:SecCont    │  │bg:SecCont │  │bg:SecCont │  │bg:SecCont │
  │label:OnSecCo │  │label:OnSecCo │  │label:OnSecCo │  │lbl:OnSecCo│  │lbl:OnSecCo│  │lbl:OnSecCo│
  │pad:16dp,12sp │  │pad:24dp,14sp │  │pad:32dp,16sp │  │pad:16dp   │  │pad:24dp   │  │pad:32dp   │
  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  └───────────┘  └───────────┘
  Icon+Label: Rounded/sm/Icon  Rounded/md/Icon  Rounded/lg/Icon  Rect/sm/Icon  Rect/md/Icon  Rect/lg/Icon

  ─── Outlined ────────────────────────────────────────────────────────────────
  Label only:
  ┌──Rounded/sm──┐  ┌──Rounded/md──┐  ┌──Rounded/lg──┐  ┌──Rect/sm──┐  ┌──Rect/md──┐  ┌──Rect/lg──┐
  │h:32dp full   │  │h:40dp full   │  │h:48dp full   │  │h:32dp 12dp│  │h:40dp 12dp│  │h:48dp 12dp│
  │bg:투명        │  │bg:투명        │  │bg:투명        │  │bg:투명    │  │bg:투명    │  │bg:투명    │
  │border:Outl 1dp│  │border:Outl 1dp│  │border:Outl 1dp│  │border:Outl│  │border:Outl│  │border:Outl│
  │label:Primary │  │label:Primary │  │label:Primary │  │label:Prim │  │label:Prim │  │label:Prim │
  │pad:16dp,12sp │  │pad:24dp,14sp │  │pad:32dp,16sp │  │pad:16dp   │  │pad:24dp   │  │pad:32dp   │
  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  └───────────┘  └───────────┘
  Icon+Label: Rounded/sm/Icon  Rounded/md/Icon  Rounded/lg/Icon  Rect/sm/Icon  Rect/md/Icon  Rect/lg/Icon

  ─── Text ────────────────────────────────────────────────────────────────────
  Label only:
  ┌──Rounded/sm──┐  ┌──Rounded/md──┐  ┌──Rounded/lg──┐  ┌──Rect/sm──┐  ┌──Rect/md──┐  ┌──Rect/lg──┐
  │h:32dp full   │  │h:40dp full   │  │h:48dp full   │  │h:32dp 12dp│  │h:40dp 12dp│  │h:48dp 12dp│
  │bg:투명        │  │bg:투명        │  │bg:투명        │  │bg:투명    │  │bg:투명    │  │bg:투명    │
  │label:Primary │  │label:Primary │  │label:Primary │  │label:Prim │  │label:Prim │  │label:Prim │
  │pad:16dp,12sp │  │pad:24dp,14sp │  │pad:32dp,16sp │  │pad:16dp   │  │pad:24dp   │  │pad:32dp   │
  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  └───────────┘  └───────────┘
  Icon+Label: Rounded/sm/Icon  Rounded/md/Icon  Rounded/lg/Icon  Rect/sm/Icon  Rect/md/Icon  Rect/lg/Icon

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Filled Button을 크게 그리고 번호 레이블 연결:
  1. Container — height 40dp, corner 20dp, Primary 배경
  2. Label text — 14sp, On-Primary, center
  3. Leading icon (선택) — 18dp, On-Primary, 좌측
  4. Trailing icon (선택) — 18dp, On-Primary, 우측

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | Small        | Medium       | Large        |
  |------------------|--------------|--------------|--------------|
  | Height           | 32 dp        | 40 dp        | 48 dp        |
  | AppButtonSize    | .sm          | .md          | .lg          |
  | Corner (Rounded) | full (9999dp)| full (9999dp)| full (9999dp)|
  | Corner (Rect)    | sm (12dp)    | sm (12dp)    | sm (12dp)    |
  | Horizontal pad   | 16 dp        | 24 dp        | 32 dp        |
  | Icon size        | 18 dp        | 18 dp        | 20 dp        |
  | Icon gap         | 8 dp         | 8 dp         | 8 dp         |
  | Label font       | 12sp, medium | 14sp, medium | 16sp, medium |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비 또는 고정 크기    │
  │  → FilledButton            │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  콘텐츠 너비에 맞게 고정     │
  │  → FilledButton            │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  고정 크기, 좌측 또는 폼 하단│
  │  → FilledButton            │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Buttons Guide" 프레임 안에 아래 60개 컴포넌트를 그리고, 각각 리유저블 컴포넌트로 등록한다
- 배치: Type별 그룹(5종), 각 그룹 안에서 가로 나열, gap 12px, 그룹 간 gap 32px

  ─── Elevated (12개) ────────────────────────────────────────────────────────

  Buttons/Elevated/Rounded/sm:
  · 높이 32dp, corner full (9999dp), 수평 패딩 16dp
  · bg: Surface Container Low, label: Primary (12sp medium)
  · Elevation Level 1 (그림자)
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/sm"

  Buttons/Elevated/Rounded/md:
  · 높이 40dp, corner full (9999dp), 수평 패딩 24dp
  · bg: Surface Container Low, label: Primary (14sp medium)
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/md"

  Buttons/Elevated/Rounded/lg:
  · 높이 48dp, corner full (9999dp), 수평 패딩 32dp
  · bg: Surface Container Low, label: Primary (16sp medium)
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/lg"

  Buttons/Elevated/Rect/sm:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Surface Container Low, label: Primary (12sp medium)
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/sm"

  Buttons/Elevated/Rect/md:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Surface Container Low, label: Primary (14sp medium)
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/md"

  Buttons/Elevated/Rect/lg:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Surface Container Low, label: Primary (16sp medium)
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/lg"

  Buttons/Elevated/Rounded/sm/Icon:
  · 높이 32dp, corner full, 수평 패딩 16dp
  · bg: Surface Container Low, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, 아이콘-레이블 gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/sm/Icon"

  Buttons/Elevated/Rounded/md/Icon:
  · 높이 40dp, corner full, 수평 패딩 24dp
  · bg: Surface Container Low, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/md/Icon"

  Buttons/Elevated/Rounded/lg/Icon:
  · 높이 48dp, corner full, 수평 패딩 32dp
  · bg: Surface Container Low, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rounded/lg/Icon"

  Buttons/Elevated/Rect/sm/Icon:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Surface Container Low, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/sm/Icon"

  Buttons/Elevated/Rect/md/Icon:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Surface Container Low, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/md/Icon"

  Buttons/Elevated/Rect/lg/Icon:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Surface Container Low, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · Elevation Level 1
  · 컴포넌트 이름: "Buttons/Elevated/Rect/lg/Icon"

  ─── Filled (12개) ──────────────────────────────────────────────────────────

  Buttons/Filled/Rounded/sm:
  · 높이 32dp, corner full (9999dp), 수평 패딩 16dp
  · bg: Primary, label: On-Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rounded/sm"

  Buttons/Filled/Rounded/md:
  · 높이 40dp, corner full (9999dp), 수평 패딩 24dp
  · bg: Primary, label: On-Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rounded/md"

  Buttons/Filled/Rounded/lg:
  · 높이 48dp, corner full (9999dp), 수평 패딩 32dp
  · bg: Primary, label: On-Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rounded/lg"

  Buttons/Filled/Rect/sm:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Primary, label: On-Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rect/sm"

  Buttons/Filled/Rect/md:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Primary, label: On-Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rect/md"

  Buttons/Filled/Rect/lg:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Primary, label: On-Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Filled/Rect/lg"

  Buttons/Filled/Rounded/sm/Icon:
  · 높이 32dp, corner full, 수평 패딩 16dp
  · bg: Primary, label: On-Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rounded/sm/Icon"

  Buttons/Filled/Rounded/md/Icon:
  · 높이 40dp, corner full, 수평 패딩 24dp
  · bg: Primary, label: On-Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rounded/md/Icon"

  Buttons/Filled/Rounded/lg/Icon:
  · 높이 48dp, corner full, 수평 패딩 32dp
  · bg: Primary, label: On-Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rounded/lg/Icon"

  Buttons/Filled/Rect/sm/Icon:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Primary, label: On-Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rect/sm/Icon"

  Buttons/Filled/Rect/md/Icon:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Primary, label: On-Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rect/md/Icon"

  Buttons/Filled/Rect/lg/Icon:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Primary, label: On-Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: On-Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Filled/Rect/lg/Icon"

  ─── FilledTonal (12개) ─────────────────────────────────────────────────────

  Buttons/FilledTonal/Rounded/sm:
  · 높이 32dp, corner full (9999dp), 수평 패딩 16dp
  · bg: Secondary Container, label: On-Secondary-Container (12sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/sm"

  Buttons/FilledTonal/Rounded/md:
  · 높이 40dp, corner full (9999dp), 수평 패딩 24dp
  · bg: Secondary Container, label: On-Secondary-Container (14sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/md"

  Buttons/FilledTonal/Rounded/lg:
  · 높이 48dp, corner full (9999dp), 수평 패딩 32dp
  · bg: Secondary Container, label: On-Secondary-Container (16sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/lg"

  Buttons/FilledTonal/Rect/sm:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Secondary Container, label: On-Secondary-Container (12sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/sm"

  Buttons/FilledTonal/Rect/md:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Secondary Container, label: On-Secondary-Container (14sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/md"

  Buttons/FilledTonal/Rect/lg:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Secondary Container, label: On-Secondary-Container (16sp medium)
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/lg"

  Buttons/FilledTonal/Rounded/sm/Icon:
  · 높이 32dp, corner full, 수평 패딩 16dp
  · bg: Secondary Container, label: On-Secondary-Container (12sp medium)
  · 좌측 아이콘 18dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/sm/Icon"

  Buttons/FilledTonal/Rounded/md/Icon:
  · 높이 40dp, corner full, 수평 패딩 24dp
  · bg: Secondary Container, label: On-Secondary-Container (14sp medium)
  · 좌측 아이콘 18dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/md/Icon"

  Buttons/FilledTonal/Rounded/lg/Icon:
  · 높이 48dp, corner full, 수평 패딩 32dp
  · bg: Secondary Container, label: On-Secondary-Container (16sp medium)
  · 좌측 아이콘 20dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rounded/lg/Icon"

  Buttons/FilledTonal/Rect/sm/Icon:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: Secondary Container, label: On-Secondary-Container (12sp medium)
  · 좌측 아이콘 18dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/sm/Icon"

  Buttons/FilledTonal/Rect/md/Icon:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: Secondary Container, label: On-Secondary-Container (14sp medium)
  · 좌측 아이콘 18dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/md/Icon"

  Buttons/FilledTonal/Rect/lg/Icon:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: Secondary Container, label: On-Secondary-Container (16sp medium)
  · 좌측 아이콘 20dp, 색상: On-Secondary-Container, gap 8dp
  · 컴포넌트 이름: "Buttons/FilledTonal/Rect/lg/Icon"

  ─── Outlined (12개) ────────────────────────────────────────────────────────

  Buttons/Outlined/Rounded/sm:
  · 높이 32dp, corner full (9999dp), 수평 패딩 16dp
  · bg: 투명, border: Outline 1dp, label: Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/sm"

  Buttons/Outlined/Rounded/md:
  · 높이 40dp, corner full (9999dp), 수평 패딩 24dp
  · bg: 투명, border: Outline 1dp, label: Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/md"

  Buttons/Outlined/Rounded/lg:
  · 높이 48dp, corner full (9999dp), 수평 패딩 32dp
  · bg: 투명, border: Outline 1dp, label: Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/lg"

  Buttons/Outlined/Rect/sm:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: 투명, border: Outline 1dp, label: Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rect/sm"

  Buttons/Outlined/Rect/md:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: 투명, border: Outline 1dp, label: Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rect/md"

  Buttons/Outlined/Rect/lg:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: 투명, border: Outline 1dp, label: Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Outlined/Rect/lg"

  Buttons/Outlined/Rounded/sm/Icon:
  · 높이 32dp, corner full, 수평 패딩 16dp
  · bg: 투명, border: Outline 1dp, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/sm/Icon"

  Buttons/Outlined/Rounded/md/Icon:
  · 높이 40dp, corner full, 수평 패딩 24dp
  · bg: 투명, border: Outline 1dp, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/md/Icon"

  Buttons/Outlined/Rounded/lg/Icon:
  · 높이 48dp, corner full, 수평 패딩 32dp
  · bg: 투명, border: Outline 1dp, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rounded/lg/Icon"

  Buttons/Outlined/Rect/sm/Icon:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: 투명, border: Outline 1dp, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rect/sm/Icon"

  Buttons/Outlined/Rect/md/Icon:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: 투명, border: Outline 1dp, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rect/md/Icon"

  Buttons/Outlined/Rect/lg/Icon:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: 투명, border: Outline 1dp, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Outlined/Rect/lg/Icon"

  ─── Text (12개) ────────────────────────────────────────────────────────────

  Buttons/Text/Rounded/sm:
  · 높이 32dp, corner full (9999dp), 수평 패딩 16dp
  · bg: 투명, label: Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rounded/sm"

  Buttons/Text/Rounded/md:
  · 높이 40dp, corner full (9999dp), 수평 패딩 24dp
  · bg: 투명, label: Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rounded/md"

  Buttons/Text/Rounded/lg:
  · 높이 48dp, corner full (9999dp), 수평 패딩 32dp
  · bg: 투명, label: Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rounded/lg"

  Buttons/Text/Rect/sm:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: 투명, label: Primary (12sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rect/sm"

  Buttons/Text/Rect/md:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: 투명, label: Primary (14sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rect/md"

  Buttons/Text/Rect/lg:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: 투명, label: Primary (16sp medium)
  · 컴포넌트 이름: "Buttons/Text/Rect/lg"

  Buttons/Text/Rounded/sm/Icon:
  · 높이 32dp, corner full, 수평 패딩 16dp
  · bg: 투명, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rounded/sm/Icon"

  Buttons/Text/Rounded/md/Icon:
  · 높이 40dp, corner full, 수평 패딩 24dp
  · bg: 투명, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rounded/md/Icon"

  Buttons/Text/Rounded/lg/Icon:
  · 높이 48dp, corner full, 수평 패딩 32dp
  · bg: 투명, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rounded/lg/Icon"

  Buttons/Text/Rect/sm/Icon:
  · 높이 32dp, corner 12dp, 수평 패딩 16dp
  · bg: 투명, label: Primary (12sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rect/sm/Icon"

  Buttons/Text/Rect/md/Icon:
  · 높이 40dp, corner 12dp, 수평 패딩 24dp
  · bg: 투명, label: Primary (14sp medium)
  · 좌측 아이콘 18dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rect/md/Icon"

  Buttons/Text/Rect/lg/Icon:
  · 높이 48dp, corner 12dp, 수평 패딩 32dp
  · bg: 투명, label: Primary (16sp medium)
  · 좌측 아이콘 20dp, 색상: Primary, gap 8dp
  · 컴포넌트 이름: "Buttons/Text/Rect/lg/Icon"


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Label only
  ElevatedButton(onPressed: () {}, child: Text('Label'))
  FilledButton(onPressed: () {}, child: Text('Label'))
  FilledButton.tonal(onPressed: () {}, child: Text('Label'))
  OutlinedButton(onPressed: () {}, child: Text('Label'))
  TextButton(onPressed: () {}, child: Text('Label'))

  // With icon
  ElevatedButton.icon(onPressed: () {}, icon: Icon(Icons.add), label: Text('Label'))
  FilledButton.icon(onPressed: () {}, icon: Icon(Icons.add), label: Text('Label'))
  FilledButton.tonalIcon(onPressed: () {}, icon: Icon(Icons.add), label: Text('Label'))
  OutlinedButton.icon(onPressed: () {}, icon: Icon(Icons.add), label: Text('Label'))
  TextButton.icon(onPressed: () {}, icon: Icon(Icons.add), label: Text('Label'))

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Filled/Rounded/md (기본)
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: Size(0, AppButtonSize.md), // 40dp
    shape: StadiumBorder(), // AppRadius.full
  ),
  child: const Text('저장'),
)

// Filled/Rect/md
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: Size(0, AppButtonSize.md), // 40dp
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(AppRadius.sm), // 12dp
    ),
  ),
  child: const Text('저장'),
)

// Filled/Rounded/sm
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: Size(0, AppButtonSize.sm), // 32dp
    shape: StadiumBorder(),
  ),
  child: const Text('저장'),
)

// Filled/Rounded/lg
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: Size(0, AppButtonSize.lg), // 48dp
    shape: StadiumBorder(),
  ),
  child: const Text('저장'),
)

// Filled/Rounded/md/Icon
FilledButton.icon(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: Size(0, AppButtonSize.md),
    shape: StadiumBorder(),
  ),
  icon: Icon(Icons.add, size: AppIconSize.sm), // 18dp
  label: const Text('추가'),
)

// FilledTonal / Outlined / Text — 동일 패턴
FilledButton.tonal(onPressed: () {}, child: const Text('임시저장'))
FilledButton.tonalIcon(onPressed: () {}, icon: Icon(Icons.save), label: const Text('임시저장'))
OutlinedButton(onPressed: () {}, child: const Text('취소'))
OutlinedButton.icon(onPressed: () {}, icon: Icon(Icons.close), label: const Text('취소'))
TextButton(onPressed: () {}, child: const Text('더보기'))
TextButton.icon(onPressed: () {}, icon: Icon(Icons.arrow_forward), label: const Text('더보기'))

// Disabled
FilledButton(onPressed: null, child: const Text('비활성'))
```
