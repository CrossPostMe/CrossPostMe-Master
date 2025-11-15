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
