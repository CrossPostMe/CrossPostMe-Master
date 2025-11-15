# iOS App Development Starter

Important: Work only from `C:\Users\johnd\Desktop\CROSSPOSTME-MASTER`; do not commit changes from any other clone or directory.

## Prerequisites

- Xcode installed (latest version recommended)
- macOS system
- Basic knowledge of Swift and iOS development

This folder is for your iOS app code. Recommended files to port or reference from your project:

- API models: `CrossPostMe/models.py`
- API client logic: `CrossPostMe/services/`, `CrossPostMe/routes/`
- Shared assets: `CrossPostMe/public/`, `app/frontend/src/components/`
- Documentation: `CrossPostMe/docs/`, `CrossPostMe/ENVIRONMENT_CONFIG.md`

For a cross-platform app, consider using Flutter or React Native. You can port logic from Python/JS to Swift (iOS) or Dart (Flutter).

Start by copying over:

- API specs and models
- Any reusable business logic
- UI assets (icons, images)
- Documentation

Let me know if you want a full starter template for Flutter or React Native!

## Getting started with the SwiftUI app

The `CrossPostMeApp` directory now contains a SwiftUI-first architecture with dedicated folders for Models, Networking, Services, Storage, ViewModels, and Views.

### Push notifications & background refresh

1. **Apple Developer setup**

- Enable *Push Notifications* and *Background Modes → Remote notifications + Background fetch* in the Xcode target capabilities.
- Register the background task identifier `com.crosspostme.app.refresh` under `BGTaskSchedulerPermittedIdentifiers` in `Info.plist`.

1. **Server hook**

- Implement `POST /api/device-tokens` to store the APNs token (sample payload `{ token, platform })`.
- Trigger APNs (e.g., via Supabase function or Azure Function) when new statuses or chat messages arrive.

1. **App behavior**

- `NotificationManager` now handles permission prompts, APNs token registration, local notifications, and background refresh fetches.

### AI assists (Azure OpenAI)

1. **Configuration**

    - Update `Resources/Config.plist` with `azureOpenAIBaseURL`, `azureOpenAIDeployment`, `azureOpenAIAPIVersion`, and set `azureOpenAIAPIKey` via secure secret management.
    - Never commit real keys; keep placeholders locally and load secrets through CI or environment injection.

1. **Feature behavior**

    - `AIComposeService` powers "Suggest reply" in the messaging tab and sentiment tagging for chat history.
    - The service calls Azure OpenAI chat completions with a lightweight prompt; adjust temperature/deployment as needed.

1. **Backend considerations**

    - Optionally expose a `/api/features` endpoint to toggle AI assists remotely.
    - Monitor usage/latency to stay within Azure quotas.

### Realtime Supabase sync

1. **Dependency**

    - Add the [`supabase-community/supabase-swift`](https://github.com/supabase-community/supabase-swift) package to the Xcode project (SPM).
    - Link it to the `CrossPostMeApp` target.

1. **Configuration**

    - Populate `supabaseURL` and `supabaseAnonKey` in `Resources/Config.plist`. Keep real keys out of source control by using local overrides or CI secrets.
    - Enable Realtime on the `status_entries` and `chat_messages` tables (or update the table names inside `SupabaseRealtimeCoordinator` to match your schema).

1. **Behavior**

    - `SupabaseRealtimeCoordinator` streams inserts/updates into the status feed and chat timeline; ViewModels merge records without requiring manual refresh.
    - The coordinator automatically disconnects on logout to conserve resources.

    ### Health analytics dashboard

    1. **Backend endpoints**

      - Expose `GET /api/health/history` returning an array of `{ timestamp, status, latency_ms }` records.
      - Expose `GET /api/health/incidents` returning incidents with `{ id, title, details, started_at, resolved_at, severity }`.

    1. **App behavior**

      - `HealthAnalyticsViewModel` fetches history/incidents concurrently and powers Swift Charts visualizations (latency trend, uptime %, incident log).
      - The new analytics cards live within `HealthView`; refreshing the page re-pulls both the realtime summary and historical analytics together.

    1. **Prerequisites**

      - Health charts rely on the built-in Swift Charts framework (iOS 16+). If you back-deploy earlier versions, add availability checks.
      - Ensure the backend timestamps are ISO-8601 strings so `Date` decoding succeeds.

    ### Listing assistant & growth recommendations

    1. **Endpoints**

      - `POST /api/assistant/generate/{platform}` now returns `suggestions`, `issues`, and a `processing_time_ms` diagnostic so the app can surface inline warnings before the user taps “Copy”.
      - `POST /api/assistant/generate/bulk` runs platform requests concurrently for much faster multi-channel drafts.
      - `GET /api/assistant/trending?days=14` bundles trending categories, peak posting windows, and actionable growth actions for the assistant home screen.

    1. **Analytics tie-in**

      - `GET /api/analytics/recommendations` produces prioritized growth playbooks (fix low-converting platforms, refresh stale listings, diversify catalog) and ships diagnostic notes when data is missing.
      - Display these recommendations inside the analytics tab or as cards beneath the listing assistant so users immediately see “what to do next.”

    1. **Handling issues**

      - Every assistant response includes structured `issues` (info/warning/critical). Surface these in SwiftUI as callouts and prompt the user to fix missing fields before copying.
      - If the backend reports `data_issues`, reflect that in the UI (e.g., “Connect Supabase to unlock trends”) rather than failing silently.

### Local development

- Requires macOS/Xcode (the `xcodebuild` tool is unavailable on Windows).
- Update `Resources/Config.plist` with your API base URL before running the simulator.
- The app persists auth tokens via Keychain and restores the last signed-in user.

```bash
# Run from the repository root on macOS
cd IOS/CrossPostMeApp
xcodebuild -scheme CrossPostMeApp -destination 'platform=iOS Simulator,name=iPhone 15' build
```

### Suggested CI step

Add a macOS runner in GitHub Actions to prevent regressions:

```yaml
name: ios-ci
on:
  pull_request:
    paths:
      - 'IOS/**'
jobs:
  build:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - name: Build & test
        run: |
          cd IOS/CrossPostMeApp
          xcodebuild -scheme CrossPostMeApp -destination 'platform=iOS Simulator,name=iPhone 15' test
```

This keeps the iOS codebase aligned with the backend contract while we continue fleshing out advanced messaging and health-monitoring features.
