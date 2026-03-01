---
name: flutter-quick-actions
description: Home screen Quick Actions (3D Touch / Long Press)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [quick_actions, home screen, 3D Touch, app icon, shortcut]
---

# Flutter Quick Actions

Shortcut menu that appears when long-pressing the app icon on the home screen.

---

## Installation

```bash
flutter pub add quick_actions
```

---

## Quick Reference

### Basic Setup

```dart
import 'package:quick_actions/quick_actions.dart';

final quickActions = QuickActions();

// initialize at app startup
void initQuickActions() {
  quickActions.initialize((type) {
    // type = the type value of the shortcutItem
    switch (type) {
      case 'action_search':
        navigateToSearch();
        break;
      case 'action_new':
        navigateToNew();
        break;
    }
  });

  // set quick action items
  quickActions.setShortcutItems([
    ShortcutItem(
      type: 'action_search',
      localizedTitle: 'Search',
      icon: 'icon_search',  // iOS: asset name, Android: drawable name
    ),
    ShortcutItem(
      type: 'action_new',
      localizedTitle: 'Create New',
      icon: 'icon_add',
    ),
  ]);
}
```

### iOS Icon Setup

```
ios/Runner/Assets.xcassets/
└── icon_search.imageset/
    ├── Contents.json
    └── icon_search.png (25x25)
```

### Android Icon Setup

```
android/app/src/main/res/drawable/
└── icon_search.xml (Vector Drawable)
```

### Cold Start Handling

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
        _initialAction = type;  // save before app starts
      }
    });
  }

  void _handleAction(String type) {
    // handle navigation
  }

  @override
  Widget build(BuildContext context) {
    // navigate to appropriate screen if _initialAction is set
    return MaterialApp(...);
  }
}
```

### Dynamic Updates

```dart
// change quick actions after login
void updateQuickActionsForUser(User user) {
  quickActions.setShortcutItems([
    ShortcutItem(
      type: 'action_profile',
      localizedTitle: user.name,
      icon: 'icon_profile',
    ),
    ShortcutItem(
      type: 'action_favorites',
      localizedTitle: 'Favorites',
      icon: 'icon_star',
    ),
  ]);
}

// clear on logout
void clearQuickActions() {
  quickActions.clearShortcutItems();
}
```

---

## Common Issues

| Situation | Solution |
|------|------|
| Icon not showing | Check iOS Asset Catalog and Android drawable |
| Cold start ignored | Save action before initialize, then process |
| Maximum 4 items | Both iOS and Android display up to 4 |
| Simulator not working | Test on real device |
