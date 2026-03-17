# flutter-cask

> Flutter package guide skills for Claude Code — 32 packages, zero setup

Curated reference skills for Flutter development. Each skill gives Claude instant access to usage patterns, best practices, and code examples for the most common Flutter packages.

## Skills

| Category | Skills |
|----------|--------|
| State Management | `flutter-riverpod` |
| Routing | `flutter-go-router` |
| Firebase | `flutter-firebase-analytics`, `flutter-firebase-crashlytics`, `flutter-firebase-messaging`, `flutter-firebase-performance` |
| Storage | `flutter-hive`, `flutter-secure-storage` |
| UI | `flutter-screenutil`, `flutter-shimmer`, `flutter-svg`, `flutter-google-fonts`, `flutter-pinput`, `flutter-quill` |
| Media | `flutter-image-picker`, `flutter-cached-image`, `flutter-webview` |
| Notifications | `flutter-local-notifications` |
| Location | `flutter-geolocator` |
| Device | `flutter-package-info`, `flutter-connectivity`, `flutter-quick-actions`, `flutter-share` |
| Monetization | `flutter-admob`, `flutter-in-app-purchase` |
| Testing | `flutter-test-unit`, `flutter-test-widget`, `flutter-test-integration` |
| Data | `flutter-freezed` |
| Infra | `flutter-fvm`, `flutter-melos`, `flutter-talker` |
| Meta | `update-flutter-skills` |

## Installation

```
/plugin marketplace add noory-code/noory-ai
/plugin install flutter-cask
```

## Maintenance

### 자동 버전 체크

CI를 통해 매주 자동으로 스킬의 패키지 버전을 체크합니다:

- **스케줄**: 매주 월요일 오전 9시 (UTC)
- **동작**: pub.dev API를 통해 최신 버전과 문서화된 버전 비교
- **결과**: 업데이트가 필요한 경우 자동으로 이슈 생성
- **수동 실행**: GitHub Actions에서 workflow_dispatch로 언제든 실행 가능

버전 체크 스크립트: `scripts/check-skill-versions.sh`

## Feedback

이 프로젝트를 개선하는 데 도움을 주세요:

- **스킬 사용 피드백**: 어떤 스킬이 유용했는지 [알려주세요](../../issues/new?template=skill-usage-feedback.md)
- **새 스킬 요청**: 추가되었으면 하는 패키지가 있나요? [요청하기](../../issues/new?template=skill-request.md)

여러분의 피드백은 어떤 스킬에 집중해야 할지, 어떤 카테고리를 확장해야 할지 결정하는 데 도움이 됩니다. 자세한 내용은 [METRICS.md](METRICS.md)를 참고하세요.
