# Changelog

## [1.2.6] — 2026-07-12

### Fixed
- `.github/workflows/check-skill-versions.yml`: script call and PR-trigger path pointed at deleted `scripts/check-skill-versions.sh`; now call `python3 scripts/check-skill-versions.py` (the CI job was broken since the 1.2.1 Python migration)
- `CONTRIBUTING.md`: stale "35개 스킬" count corrected to 34 (32 package skills + `help` + `update-flutter-skills`)
- `CONTRIBUTING.md`: replaced two vague "필요시" ("if needed") phrases with explicit conditions
- `CONTRIBUTING.md`: SKILL.md structure section now links to `scaffold/template/SKILL.md` as the canonical template instead of duplicating it in prose
- `README.md`: skills table now lists the `help` skill under Meta (previously undocumented)
- `METRICS.md`: removed the "액션 아이템" checkbox list (status tracker embedded in doc body); action items now tracked in GitHub Issues

---

## [1.2.5] — 2026-03-20

### Fixed
- `help`: sync metadata version from "1.0.0" to "1.1.0"

---

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
