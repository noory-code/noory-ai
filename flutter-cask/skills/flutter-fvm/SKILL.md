---
name: flutter-fvm
description: Flutter SDK version management using FVM
metadata:
  version: "1.1.0"
  category: flutter-tool
  type: unit
  style: guide
  triggers: [fvm, Flutter version, SDK version, version management]
---

# Flutter FVM

Per-project Flutter SDK version management. Ensures the entire team uses the same Flutter version.

---

## Installation

```bash
# macOS (Homebrew)
brew tap leoafarias/fvm
brew install fvm

# or pub global
dart pub global activate fvm
```

---

## Quick Reference

### Key Commands

| Command | Description |
|--------|------|
| `fvm install <version>` | Install an SDK version |
| `fvm use <version>` | Set the project version |
| `fvm list` | List installed versions |
| `fvm releases` | List available versions |
| `fvm global <version>` | Set the global default version |
| `fvm doctor` | Diagnose the environment |

### Install and Use a Version

```bash
# check available versions
fvm releases --channel stable

# install a specific version
fvm install 3.24.0

# set the version for this project (creates .fvmrc)
fvm use 3.24.0

# run Flutter commands via FVM
fvm flutter doctor
fvm dart --version
```

---

## .fvmrc Configuration

```json
{
  "flutter": "3.24.0",
  "flavors": {}
}
```

**Git policy:**
- `.fvmrc` — commit this file to share the version with the team
- `.fvm/` — add to .gitignore (local symlink only)

**.gitignore:**
```
.fvm/flutter_sdk
```

---

## VSCode Setup

`.vscode/settings.json`:
```json
{
  "dart.flutterSdkPath": ".fvm/flutter_sdk"
}
```

---

## Rules

| Item | Rule |
|------|------|
| **Pin version** | Always specify the project version in `.fvmrc` |
| **Team sync** | Commit `.fvmrc` to Git |
| **IDE setup** | Point the IDE to `.fvm/flutter_sdk` |
| **CI/CD** | Run `fvm install && fvm flutter build` |

---

## Common Mistakes

| Wrong | Correct |
|---|---|
| Run `flutter doctor` directly | `fvm flutter doctor` |
| Commit the entire `.fvm/` directory | Commit only `.fvmrc` |
| Use the default VSCode SDK path | Set `dart.flutterSdkPath` in settings |
| No version pinned | Always run `fvm use <version>` |

---

## References

- [FVM Official Docs](https://fvm.app/)
- [Getting Started](https://fvm.app/documentation/getting-started/overview)
