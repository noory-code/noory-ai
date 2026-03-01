# FCM 전체 초기화 예시

```dart
class FCMService {
  Future<void> init() async {
    await _requestPermission();
    await _getToken();
    _setupHandlers();
    await _checkInitialMessage();
  }

  Future<void> _requestPermission() async {
    await FirebaseMessaging.instance.requestPermission();
  }

  Future<void> _getToken() async {
    final token = await FirebaseMessaging.instance.getToken();
    await saveTokenToServer(token);
  }

  void _setupHandlers() {
    FirebaseMessaging.onMessage.listen(showLocalNotification);
    FirebaseMessaging.onMessageOpenedApp.listen(handleTap);
  }

  Future<void> _checkInitialMessage() async {
    final message = await FirebaseMessaging.instance.getInitialMessage();
    if (message != null) handleTap(message);
  }
}
```
