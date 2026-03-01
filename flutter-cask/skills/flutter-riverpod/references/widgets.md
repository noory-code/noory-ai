# Riverpod Widgets

Widgets for using Providers in Flutter.

## ProviderScope

Provides the Provider state store at the top of the app.

```dart
void main() {
  runApp(
    ProviderScope(
      // overrides (for testing)
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

StatelessWidget that uses Providers.

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

When state is required.

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

Rebuild only a portion of the widget tree.

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

| Method | Purpose | Rebuild |
|--------|------|--------|
| `ref.watch(p)` | Subscribe to value + rebuild on change | Yes |
| `ref.read(p)` | Read value once (event handlers) | No |
| `ref.listen(p, cb)` | Execute callback on change | No |

### Usage Examples

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // watch: use in build
    final count = ref.watch(counterProvider);

    // listen: side effects (snackbar, etc.)
    ref.listen(errorProvider, (prev, next) {
      if (next != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next)),
        );
      }
    });

    return TextButton(
      // read: in event handlers
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      child: Text('Count: $count'),
    );
  }
}
```

---

## select (Partial Subscription)

Subscribe to specific fields only to prevent unnecessary rebuilds.

```dart
// full subscription (rebuilds on any user change)
final user = ref.watch(userProvider);

// partial subscription (rebuilds only on name change)
final name = ref.watch(userProvider.select((u) => u.name));
```
