# ShellRoute

중첩 네비게이션과 공통 UI (BottomNavigationBar 등).

## 기본 구조

```dart
@TypedShellRoute<MainShellRoute>(
  routes: [
    TypedGoRoute<HomeRoute>(path: '/home'),
    TypedGoRoute<SearchRoute>(path: '/search'),
    TypedGoRoute<ProfileRoute>(path: '/profile'),
  ],
)
class MainShellRoute extends ShellRouteData {
  const MainShellRoute();

  @override
  Widget builder(BuildContext context, GoRouterState state, Widget navigator) {
    return MainShell(child: navigator);
  }
}

class MainShell extends StatelessWidget {
  const MainShell({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: const MainBottomNav(),
    );
  }
}
```

---

## BottomNavigationBar 연동

```dart
class MainBottomNav extends StatelessWidget {
  const MainBottomNav();

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;

    return BottomNavigationBar(
      currentIndex: _getIndex(location),
      onTap: (index) => _onTap(context, index),
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
        BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
        BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
      ],
    );
  }

  int _getIndex(String location) {
    if (location.startsWith('/home')) return 0;
    if (location.startsWith('/search')) return 1;
    if (location.startsWith('/profile')) return 2;
    return 0;
  }

  void _onTap(BuildContext context, int index) {
    switch (index) {
      case 0:
        const HomeRoute().go(context);
      case 1:
        const SearchRoute().go(context);
      case 2:
        const ProfileRoute().go(context);
    }
  }
}
```

---

## Shell 밖 라우트

Shell 없이 전체 화면으로 표시:

```dart
@TypedGoRoute<HomeRoute>(path: '/')
@TypedShellRoute<MainShellRoute>(
  routes: [
    TypedGoRoute<FeedRoute>(path: '/feed'),
    TypedGoRoute<ProfileRoute>(path: '/profile'),
  ],
)
// Shell 밖 (전체 화면)
@TypedGoRoute<LoginRoute>(path: '/login')
@TypedGoRoute<OnboardingRoute>(path: '/onboarding')
```

---

## StatefulShellRoute (탭별 상태 유지)

각 탭의 네비게이션 상태를 유지:

```dart
@TypedStatefulShellRoute<MainShellRoute>(
  branches: [
    TypedStatefulShellBranch<HomeBranch>(
      routes: [
        TypedGoRoute<HomeRoute>(path: '/home'),
        TypedGoRoute<HomeDetailRoute>(path: '/home/detail'),
      ],
    ),
    TypedStatefulShellBranch<SearchBranch>(
      routes: [
        TypedGoRoute<SearchRoute>(path: '/search'),
      ],
    ),
  ],
)
class MainShellRoute extends StatefulShellRouteData {
  const MainShellRoute();

  @override
  Widget builder(
    BuildContext context,
    GoRouterState state,
    StatefulNavigationShell navigationShell,
  ) {
    return MainShell(navigationShell: navigationShell);
  }
}

class HomeBranch extends StatefulShellBranchData {
  const HomeBranch();
}

class SearchBranch extends StatefulShellBranchData {
  const SearchBranch();
}
```

### StatefulNavigationShell 사용

```dart
class MainShell extends StatelessWidget {
  const MainShell({required this.navigationShell});
  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,  // 현재 branch의 navigator
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: navigationShell.currentIndex,
        onTap: (index) => navigationShell.goBranch(index),
        items: const [...],
      ),
    );
  }
}
```
