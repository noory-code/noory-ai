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

Per-project Flutter SDK version management tool. Ensures the entire team uses the same version.

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
| `fvm install <version>` | Install SDK version |
| `fvm use <version>` | Set project version |
| `fvm list` | List installed versions |
| `fvm releases` | Available versions |
| `fvm global <version>` | Set global default version |
| `fvm doctor` | Diagnose environment |

### Install and Use a Version

```bash
# check available versions
fvm releases --channel stable

# install specific version
fvm install 3.24.0

# set version for project (creates .fvmrc)
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

**Include in Git**:
- `.fvmrc` - commit (share version)
- `.fvm/` - gitignore (local symbolic link)

**.gitignore**:
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
| **Pin version** | Specify project version with `.fvmrc` |
| **Team sync** | Must commit `.fvmrc` to Git |
| **IDE setup** | Use `.fvm/flutter_sdk` path |
| **CI/CD** | `fvm install && fvm flutter build` |

---

## Common Mistakes

| Wrong | Correct |
|---|---|
| Run `flutter doctor` directly | `fvm flutter doctor` |
| Commit entire `.fvm/` | Commit only `.fvmrc` |
| Use default VSCode SDK | Set `dart.flutterSdkPath` |
| No version specified | Must run `fvm use <version>` |

---

## References

- [FVM Official Docs](https://fvm.app/)
- [Getting Started](https://fvm.app/documentation/getting-started/overview)
