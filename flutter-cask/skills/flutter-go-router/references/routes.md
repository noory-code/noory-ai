# Route Definitions

Type-safe routes using go_router_builder.

## Basic Route

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

## Path Parameters

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

// usage
UserRoute(userId: 'user-123').go(context);
// URL: /user/user-123
```

---

## Query Parameters

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

// usage
SearchRoute(query: 'flutter', page: 2).go(context);
// URL: /search?query=flutter&page=2
```

---

## Nested Routes

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
  final String userId;  // parent parameter also required
  ...
}

// URL: /profile/user-123/edit
```

---

## Extra Data (Non-serializable)

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

// usage (not included in URL, deep link not possible)
DetailRoute($extra: myObject).go(context);
```

---

## Enum Parameters

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
