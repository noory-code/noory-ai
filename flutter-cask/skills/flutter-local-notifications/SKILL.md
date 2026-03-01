---
name: flutter-local-notifications
description: 로컬 푸시 알림 (스케줄, 반복, 커스텀)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [flutter_local_notifications, 로컬 알림, 스케줄 알림, notification, 예약 알림]
---

# Flutter Local Notifications

로컬 푸시 알림. 스케줄, 반복, 액션 버튼 지원.

---

## 설치

```bash
flutter pub add flutter_local_notifications
flutter pub add timezone  # 스케줄 알림용
```

## 플랫폼 설정

### iOS (ios/Runner/AppDelegate.swift)

```swift
if #available(iOS 10.0, *) {
  UNUserNotificationCenter.current().delegate = self as? UNUserNotificationCenterDelegate
}
```

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

---

## Quick Reference

### 초기화

```dart
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

final notifications = FlutterLocalNotificationsPlugin();

Future<void> initNotifications() async {
  const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
  const iosSettings = DarwinInitializationSettings(
    requestAlertPermission: true,
    requestBadgePermission: true,
    requestSoundPermission: true,
  );

  await notifications.initialize(
    InitializationSettings(android: androidSettings, iOS: iosSettings),
    onDidReceiveNotificationResponse: (response) {
      // 알림 탭 처리
      final payload = response.payload;
      if (payload != null) handleNotificationTap(payload);
    },
  );
}
```

### 즉시 알림

```dart
Future<void> showNotification({
  required int id,
  required String title,
  required String body,
  String? payload,
}) async {
  const androidDetails = AndroidNotificationDetails(
    'default_channel',
    '기본 알림',
    importance: Importance.high,
    priority: Priority.high,
  );
  const iosDetails = DarwinNotificationDetails();

  await notifications.show(
    id,
    title,
    body,
    NotificationDetails(android: androidDetails, iOS: iosDetails),
    payload: payload,
  );
}
```

### 스케줄 알림

```dart
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

// 초기화 시 timezone 설정
tz.initializeTimeZones();

Future<void> scheduleNotification({
  required int id,
  required String title,
  required String body,
  required DateTime scheduledTime,
}) async {
  await notifications.zonedSchedule(
    id,
    title,
    body,
    tz.TZDateTime.from(scheduledTime, tz.local),
    NotificationDetails(
      android: AndroidNotificationDetails('scheduled', '예약 알림'),
      iOS: DarwinNotificationDetails(),
    ),
    androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
    uiLocalNotificationDateInterpretation:
        UILocalNotificationDateInterpretation.absoluteTime,
  );
}
```

### 반복 알림

```dart
// 매일 특정 시간
await notifications.zonedSchedule(
  id,
  title,
  body,
  _nextInstanceOfTime(hour: 9, minute: 0),
  notificationDetails,
  androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
  uiLocalNotificationDateInterpretation:
      UILocalNotificationDateInterpretation.absoluteTime,
  matchDateTimeComponents: DateTimeComponents.time,  // 매일 반복
);

tz.TZDateTime _nextInstanceOfTime({required int hour, required int minute}) {
  final now = tz.TZDateTime.now(tz.local);
  var scheduled = tz.TZDateTime(tz.local, now.year, now.month, now.day, hour, minute);
  if (scheduled.isBefore(now)) {
    scheduled = scheduled.add(Duration(days: 1));
  }
  return scheduled;
}
```

### 알림 취소

```dart
// 특정 알림 취소
await notifications.cancel(id);

// 모든 알림 취소
await notifications.cancelAll();
```

### 권한 요청 (iOS)

```dart
Future<bool> requestPermission() async {
  final result = await notifications
      .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
      ?.requestPermissions(alert: true, badge: true, sound: true);
  return result ?? false;
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| iOS 권한 거부 | requestPermissions 호출 후 설정 안내 |
| Android 13+ | POST_NOTIFICATIONS 권한 요청 필요 |
| 스케줄 안됨 | timezone 초기화, SCHEDULE_EXACT_ALARM 권한 |
| 재부팅 후 사라짐 | RECEIVE_BOOT_COMPLETED + BroadcastReceiver |
| 백그라운드 안됨 | 포그라운드 서비스 또는 WorkManager 연동 |
