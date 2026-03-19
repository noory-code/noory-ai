# Changelog

## [1.2.4] — 2026-03-20

### Added
- `user-invocable: true` frontmatter to all 34 skills for explicit /command invocation

---

## [1.2.3] — 2026-03-20

### Fixed
- `update-flutter-skills`: metadata `type: composite` → `type: unit` (no sub-skill invocations)

---

## [1.2.2] — 2026-03-18

### Fixed
- Move `skills/template/` to `scaffold/template/` so unfilled placeholder is not loaded as an active skill
- Fix help skill description and body: "33 packages" → "32 packages"
- Translate all 35 SKILL.md changelog entries from Korean to English (`초기 릴리스` → `Initial release`)

---

## [1.2.1] — 2026-03-18

### Fixed
- **Cross-platform scripts**: replaced `check-skill-versions.sh` and `new-skill.sh` with Python equivalents for Windows/macOS/Linux compatibility

---

## [1.2.0] — 2026-03-07

### Improved
- `README.md`: added skill effectiveness metrics guidance and feedback mechanism
- `README.md`: added automated version staleness detection via CI guidance
- `update-flutter-skills/SKILL.md`: standardized reference documentation depth criteria
- Added `## Changelog` section to all 34 skill SKILL.md files for per-skill change tracking

---

## [1.0.0] - 2026-03-01

### Added
- Initial release with 33 Flutter package guide skills
- State management: flutter-riverpod
- Routing: flutter-go-router
- Firebase: analytics, crashlytics, messaging, performance
- Storage: flutter-hive, flutter-secure-storage
- UI: screenutil, shimmer, svg, google-fonts, pinput, quill
- Media: image-picker, cached-image, webview
- Notifications: flutter-local-notifications
- Location: flutter-geolocator
- Device: package-info, connectivity, quick-actions, share
- Monetization: admob, in-app-purchase
- Testing: unit, widget, integration
- Data: flutter-freezed
- Infra: flutter-fvm, flutter-melos, flutter-talker
- Meta: update-flutter-skills skill
