---
name: flutter-package-info
description: Retrieve package info such as app version and build number
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [package_info_plus, app version, build number, version info, package info]
---

# Flutter Package Info Plus

Retrieve app information such as version, build number, and package name.

---

## Installation

```bash
flutter pub add package_info_plus
```

---

## Quick Reference

### Basic Usage

```dart
import 'package:package_info_plus/package_info_plus.dart';

// get package info
final packageInfo = await PackageInfo.fromPlatform();

print(packageInfo.appName);        // app name
print(packageInfo.packageName);    // package name (com.example.app)
print(packageInfo.version);        // version (1.0.0)
print(packageInfo.buildNumber);    // build number (1)
print(packageInfo.buildSignature); // build signature (Android only)
```

### Cache at App Startup

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

// usage
Text('v${AppInfo.fullVersion}')  // v1.0.0+1
```

### Version Display Widget

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

### Update Check

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

### Settings Screen Example

```dart
ListTile(
  title: Text('App Info'),
  subtitle: FutureBuilder<PackageInfo>(
    future: PackageInfo.fromPlatform(),
    builder: (context, snapshot) {
      if (!snapshot.hasData) return Text('Loading...');
      return Text('${snapshot.data!.appName} v${snapshot.data!.version}');
    },
  ),
  trailing: Icon(Icons.chevron_right),
  onTap: () => showAboutDialog(context: context),
)
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Unexpected build number | Use pubspec.yaml version format: 1.0.0+1 |
| Not working on web | Web is not supported; use fallback values |
| Slow loading | Load once at app startup and cache the result |
| Test failure | Use a mock or an integration test |
