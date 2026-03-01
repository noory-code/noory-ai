# 라우트 정의

go_router_builder를 사용한 타입 안전 라우트.

## 기본 라우트

```dart
import 'package:go_router/go_router.dart';

part 'routes.g.dart';

@TypedGoRoute<HomeRoute>(path: '/')
class HomeRoute extends GoRouteData {
  const HomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const HomeScreen();
  }
}
```

---

## Path 파라미터

```dart
@TypedGoRoute<UserRoute>(path: '/user/:userId')
class UserRoute extends GoRouteData {
  const UserRoute({required this.userId});

  final String userId;

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return UserScreen(userId: userId);
  }
}

// 사용
UserRoute(userId: 'user-123').go(context);
// URL: /user/user-123
```

---

## Query 파라미터

```dart
@TypedGoRoute<SearchRoute>(path: '/search')
class SearchRoute extends GoRouteData {
  const SearchRoute({this.query, this.page = 1});

  final String? query;
  final int page;

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return SearchScreen(query: query, page: page);
  }
}

// 사용
SearchRoute(query: 'flutter', page: 2).go(context);
// URL: /search?query=flutter&page=2
```

---

## 중첩 라우트

```dart
@TypedGoRoute<HomeRoute>(
  path: '/',
  routes: [
    TypedGoRoute<ProfileRoute>(
      path: 'profile/:userId',
      routes: [
        TypedGoRoute<ProfileEditRoute>(path: 'edit'),
      ],
    ),
  ],
)
class HomeRoute extends GoRouteData { ... }

class ProfileRoute extends GoRouteData {
  const ProfileRoute({required this.userId});
  final String userId;
  ...
}

class ProfileEditRoute extends GoRouteData {
  const ProfileEditRoute({required this.userId});
  final String userId;  // 부모 파라미터도 필요
  ...
}

// URL: /profile/user-123/edit
```

---

## Extra 데이터 (비직렬화)

```dart
@TypedGoRoute<DetailRoute>(path: '/detail')
class DetailRoute extends GoRouteData {
  const DetailRoute({required this.$extra});

  final MyObject $extra;  // $ prefix = extra

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return DetailScreen(data: $extra);
  }
}

// 사용 (URL에 포함 안됨, 딥링크 불가)
DetailRoute($extra: myObject).go(context);
```

---

## Enum 파라미터

```dart
enum Category { all, popular, recent }

@TypedGoRoute<CategoryRoute>(path: '/category/:category')
class CategoryRoute extends GoRouteData {
  const CategoryRoute({required this.category});

  final Category category;

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return CategoryScreen(category: category);
  }
}

// URL: /category/popular
```
