---
name: flutter-package-info
description: 앱 버전, 빌드 번호 등 패키지 정보 조회
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [package_info_plus, 앱 버전, 빌드 번호, 버전 정보, 패키지 정보]
---

# Flutter Package Info Plus

앱 버전, 빌드 번호, 패키지명 등 앱 정보 조회.

---

## 설치

```bash
flutter pub add package_info_plus
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:package_info_plus/package_info_plus.dart';

// 패키지 정보 가져오기
final packageInfo = await PackageInfo.fromPlatform();

print(packageInfo.appName);        // 앱 이름
print(packageInfo.packageName);    // 패키지명 (com.example.app)
print(packageInfo.version);        // 버전 (1.0.0)
print(packageInfo.buildNumber);    // 빌드 번호 (1)
print(packageInfo.buildSignature); // 빌드 서명 (Android만)
```

### 앱 시작 시 캐싱

```dart
class AppInfo {
  static late PackageInfo _packageInfo;

  static Future<void> init() async {
    _packageInfo = await PackageInfo.fromPlatform();
  }

  static String get version => _packageInfo.version;
  static String get buildNumber => _packageInfo.buildNumber;
  static String get fullVersion => '${version}+${buildNumber}';
}

// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppInfo.init();
  runApp(MyApp());
}

// 사용
Text('v${AppInfo.fullVersion}')  // v1.0.0+1
```

### 버전 표시 위젯

```dart
class VersionText extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<PackageInfo>(
      future: PackageInfo.fromPlatform(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return SizedBox.shrink();
        final info = snapshot.data!;
        return Text(
          'v${info.version} (${info.buildNumber})',
          style: TextStyle(color: Colors.grey, fontSize: 12),
        );
      },
    );
  }
}
```

### 업데이트 체크

```dart
Future<bool> needsUpdate(String latestVersion) async {
  final info = await PackageInfo.fromPlatform();
  final current = info.version.split('.').map(int.parse).toList();
  final latest = latestVersion.split('.').map(int.parse).toList();

  for (int i = 0; i < 3; i++) {
    if (latest[i] > current[i]) return true;
    if (latest[i] < current[i]) return false;
  }
  return false;
}
```

### 설정 화면 예시

```dart
ListTile(
  title: Text('앱 정보'),
  subtitle: FutureBuilder<PackageInfo>(
    future: PackageInfo.fromPlatform(),
    builder: (context, snapshot) {
      if (!snapshot.hasData) return Text('로딩 중...');
      return Text('${snapshot.data!.appName} v${snapshot.data!.version}');
    },
  ),
  trailing: Icon(Icons.chevron_right),
  onTap: () => showAboutDialog(context: context),
)
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 빌드 번호 다름 | pubspec.yaml version 형식: 1.0.0+1 |
| Web에서 안됨 | Web 미지원, 폴백 값 사용 |
| 느린 로딩 | 앱 시작 시 한 번만 로드 후 캐싱 |
| 테스트 실패 | mock 또는 integration test 사용 |
