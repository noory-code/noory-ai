# Family Provider

Provider that accepts parameters. In riverpod_generator, handled automatically via function arguments.

## Function-based (Simple)

```dart
@riverpod
String greeting(Ref ref, String name) {
  return 'Hello, $name';
}

// usage
final msg = ref.watch(greetingProvider('Kim'));
```

## Notifier-based

```dart
@riverpod
class TodoDetail extends _$TodoDetail {
  @override
  Future<Todo> build(String todoId) async {
    return await fetchTodo(todoId);
  }

  Future<void> update(String title) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      return await updateTodo(todoId, title);  // todoId accessible
    });
  }
}

// usage
final todo = ref.watch(todoDetailProvider('todo-123'));
```

---

## Multiple Parameters

```dart
@riverpod
Future<List<Post>> userPosts(
  Ref ref,
  String userId,
  {int page = 1, int limit = 20}
) async {
  return await fetchPosts(userId, page: page, limit: limit);
}

// usage
final posts = ref.watch(
  userPostsProvider('user-1', page: 2, limit: 10),
);
```

---

## Caching Behavior

```dart
// same parameter = same instance (cached)
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-1'));  // cache hit

// different parameter = different instance
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-2'));  // separate instance
```
