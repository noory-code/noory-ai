# Navigation

go vs push, redirect, guard patterns.

## go vs push vs replace

| Method | Behavior | When to Use |
|--------|------|----------|
| `go()` | Replace stack (navigate to new path) | Tab switch, main screen |
| `push()` | Add to stack | Detail screen, modal |
| `replace()` | Replace current screen only | Navigate to home after login |

```dart
// go: /home -> /profile (stack: [/profile])
const ProfileRoute(userId: 'u1').go(context);

// push: /home -> /profile (stack: [/home, /profile])
const ProfileRoute(userId: 'u1').push(context);

// replace: /login -> /home (stack: [/home], no login on back navigation)
const HomeRoute().replace(context);
```

---

## Back Navigation

```dart
// go to previous screen
context.pop();

// with result value
context.pop(result);

// pop to specific screen
context.go('/');  // navigate to home (reset stack)
```

---

## Redirect

```dart
final router = GoRouter(
  routes: $appRoutes,
  redirect: (context, state) {
    final isLoggedIn = authNotifier.isLoggedIn;
    final isLoginRoute = state.matchedLocation == '/login';

    // not logged in + not on login page -> go to login
    if (!isLoggedIn && !isLoginRoute) {
      return '/login';
    }

    // logged in + on login page -> go to home
    if (isLoggedIn && isLoginRoute) {
      return '/';
    }

    return null;  // no redirect
  },
);
```

---

## Refresh (Detect State Changes)

```dart
final router = GoRouter(
  routes: $appRoutes,
  redirect: (context, state) { ... },
  refreshListenable: authNotifier,  // re-evaluate redirect on change
);
```

---

## Route-level Redirect

```dart
@TypedGoRoute<AdminRoute>(path: '/admin')
class AdminRoute extends GoRouteData {
  const AdminRoute();

  @override
  String? redirect(BuildContext context, GoRouterState state) {
    final isAdmin = context.read<AuthNotifier>().isAdmin;
    if (!isAdmin) return '/';  // redirect to home if not admin
    return null;
  }

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const AdminScreen();
  }
}
```

---

## Error Page

```dart
final router = GoRouter(
  routes: $appRoutes,
  errorBuilder: (context, state) {
    return ErrorScreen(error: state.error);
  },
);
```

---

## Check Current Path

```dart
// current location
final location = GoRouterState.of(context).matchedLocation;

// query parameters
final params = GoRouterState.of(context).uri.queryParameters;
```
