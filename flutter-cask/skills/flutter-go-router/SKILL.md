---
name: flutter-go-router
description: go_router + go_router_builder를 사용한 타입 안전 라우팅
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [go_router, routing, 라우팅, navigation, 네비게이션, deep link]
---

# Flutter Go Router

go_router_builder를 사용한 코드 생성 기반 타입 안전 라우팅.

---

## 설치

```bash
# 필수
flutter pub add go_router
flutter pub add dev:go_router_builder
flutter pub add dev:build_runner
```

## 코드 생성

```bash
# 일회성 빌드
dart run build_runner build --delete-conflicting-outputs

# 감시 모드
dart run build_runner watch -d
```

---

## Quick Reference

```dart
import 'package:go_router/go_router.dart';

part 'router.g.dart';

// 라우트 정의
@TypedGoRoute<HomeRoute>(
  path: '/',
  routes: [
    TypedGoRoute<ProfileRoute>(path: 'profile/:userId'),
    TypedGoRoute<SettingsRoute>(path: 'settings'),
  ],
)
class HomeRoute extends GoRouteData {
  const HomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const HomeScreen();
  }
}

class ProfileRoute extends GoRouteData {
  const ProfileRoute({required this.userId});

  final String userId;

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return ProfileScreen(userId: userId);
  }
}

class SettingsRoute extends GoRouteData {
  const SettingsRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const SettingsScreen();
  }
}

// GoRouter 설정
final router = GoRouter(routes: $appRoutes);

// App 설정
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(routerConfig: router);
  }
}
```

### 네비게이션

```dart
// 타입 안전 네비게이션
const HomeRoute().go(context);
ProfileRoute(userId: 'user-123').go(context);

// push (스택에 추가)
ProfileRoute(userId: 'user-123').push(context);

// replace (현재 화면 교체)
const SettingsRoute().replace(context);
```

### ShellRoute (BottomNav)

```dart
@TypedStatefulShellRoute<MainShellRoute>(
  branches: [
    TypedStatefulShellBranch<HomeBranch>(
      routes: [TypedGoRoute<HomeRoute>(path: '/home')],
    ),
    TypedStatefulShellBranch<SearchBranch>(
      routes: [TypedGoRoute<SearchRoute>(path: '/search')],
    ),
  ],
)
class MainShellRoute extends StatefulShellRouteData {
  const MainShellRoute();

  @override
  Widget builder(context, state, StatefulNavigationShell shell) {
    return Scaffold(
      body: shell,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: shell.currentIndex,
        onTap: shell.goBranch,
        items: [...],
      ),
    );
  }
}

class HomeBranch extends StatefulShellBranchData {
  const HomeBranch();
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 라우트 찾을 수 없음 | `$appRoutes` 사용 확인 |
| 파라미터 타입 에러 | 경로에 `:param` 형식 확인 |
| 빌드 에러 | `dart run build_runner build` 실행 |
| 딥링크 안됨 | AndroidManifest.xml / Info.plist 설정 |

---

## References

| 파일 | 내용 |
|------|------|
| [routes.md](references/routes.md) | GoRouteData, 파라미터, 쿼리스트링 |
| [navigation.md](references/navigation.md) | go vs push, redirect, guard |
| [shell-route.md](references/shell-route.md) | ShellRoute, 중첩 네비게이션 |
