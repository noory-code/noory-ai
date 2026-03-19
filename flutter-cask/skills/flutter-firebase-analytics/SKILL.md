---
name: flutter-firebase-analytics
user-invocable: true
description: Firebase Analytics event tracking and user analysis
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_analytics, analytics, event tracking, user analysis, GA]
---

# Flutter Firebase Analytics

Track user behavior with Firebase Analytics. Log events, screen views, and user properties.

---

## Installation

```bash
flutter pub add firebase_analytics
```

## Prerequisites

- Firebase project configured
- `flutterfire configure` has been run

---

## Quick Reference

### Initialization

```dart
import 'package:firebase_analytics/firebase_analytics.dart';

final analytics = FirebaseAnalytics.instance;
```

### Screen View Tracking

```dart
// log on each screen transition
await analytics.logScreenView(
  screenName: 'home_screen',
  screenClass: 'HomeScreen',
);

// integrate with GoRouter
GoRouter(
  observers: [FirebaseAnalyticsObserver(analytics: analytics)],
  routes: [...],
)
```

### Custom Events

```dart
// basic event
await analytics.logEvent(
  name: 'button_click',
  parameters: {
    'button_name': 'submit',
    'screen': 'login',
  },
);

// search event
await analytics.logSearch(searchTerm: 'whiskey');

// share event
await analytics.logShare(
  contentType: 'product',
  itemId: 'product_123',
  method: 'kakao',
);
```

### E-commerce Events

```dart
// view item
await analytics.logViewItem(
  currency: 'KRW',
  value: 50000,
  items: [
    AnalyticsEventItem(
      itemId: 'SKU_123',
      itemName: 'Whiskey',
      itemCategory: 'Liquor',
      price: 50000,
    ),
  ],
);

// add to cart
await analytics.logAddToCart(
  currency: 'KRW',
  value: 50000,
  items: [AnalyticsEventItem(itemId: 'SKU_123', itemName: 'Whiskey')],
);

// purchase complete
await analytics.logPurchase(
  currency: 'KRW',
  value: 50000,
  transactionId: 'TXN_123',
  items: [...],
);
```

### User Properties

```dart
// set user ID
await analytics.setUserId(id: 'user_123');

// custom property
await analytics.setUserProperty(
  name: 'membership_level',
  value: 'gold',
);

// reset on logout
await analytics.setUserId(id: null);
```

### Analytics Service Class

```dart
class AnalyticsService {
  final _analytics = FirebaseAnalytics.instance;

  Future<void> logLogin(String method) async {
    await _analytics.logLogin(loginMethod: method);
  }

  Future<void> logSignUp(String method) async {
    await _analytics.logSignUp(signUpMethod: method);
  }

  Future<void> setUser(String userId, {String? level}) async {
    await _analytics.setUserId(id: userId);
    if (level != null) {
      await _analytics.setUserProperty(name: 'level', value: level);
    }
  }
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Event not visible | Use DebugView (-FIRDebugEnabled); the dashboard has a 24-hour delay |
| Missing parameters | Key limit is 25 chars; value limit is 100 chars |
| Event name error | Use lowercase with underscores; cannot start with a number |
| Data not real-time | Only DebugView is real-time; the main dashboard has a delay |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
