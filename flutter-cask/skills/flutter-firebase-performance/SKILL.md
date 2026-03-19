---
name: flutter-firebase-performance
user-invocable: true
description: Firebase Performance app performance monitoring
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_performance, performance, performance monitoring, app speed, trace]
---

# Flutter Firebase Performance

Monitor app startup time, network requests, and custom traces.

---

## Installation

```bash
flutter pub add firebase_performance
```

## Prerequisites

- Firebase project configured
- `flutterfire configure` has been run

---

## Quick Reference

### Initialization

```dart
import 'package:firebase_performance/firebase_performance.dart';

final performance = FirebasePerformance.instance;

// check if collection is enabled
final isEnabled = await performance.isPerformanceCollectionEnabled();
```

### Custom Traces

```dart
// measure the performance of a specific operation
Future<void> loadData() async {
  final trace = performance.newTrace('load_data');
  await trace.start();

  try {
    final data = await fetchData();
    trace.setMetric('item_count', data.length);
    trace.putAttribute('source', 'api');
  } finally {
    await trace.stop();
  }
}
```

### HTTP Metrics

```dart
// measure a network request
Future<void> fetchWithMetric(String url) async {
  final metric = performance.newHttpMetric(url, HttpMethod.Get);
  await metric.start();

  try {
    final response = await http.get(Uri.parse(url));
    metric.httpResponseCode = response.statusCode;
    metric.responseContentType = response.headers['content-type'];
    metric.responsePayloadSize = response.bodyBytes.length;
  } finally {
    await metric.stop();
  }
}
```

### Dio Interceptor

```dart
class PerformanceInterceptor extends Interceptor {
  final _metrics = <String, HttpMetric>{};

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final metric = FirebasePerformance.instance.newHttpMetric(
      options.uri.toString(),
      _getMethod(options.method),
    );
    metric.start();
    _metrics[options.hashCode.toString()] = metric;
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final metric = _metrics.remove(response.requestOptions.hashCode.toString());
    metric?.httpResponseCode = response.statusCode;
    metric?.stop();
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final metric = _metrics.remove(err.requestOptions.hashCode.toString());
    metric?.stop();
    handler.next(err);
  }

  HttpMethod _getMethod(String method) {
    switch (method.toUpperCase()) {
      case 'GET': return HttpMethod.Get;
      case 'POST': return HttpMethod.Post;
      case 'PUT': return HttpMethod.Put;
      case 'DELETE': return HttpMethod.Delete;
      default: return HttpMethod.Get;
    }
  }
}
```

### Screen Rendering Performance

```dart
class ScreenTraceWidget extends StatefulWidget {
  final String screenName;
  final Widget child;

  const ScreenTraceWidget({
    required this.screenName,
    required this.child,
  });

  @override
  State<ScreenTraceWidget> createState() => _ScreenTraceWidgetState();
}

class _ScreenTraceWidgetState extends State<ScreenTraceWidget> {
  Trace? _trace;

  @override
  void initState() {
    super.initState();
    _startTrace();
  }

  Future<void> _startTrace() async {
    _trace = FirebasePerformance.instance.newTrace('screen_${widget.screenName}');
    await _trace?.start();
  }

  @override
  void dispose() {
    _trace?.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
```

### Disable in Development Mode

```dart
void main() async {
  await Firebase.initializeApp();

  if (kDebugMode) {
    await FirebasePerformance.instance.setPerformanceCollectionEnabled(false);
  }

  runApp(MyApp());
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Data not visible | Check the dashboard after 24 hours |
| Trace not ending | Always call stop() in a finally block |
| Attribute limit exceeded | Maximum 5 custom attributes per trace |
| Metric limit exceeded | Maximum 32 custom metrics per trace |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
