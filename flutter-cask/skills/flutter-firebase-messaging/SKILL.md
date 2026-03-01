---
name: flutter-firebase-messaging
description: Firebase Cloud Messaging (FCM) 푸시 알림
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_messaging, FCM, 푸시 알림, remote notification, 원격 알림]
---

# Flutter Firebase Messaging

Firebase Cloud Messaging으로 원격 푸시 알림 수신.

---

## 설치

```bash
flutter pub add firebase_messaging
flutter pub add flutter_local_notifications  # 포그라운드 알림 표시용
```

## 사전 요구사항

- Firebase 프로젝트 설정 완료
- `flutterfire configure` 실행됨
- iOS: APNs 인증서 또는 키 등록

---

## Quick Reference

### 초기화 및 권한

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

Future<void> initFCM() async {
  final messaging = FirebaseMessaging.instance;

  // 권한 요청
  final settings = await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  if (settings.authorizationStatus == AuthorizationStatus.authorized) {
    print('알림 권한 허용됨');
  }

  // FCM 토큰 가져오기
  final token = await messaging.getToken();
  print('FCM Token: $token');

  // 토큰 갱신 리스너
  messaging.onTokenRefresh.listen((newToken) {
    // 서버에 새 토큰 전송
    updateTokenOnServer(newToken);
  });
}
```

### 메시지 핸들러 설정

```dart
void setupMessageHandlers() {
  // 포그라운드 메시지
  FirebaseMessaging.onMessage.listen((message) {
    print('포그라운드 메시지: ${message.notification?.title}');
    // 로컬 알림으로 표시
    showLocalNotification(message);
  });

  // 백그라운드에서 알림 탭
  FirebaseMessaging.onMessageOpenedApp.listen((message) {
    print('알림 탭으로 앱 열림');
    handleNotificationTap(message);
  });
}

// 앱 종료 상태에서 알림 탭으로 실행
Future<void> checkInitialMessage() async {
  final message = await FirebaseMessaging.instance.getInitialMessage();
  if (message != null) {
    handleNotificationTap(message);
  }
}
```

### 백그라운드 핸들러

```dart
// main.dart (최상위 함수로 정의)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('백그라운드 메시지: ${message.messageId}');
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(MyApp());
}
```

### 포그라운드 알림 표시

```dart
Future<void> showLocalNotification(RemoteMessage message) async {
  final notification = message.notification;
  if (notification == null) return;

  await FlutterLocalNotificationsPlugin().show(
    notification.hashCode,
    notification.title,
    notification.body,
    NotificationDetails(
      android: AndroidNotificationDetails(
        'fcm_channel',
        'FCM 알림',
        importance: Importance.high,
      ),
      iOS: DarwinNotificationDetails(),
    ),
    payload: message.data.toString(),
  );
}
```

### 토픽 구독

```dart
// 토픽 구독
await FirebaseMessaging.instance.subscribeToTopic('news');

// 토픽 구독 해제
await FirebaseMessaging.instance.unsubscribeFromTopic('news');
```

### 데이터 메시지 처리

```dart
FirebaseMessaging.onMessage.listen((message) {
  // notification 필드 (알림 메시지)
  final notification = message.notification;

  // data 필드 (데이터 메시지)
  final data = message.data;

  if (data['type'] == 'chat') {
    // 채팅 메시지 처리
    navigateToChat(data['chatId']);
  }
});
```

### 전체 초기화 예시

→ [references/fcm-service.md](references/fcm-service.md) 참조

---

## 주의사항

| 상황 | 해결 |
|------|------|
| iOS 알림 안옴 | APNs 키/인증서 Firebase 등록 확인 |
| 포그라운드 안보임 | flutter_local_notifications로 표시 |
| 토큰 null | 시뮬레이터 미지원 (실기기 테스트) |
| 백그라운드 핸들러 | 최상위 함수 + @pragma 필수 |
| 데이터만 메시지 | notification 없으면 시스템 알림 안뜸 |
