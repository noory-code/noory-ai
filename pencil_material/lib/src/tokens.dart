// Design Tokens — Spacing / Radius / Elevation / Icon Size / Opacity / Thickness
// 펜슬 material-design-guide.lib.pen 의 Design Tokens 테마 토큰과 1:1 대응.
//
// 사용법:
//   padding: EdgeInsets.all(AppSpacing.base)
//   borderRadius: BorderRadius.circular(AppRadius.md)
//   elevation: AppElevation.level1
//   size: AppIconSize.md
//   color.withValues(alpha: AppOpacity.hover)

abstract final class AppSpacing {
  /// 0 dp — 간격 없음
  static const double zero = 0;

  /// 2 dp — 아이콘 내부 패딩, 칩 내부 최소 간격
  static const double xs = 2;

  /// 4 dp — 아이콘 gap, 칩 내부
  static const double sm = 4;

  /// 8 dp — 리스트 아이템 간격, 아이콘 gap
  static const double md = 8;

  /// 12 dp — 기본 패딩, 카드 내부 패딩
  static const double base = 12;

  /// 16 dp — 콘텐츠 여백, 섹션 내 간격
  static const double lg = 16;

  /// 20 dp — 버튼 수평 패딩
  static const double xl = 20;

  /// 24 dp — 카드 패딩, 섹션 간격
  static const double x2l = 24;

  /// 32 dp — 섹션 간 간격
  static const double x3l = 32;

  /// 40 dp — 페이지 좌우 패딩, 섹션 헤더 간격
  static const double x4l = 40;
}

abstract final class AppRadius {
  /// 0 dp — shape/none (DataTable, 직각 이미지)
  static const double none = 0;

  /// 8 dp — shape/extra-small (Chip, Tooltip, 입력 필드)
  static const double xs = 8;

  /// 12 dp — shape/small (소형 Card, Menu, Snackbar)
  static const double sm = 12;

  /// 16 dp — shape/medium (Card, Dialog)
  static const double md = 16;

  /// 20 dp — shape/large (BottomSheet, Drawer)
  static const double lg = 20;

  /// 28 dp — shape/extra-large (FAB, 대형 Card)
  static const double xl = 28;

  /// 9999 dp — shape/full — pill 형태 (Button, Chip, ExtendedFAB)
  static const double full = 9999;
}

abstract final class AppElevation {
  /// Level 0 — 0 dp (Scaffold 배경)
  static const double level0 = 0;

  /// Level 1 — 1 dp (Card, NavigationDrawer)
  static const double level1 = 1;

  /// Level 2 — 3 dp (FAB resting, DropdownMenu)
  static const double level2 = 3;

  /// Level 3 — 6 dp (FAB hover, NavigationBar)
  static const double level3 = 6;

  /// Level 4 — 8 dp (Scrim 영역)
  static const double level4 = 8;

  /// Level 5 — 12 dp (Dialog, BottomSheet, Modal)
  static const double level5 = 12;
}

abstract final class AppIconSize {
  /// 18 dp — 버튼 Leading/Trailing 아이콘, 인라인 텍스트 옆
  static const double sm = 18;

  /// 20 dp — 작은 IconButton, Chip 아이콘
  static const double base = 20;

  /// 24 dp — 기본값 (NavigationBar, AppBar, ListTile)
  static const double md = 24;

  /// 36 dp — 강조 아이콘, 빈 상태 화면 보조
  static const double lg = 36;

  /// 48 dp — 빈 상태 화면 메인, 온보딩
  static const double xl = 48;
}

abstract final class AppOpacity {
  /// 0.38 — Disabled 상태 콘텐츠 (텍스트, 아이콘)
  static const double disabled = 0.38;

  /// 0.08 — Hovered State Layer
  static const double hover = 0.08;

  /// 0.12 — Focused State Layer
  static const double focus = 0.12;

  /// 0.12 — Pressed State Layer
  static const double pressed = 0.12;

  /// 0.16 — Dragged State Layer
  static const double dragged = 0.16;
}

abstract final class AppButtonSize {
  /// 32 dp — Small 버튼 높이
  static const double sm = 32;

  /// 40 dp — Medium 버튼 높이 (M3 기본)
  static const double md = 40;

  /// 48 dp — Large 버튼 높이
  static const double lg = 48;
}

abstract final class AppThickness {
  /// 0.5 dp — 보조 Divider, 얇은 구분선
  static const double thin = 0.5;

  /// 1 dp — 기본 Divider, OutlinedButton, TextField outline
  static const double md = 1;

  /// 2 dp — Focused TextField, Focused OutlinedButton, 강조 border
  static const double thick = 2;
}
