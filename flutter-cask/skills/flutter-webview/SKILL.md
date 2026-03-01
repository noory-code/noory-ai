---
name: flutter-webview
description: 앱 내 웹페이지 표시 (WebView)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [webview_flutter, 웹뷰, 임베디드 웹, 웹페이지, 브라우저]
---

# Flutter WebView

앱 내에서 웹페이지 표시. 외부 링크, 약관, 웹 콘텐츠 렌더링.

---

## 설치

```bash
flutter pub add webview_flutter
```

## 플랫폼 설정

### iOS (ios/Runner/Info.plist)

```xml
<key>io.flutter.embedded_views_preview</key>
<true/>
```

### Android (android/app/build.gradle)

```groovy
android {
    defaultConfig {
        minSdkVersion 19
    }
}
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:webview_flutter/webview_flutter.dart';

class WebViewPage extends StatefulWidget {
  final String url;
  const WebViewPage({required this.url});

  @override
  State<WebViewPage> createState() => _WebViewPageState();
}

class _WebViewPageState extends State<WebViewPage> {
  late final WebViewController controller;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('웹뷰')),
      body: WebViewWidget(controller: controller),
    );
  }
}
```

### 네비게이션 제어

```dart
controller = WebViewController()
  ..setJavaScriptMode(JavaScriptMode.unrestricted)
  ..setNavigationDelegate(NavigationDelegate(
    onProgress: (progress) {
      setState(() => _progress = progress);
    },
    onPageStarted: (url) {
      setState(() => _isLoading = true);
    },
    onPageFinished: (url) {
      setState(() => _isLoading = false);
    },
    onNavigationRequest: (request) {
      // 특정 URL 차단
      if (request.url.contains('blocked.com')) {
        return NavigationDecision.prevent;
      }
      return NavigationDecision.navigate;
    },
  ))
  ..loadRequest(Uri.parse(url));
```

### 뒤로가기 처리

```dart
@override
Widget build(BuildContext context) {
  return PopScope(
    canPop: false,
    onPopInvokedWithResult: (didPop, result) async {
      if (didPop) return;
      if (await controller.canGoBack()) {
        await controller.goBack();
      } else {
        Navigator.of(context).pop();
      }
    },
    child: WebViewWidget(controller: controller),
  );
}
```

### JavaScript 실행

```dart
// JS 실행
await controller.runJavaScript('document.title');

// JS 결과 받기
final result = await controller.runJavaScriptReturningResult(
  'document.title',
);
print('페이지 제목: $result');
```

### JavaScript → Flutter 통신

```dart
controller = WebViewController()
  ..addJavaScriptChannel(
    'FlutterChannel',
    onMessageReceived: (message) {
      print('JS에서 받은 메시지: ${message.message}');
      // 메시지 처리
    },
  )
  ..loadRequest(Uri.parse(url));

// 웹에서 호출
// FlutterChannel.postMessage('Hello from JS');
```

### HTML 문자열 로드

```dart
await controller.loadHtmlString('''
<!DOCTYPE html>
<html>
  <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
  <body>
    <h1>Hello WebView</h1>
  </body>
</html>
''');
```

### 로딩 인디케이터

```dart
@override
Widget build(BuildContext context) {
  return Stack(
    children: [
      WebViewWidget(controller: controller),
      if (_isLoading)
        Center(child: CircularProgressIndicator()),
    ],
  );
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| JS 안됨 | setJavaScriptMode(unrestricted) |
| 뒤로가기 앱 종료 | canGoBack() 체크 후 goBack() |
| HTTPS만 됨 | Android: usesCleartextTraffic, iOS: NSAppTransportSecurity |
| 키보드 가림 | resizeToAvoidBottomInset: true |
| 쿠키 안됨 | WebViewCookieManager 사용 |
