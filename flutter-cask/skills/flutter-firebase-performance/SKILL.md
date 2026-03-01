---
name: flutter-firebase-performance
description: Firebase Performance 앱 성능 모니터링
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_performance, performance, 성능 모니터링, 앱 속도, 트레이스]
---

# Flutter Firebase Performance

앱 시작 시간, 네트워크 요청, 커스텀 트레이스로 성능 모니터링.

---

## 설치

```bash
flutter pub add firebase_performance
```

## 사전 요구사항

- Firebase 프로젝트 설정 완료
- `flutterfire configure` 실행됨

---

## Quick Reference

### 초기화

```dart
import 'package:firebase_performance/firebase_performance.dart';

final performance = FirebasePerformance.instance;

// 수집 활성화 확인
final isEnabled = await performance.isPerformanceCollectionEnabled();
```

### 커스텀 트레이스

```dart
// 특정 작업 성능 측정
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

### HTTP 메트릭

```dart
// 네트워크 요청 측정
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

### Dio 인터셉터

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

### 화면 렌더링 성능

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

### 개발 모드 비활성화

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

## 주의사항

| 상황 | 해결 |
|------|------|
| 데이터 안보임 | 24시간 후 대시보드 확인 |
| 트레이스 안끝남 | finally에서 stop() 호출 필수 |
| 속성 제한 | 최대 5개 커스텀 속성 |
| 메트릭 제한 | 최대 32개 커스텀 메트릭 |
