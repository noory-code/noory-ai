# 네비게이션

go vs push, redirect, guard 패턴.

## go vs push vs replace

| 메서드 | 동작 | 사용 시점 |
|--------|------|----------|
| `go()` | 스택 교체 (새 경로로 이동) | 탭 전환, 메인 화면 |
| `push()` | 스택에 추가 | 상세 화면, 모달 |
| `replace()` | 현재 화면만 교체 | 로그인 후 홈 이동 |

```dart
// go: /home → /profile (스택: [/profile])
const ProfileRoute(userId: 'u1').go(context);

// push: /home → /profile (스택: [/home, /profile])
const ProfileRoute(userId: 'u1').push(context);

// replace: /login → /home (스택: [/home], 뒤로가기 시 login 없음)
const HomeRoute().replace(context);
```

---

## 뒤로가기

```dart
// 이전 화면으로
context.pop();

// 결과값과 함께
context.pop(result);

// 특정 화면까지 pop
context.go('/');  // 홈으로 이동 (스택 초기화)
```

---

## Redirect (리다이렉트)

```dart
final router = GoRouter(
  routes: $appRoutes,
  redirect: (context, state) {
    final isLoggedIn = authNotifier.isLoggedIn;
    final isLoginRoute = state.matchedLocation == '/login';

    // 비로그인 + 로그인 페이지 아님 → 로그인으로
    if (!isLoggedIn && !isLoginRoute) {
      return '/login';
    }

    // 로그인 + 로그인 페이지 → 홈으로
    if (isLoggedIn && isLoginRoute) {
      return '/';
    }

    return null;  // 리다이렉트 없음
  },
);
```

---

## Refresh (상태 변경 감지)

```dart
final router = GoRouter(
  routes: $appRoutes,
  redirect: (context, state) { ... },
  refreshListenable: authNotifier,  // 변경 시 redirect 재평가
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
    if (!isAdmin) return '/';  // 관리자 아니면 홈으로
    return null;
  }

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const AdminScreen();
  }
}
```

---

## 에러 페이지

```dart
final router = GoRouter(
  routes: $appRoutes,
  errorBuilder: (context, state) {
    return ErrorScreen(error: state.error);
  },
);
```

---

## 현재 경로 확인

```dart
// 현재 위치
final location = GoRouterState.of(context).matchedLocation;

// 쿼리 파라미터
final params = GoRouterState.of(context).uri.queryParameters;
```
