---
name: flutter-quick-actions
description: 홈스크린 Quick Action (3D Touch/Long Press)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [quick_actions, 홈스크린, 3D Touch, 앱 아이콘, 바로가기]
---

# Flutter Quick Actions

홈스크린 앱 아이콘 꾹 누르면 나오는 바로가기 메뉴.

---

## 설치

```bash
flutter pub add quick_actions
```

---

## Quick Reference

### 기본 설정

```dart
import 'package:quick_actions/quick_actions.dart';

final quickActions = QuickActions();

// 앱 시작 시 초기화
void initQuickActions() {
  quickActions.initialize((type) {
    // type = shortcutItem의 type 값
    switch (type) {
      case 'action_search':
        navigateToSearch();
        break;
      case 'action_new':
        navigateToNew();
        break;
    }
  });

  // Quick Action 아이템 설정
  quickActions.setShortcutItems([
    ShortcutItem(
      type: 'action_search',
      localizedTitle: '검색',
      icon: 'icon_search',  // iOS: Asset명, Android: drawable명
    ),
    ShortcutItem(
      type: 'action_new',
      localizedTitle: '새로 만들기',
      icon: 'icon_add',
    ),
  ]);
}
```

### iOS 아이콘 설정

```
ios/Runner/Assets.xcassets/
└── icon_search.imageset/
    ├── Contents.json
    └── icon_search.png (25x25)
```

### Android 아이콘 설정

```
android/app/src/main/res/drawable/
└── icon_search.xml (Vector Drawable)
```

### 콜드 스타트 처리

```dart
class MyApp extends StatefulWidget {
  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final quickActions = QuickActions();
  String? _initialAction;

  @override
  void initState() {
    super.initState();
    quickActions.initialize((type) {
      if (mounted) {
        _handleAction(type);
      } else {
        _initialAction = type;  // 앱 시작 전이면 저장
      }
    });
  }

  void _handleAction(String type) {
    // 네비게이션 처리
  }

  @override
  Widget build(BuildContext context) {
    // _initialAction이 있으면 해당 화면으로 이동
    return MaterialApp(...);
  }
}
```

### 동적 업데이트

```dart
// 로그인 후 Quick Action 변경
void updateQuickActionsForUser(User user) {
  quickActions.setShortcutItems([
    ShortcutItem(
      type: 'action_profile',
      localizedTitle: user.name,
      icon: 'icon_profile',
    ),
    ShortcutItem(
      type: 'action_favorites',
      localizedTitle: '즐겨찾기',
      icon: 'icon_star',
    ),
  ]);
}

// 로그아웃 시 초기화
void clearQuickActions() {
  quickActions.clearShortcutItems();
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 아이콘 안보임 | iOS: Asset Catalog, Android: drawable 확인 |
| 콜드 스타트 무시됨 | initialize 전 액션 저장 후 처리 |
| 최대 4개 제한 | iOS/Android 모두 4개까지만 표시 |
| 시뮬레이터 안됨 | 실제 기기에서 테스트 |
