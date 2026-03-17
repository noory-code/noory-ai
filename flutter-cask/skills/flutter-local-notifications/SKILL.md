---
name: flutter-local-notifications
description: Local push notifications (scheduled, repeating, custom)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [flutter_local_notifications, local notification, scheduled notification, notification]
---

# Flutter Local Notifications

Local push notifications with support for scheduling, repeating, and action buttons.

---

## Installation

```bash
flutter pub add flutter_local_notifications
flutter pub add timezone  # for scheduled notifications
```

## Platform Setup

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

### Initialization

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
      // handle notification tap
      final payload = response.payload;
      if (payload != null) handleNotificationTap(payload);
    },
  );
}
```

### Immediate Notification

```dart
Future<void> showNotification({
  required int id,
  required String title,
  required String body,
  String? payload,
}) async {
  const androidDetails = AndroidNotificationDetails(
    'default_channel',
    'Default Notifications',
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

### Scheduled Notification

```dart
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

// initialize timezone data at startup
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
      android: AndroidNotificationDetails('scheduled', 'Scheduled Notifications'),
      iOS: DarwinNotificationDetails(),
    ),
    androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
    uiLocalNotificationDateInterpretation:
        UILocalNotificationDateInterpretation.absoluteTime,
  );
}
```

### Repeating Notification

```dart
// every day at a specific time
await notifications.zonedSchedule(
  id,
  title,
  body,
  _nextInstanceOfTime(hour: 9, minute: 0),
  notificationDetails,
  androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
  uiLocalNotificationDateInterpretation:
      UILocalNotificationDateInterpretation.absoluteTime,
  matchDateTimeComponents: DateTimeComponents.time,  // repeat daily
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

### Cancel Notifications

```dart
// cancel a specific notification
await notifications.cancel(id);

// cancel all notifications
await notifications.cancelAll();
```

### Request Permission (iOS)

```dart
Future<bool> requestPermission() async {
  final result = await notifications
      .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
      ?.requestPermissions(alert: true, badge: true, sound: true);
  return result ?? false;
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| iOS permission denied | Call requestPermissions, then guide the user to Settings |
| Android 13+ | Must request the POST_NOTIFICATIONS permission at runtime |
| Schedule not working | Initialize timezone data and check SCHEDULE_EXACT_ALARM permission |
| Notification disappears after reboot | Add RECEIVE_BOOT_COMPLETED + BroadcastReceiver |
| Not working in background | Use a foreground service or WorkManager integration |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
