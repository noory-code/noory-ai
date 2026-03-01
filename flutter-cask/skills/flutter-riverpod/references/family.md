# Family Provider

A provider that accepts parameters. With riverpod_generator, parameters are handled automatically through function arguments.

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
      return await updateTodo(todoId, title);  // todoId is accessible here
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
// same parameters = same cached instance
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-1'));  // cache hit

// different parameters = separate instances
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-2'));  // separate instance
```
