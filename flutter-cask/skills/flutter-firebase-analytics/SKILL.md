---
name: flutter-firebase-analytics
description: Firebase Analytics 이벤트 추적 및 사용자 분석
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_analytics, analytics, 이벤트 추적, 사용자 분석, GA]
---

# Flutter Firebase Analytics

Firebase Analytics로 사용자 행동 추적. 이벤트, 화면 조회, 사용자 속성 기록.

---

## 설치

```bash
flutter pub add firebase_analytics
```

## 사전 요구사항

- Firebase 프로젝트 설정 완료
- `flutterfire configure` 실행됨

---

## Quick Reference

### 초기화

```dart
import 'package:firebase_analytics/firebase_analytics.dart';

final analytics = FirebaseAnalytics.instance;
```

### 화면 조회 추적

```dart
// 화면 전환 시 로깅
await analytics.logScreenView(
  screenName: 'home_screen',
  screenClass: 'HomeScreen',
);

// GoRouter와 연동
GoRouter(
  observers: [FirebaseAnalyticsObserver(analytics: analytics)],
  routes: [...],
)
```

### 커스텀 이벤트

```dart
// 기본 이벤트
await analytics.logEvent(
  name: 'button_click',
  parameters: {
    'button_name': 'submit',
    'screen': 'login',
  },
);

// 검색 이벤트
await analytics.logSearch(searchTerm: '위스키');

// 공유 이벤트
await analytics.logShare(
  contentType: 'product',
  itemId: 'product_123',
  method: 'kakao',
);
```

### 이커머스 이벤트

```dart
// 상품 조회
await analytics.logViewItem(
  currency: 'KRW',
  value: 50000,
  items: [
    AnalyticsEventItem(
      itemId: 'SKU_123',
      itemName: '위스키',
      itemCategory: '주류',
      price: 50000,
    ),
  ],
);

// 장바구니 추가
await analytics.logAddToCart(
  currency: 'KRW',
  value: 50000,
  items: [AnalyticsEventItem(itemId: 'SKU_123', itemName: '위스키')],
);

// 구매 완료
await analytics.logPurchase(
  currency: 'KRW',
  value: 50000,
  transactionId: 'TXN_123',
  items: [...],
);
```

### 사용자 속성

```dart
// 사용자 ID 설정
await analytics.setUserId(id: 'user_123');

// 커스텀 속성
await analytics.setUserProperty(
  name: 'membership_level',
  value: 'gold',
);

// 초기화 (로그아웃)
await analytics.setUserId(id: null);
```

### Analytics 서비스 클래스

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

## 주의사항

| 상황 | 해결 |
|------|------|
| 이벤트 안보임 | DebugView 사용 (-FIRDebugEnabled), 24시간 대기 |
| 파라미터 누락 | key 25자, value 100자 제한 |
| 이벤트명 에러 | 소문자+밑줄, 숫자 시작 금지 |
| 실시간 안됨 | DebugView만 실시간, 대시보드는 지연 |
