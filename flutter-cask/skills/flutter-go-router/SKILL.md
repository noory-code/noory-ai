---
name: flutter-go-router
user-invocable: true
description: Type-safe routing using go_router + go_router_builder
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [go_router, routing, navigation, deep link]
---

# Flutter Go Router

Code-generation-based type-safe routing using go_router_builder.

---

## Installation

```bash
# required
flutter pub add go_router
flutter pub add dev:go_router_builder
flutter pub add dev:build_runner
```

## Code Generation

```bash
# one-time build
dart run build_runner build --delete-conflicting-outputs

# watch mode
dart run build_runner watch -d
```

---

## Quick Reference

```dart
import 'package:go_router/go_router.dart';

part 'router.g.dart';

// route definition
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

// GoRouter setup
final router = GoRouter(routes: $appRoutes);

// App setup
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(routerConfig: router);
  }
}
```

### Navigation

```dart
// type-safe navigation
const HomeRoute().go(context);
ProfileRoute(userId: 'user-123').go(context);

// push (add to stack)
ProfileRoute(userId: 'user-123').push(context);

// replace (replace current screen)
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

## Common Issues

| Issue | Fix |
|------|------|
| Route not found | Verify that `$appRoutes` is used in the GoRouter |
| Parameter type error | Check the `:param` format in the path |
| Build error | Run `dart run build_runner build` |
| Deep link not working | Configure AndroidManifest.xml and Info.plist |

---

## References

| File | Description |
|------|------|
| [routes.md](references/routes.md) | GoRouteData, parameters, query strings |
| [navigation.md](references/navigation.md) | go vs push, redirect, guard |
| [shell-route.md](references/shell-route.md) | ShellRoute, nested navigation |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
