---
name: flutter-firebase-messaging
user-invocable: true
description: Firebase Cloud Messaging (FCM) push notifications
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_messaging, FCM, push notification, remote notification]
---

# Flutter Firebase Messaging

Receive remote push notifications via Firebase Cloud Messaging.

---

## Installation

```bash
flutter pub add firebase_messaging
flutter pub add flutter_local_notifications  # for foreground notification display
```

## Prerequisites

- Firebase project configured
- `flutterfire configure` has been run
- iOS: APNs certificate or key registered in Firebase

---

## Quick Reference

### Initialization and Permissions

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

Future<void> initFCM() async {
  final messaging = FirebaseMessaging.instance;

  // request permissions
  final settings = await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  if (settings.authorizationStatus == AuthorizationStatus.authorized) {
    print('Notification permission granted');
  }

  // get FCM token
  final token = await messaging.getToken();
  print('FCM Token: $token');

  // token refresh listener
  messaging.onTokenRefresh.listen((newToken) {
    // send new token to server
    updateTokenOnServer(newToken);
  });
}
```

### Setting Up Message Handlers

```dart
void setupMessageHandlers() {
  // foreground message
  FirebaseMessaging.onMessage.listen((message) {
    print('Foreground message: ${message.notification?.title}');
    // display as local notification
    showLocalNotification(message);
  });

  // notification tap from background
  FirebaseMessaging.onMessageOpenedApp.listen((message) {
    print('App opened via notification tap');
    handleNotificationTap(message);
  });
}

// launched via notification tap while the app was terminated
Future<void> checkInitialMessage() async {
  final message = await FirebaseMessaging.instance.getInitialMessage();
  if (message != null) {
    handleNotificationTap(message);
  }
}
```

### Background Handler

```dart
// main.dart (must be a top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Background message: ${message.messageId}');
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(MyApp());
}
```

### Display Foreground Notification

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
        'FCM Notifications',
        importance: Importance.high,
      ),
      iOS: DarwinNotificationDetails(),
    ),
    payload: message.data.toString(),
  );
}
```

### Topic Subscription

```dart
// subscribe to topic
await FirebaseMessaging.instance.subscribeToTopic('news');

// unsubscribe from topic
await FirebaseMessaging.instance.unsubscribeFromTopic('news');
```

### Handling Data Messages

```dart
FirebaseMessaging.onMessage.listen((message) {
  // notification field (notification message)
  final notification = message.notification;

  // data field (data message)
  final data = message.data;

  if (data['type'] == 'chat') {
    // handle chat message
    navigateToChat(data['chatId']);
  }
});
```

### Full Initialization Example

See [references/fcm-service.md](references/fcm-service.md)

---

## Common Issues

| Issue | Fix |
|------|------|
| No notification on iOS | Check that the APNs key/certificate is registered in Firebase |
| Not showing in foreground | Display using flutter_local_notifications |
| Token is null | Simulators are not supported; test on a real device |
| Background handler not called | Must be a top-level function with @pragma('vm:entry-point') |
| Data-only message | No system notification appears without a notification field |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
