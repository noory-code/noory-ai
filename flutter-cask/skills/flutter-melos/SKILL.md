---
name: flutter-melos
description: Flutter monorepo management using Melos
metadata:
  version: "1.1.0"
  category: flutter-tool
  type: unit
  style: guide
  triggers: [melos, monorepo, multi-package, workspace]
---

# Flutter Melos

Flutter/Dart monorepo management tool. Handles inter-package dependencies, shared configuration, and bulk command execution.

---

## Installation

```bash
# global install
dart pub global activate melos

# add to project
dart pub add melos --dev
```

---

## Quick Reference

### Root pubspec.yaml

```yaml
name: my_project
publish_to: none

environment:
  sdk: ^3.6.0

workspace:
  - {project}_entities
  - {project}_core
  - {project}_app
  - {project}_admin

dev_dependencies:
  melos: ^6.0.0

melos:
  scripts:
    # code generation
    generate:
      run: melos exec -c 1 --depends-on build_runner -- dart run build_runner build --delete-conflicting-outputs
      description: Run build_runner in all packages

    # tests
    test:
      run: melos exec -- flutter test
      description: Run tests in all packages

    # format
    format:
      run: melos exec -- dart format .
      description: Format all packages

    # analyze
    analyze:
      run: melos exec -- dart analyze
      description: Analyze all packages
```

### Package pubspec.yaml

```yaml
name: {project}_entities
description: Domain entities

environment:
  sdk: ^3.6.0

resolution: workspace  # required!

dependencies:
  freezed_annotation: ^2.4.0

dev_dependencies:
  build_runner: ^2.4.0
  freezed: ^2.5.0
```

---

## Key Commands

| Command | Description |
|--------|------|
| `melos bootstrap` | Install dependencies + link packages |
| `melos clean` | Clean all packages |
| `melos exec -- <cmd>` | Run command in all packages |
| `melos run <script>` | Run a script |
| `melos list` | List packages |

### exec Options

```bash
# sequential execution (for build_runner, etc.)
melos exec -c 1 -- dart run build_runner build

# specific packages only
melos exec --scope="{project}_entities" -- flutter test

# packages with specific dependency
melos exec --depends-on="freezed" -- dart run build_runner build
```

---

## Folder Structure

```
{project}/
├── pubspec.yaml              # root (workspace definition)
├── melos.yaml                # (optional) separate config file
├── {project}_entities/
│   └── pubspec.yaml          # resolution: workspace
├── {project}_core/
│   └── pubspec.yaml
├── {project}_app/
│   └── pubspec.yaml
└── {project}_admin/
    └── pubspec.yaml
```

---

## Rules

| Item | Rule |
|------|------|
| **resolution** | `resolution: workspace` required in all packages |
| **workspace** | List all package paths in root pubspec.yaml |
| **version sync** | Manage shared dependencies from root |
| **scripts** | Define repetitive tasks as melos scripts |

---

## Common Mistakes

| Wrong | Correct |
|---|---|
| Missing `resolution: workspace` | Add to all packages |
| `flutter pub get` from root | Use `melos bootstrap` |
| Add dependency per package | Manage in root pubspec.yaml |
| build_runner without `-c 1` | `melos exec -c 1` (sequential execution) |

---

## References

- [Melos Official Docs](https://melos.invertase.dev/)
- [Getting Started](https://melos.invertase.dev/getting-started)
