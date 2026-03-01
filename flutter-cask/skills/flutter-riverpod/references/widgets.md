# Riverpod Widgets

Widgets for using providers in Flutter.

## ProviderScope

Provides the provider state store at the top of the widget tree.

```dart
void main() {
  runApp(
    ProviderScope(
      // overrides (useful for testing)
      overrides: [
        authRepositoryProvider.overrideWithValue(MockAuthRepository()),
      ],
      child: MyApp(),
    ),
  );
}
```

---

## ConsumerWidget

A StatelessWidget that can read from providers.

```dart
class HomePage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userProvider);

    return Text('Hello, ${user.name}');
  }
}
```

---

## ConsumerStatefulWidget

Use this when local widget state is also needed.

```dart
class HomePage extends ConsumerStatefulWidget {
  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  @override
  void initState() {
    super.initState();
    // ref is available here
    ref.read(analyticsProvider).logPageView('home');
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(userProvider);
    return Text('Hello, ${user.name}');
  }
}
```

---

## Consumer

Rebuilds only a specific portion of the widget tree.

```dart
class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Header(),  // not rebuilt
        Consumer(
          builder: (context, ref, child) {
            final count = ref.watch(counterProvider);
            return Text('Count: $count');  // only this rebuilds
          },
        ),
        const Footer(),  // not rebuilt
      ],
    );
  }
}
```

---

## ref Methods

| Method | Purpose | Triggers Rebuild |
|--------|------|--------|
| `ref.watch(p)` | Subscribe to a value and rebuild on change | Yes |
| `ref.read(p)` | Read a value once (use in event handlers) | No |
| `ref.listen(p, cb)` | Execute a callback on change | No |

### Usage Examples

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // watch: use inside build
    final count = ref.watch(counterProvider);

    // listen: side effects such as showing a snackbar
    ref.listen(errorProvider, (prev, next) {
      if (next != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next)),
        );
      }
    });

    return TextButton(
      // read: use inside event handlers
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      child: Text('Count: $count'),
    );
  }
}
```

---

## select (Partial Subscription)

Subscribe to a specific field only to avoid unnecessary rebuilds.

```dart
// full subscription (rebuilds on any change to the user)
final user = ref.watch(userProvider);

// partial subscription (rebuilds only when the name changes)
final name = ref.watch(userProvider.select((u) => u.name));
```
