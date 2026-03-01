# Navigation

go vs push, redirect, and guard patterns.

## go vs push vs replace

| Method | Behavior | When to Use |
|--------|------|----------|
| `go()` | Replace the stack (navigate to a new path) | Tab switch, main screen |
| `push()` | Add to the stack | Detail screen, modal |
| `replace()` | Replace only the current screen | Navigate to home after login |

```dart
// go: /home -> /profile (stack: [/profile])
const ProfileRoute(userId: 'u1').go(context);

// push: /home -> /profile (stack: [/home, /profile])
const ProfileRoute(userId: 'u1').push(context);

// replace: /login -> /home (stack: [/home], no login screen on back navigation)
const HomeRoute().replace(context);
```

---

## Back Navigation

```dart
// go to the previous screen
context.pop();

// with a result value
context.pop(result);

// pop to a specific screen
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

    // not logged in and not on login page -> redirect to login
    if (!isLoggedIn && !isLoginRoute) {
      return '/login';
    }

    // logged in and on login page -> redirect to home
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
  refreshListenable: authNotifier,  // re-evaluate redirect whenever this changes
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
