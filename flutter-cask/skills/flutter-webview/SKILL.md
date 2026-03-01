---
name: flutter-webview
description: Display web pages inside the app (WebView)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [webview_flutter, webview, embedded web, webpage, browser]
---

# Flutter WebView

Display web pages inside the app. For external links, terms, and web content rendering.

---

## Installation

```bash
flutter pub add webview_flutter
```

## Platform Setup

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

### Basic Usage

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
      appBar: AppBar(title: Text('WebView')),
      body: WebViewWidget(controller: controller),
    );
  }
}
```

### Navigation Control

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
      // block specific URLs
      if (request.url.contains('blocked.com')) {
        return NavigationDecision.prevent;
      }
      return NavigationDecision.navigate;
    },
  ))
  ..loadRequest(Uri.parse(url));
```

### Back Navigation Handling

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

### Execute JavaScript

```dart
// run JS
await controller.runJavaScript('document.title');

// get JS result
final result = await controller.runJavaScriptReturningResult(
  'document.title',
);
print('Page title: $result');
```

### JavaScript to Flutter Communication

```dart
controller = WebViewController()
  ..addJavaScriptChannel(
    'FlutterChannel',
    onMessageReceived: (message) {
      print('Message from JS: ${message.message}');
      // handle message
    },
  )
  ..loadRequest(Uri.parse(url));

// call from web
// FlutterChannel.postMessage('Hello from JS');
```

### Load HTML String

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

### Loading Indicator

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

## Common Issues

| Situation | Solution |
|------|------|
| JS not working | setJavaScriptMode(unrestricted) |
| Back exits app | Check canGoBack() then call goBack() |
| HTTPS only | Android: usesCleartextTraffic, iOS: NSAppTransportSecurity |
| Keyboard covering content | resizeToAvoidBottomInset: true |
| Cookies not working | Use WebViewCookieManager |
