# ShellRoute

Nested navigation and shared UI (BottomNavigationBar, etc.).

## Basic Structure

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

## BottomNavigationBar Integration

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

## Routes Outside Shell

Display as full screen without shell:

```dart
@TypedGoRoute<HomeRoute>(path: '/')
@TypedShellRoute<MainShellRoute>(
  routes: [
    TypedGoRoute<FeedRoute>(path: '/feed'),
    TypedGoRoute<ProfileRoute>(path: '/profile'),
  ],
)
// outside shell (full screen)
@TypedGoRoute<LoginRoute>(path: '/login')
@TypedGoRoute<OnboardingRoute>(path: '/onboarding')
```

---

## StatefulShellRoute (Preserve Tab State)

Preserve navigation state per tab:

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

### Using StatefulNavigationShell

```dart
class MainShell extends StatelessWidget {
  const MainShell({required this.navigationShell});
  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,  // navigator of the current branch
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: navigationShell.currentIndex,
        onTap: (index) => navigationShell.goBranch(index),
        items: const [...],
      ),
    );
  }
}
```
