# iOS App Development Starter

Important: Work only from `C:\Users\johnd\Desktop\CROSSPOSTME-MASTER`; do not commit changes from any other clone or directory.

## Prerequisites

- Xcode installed (latest version recommended)
- macOS system
- Basic knowledge of Swift and iOS development

This folder now contains a native SwiftUI replica of the Android CrossPostMe app.

## Project Overview

- Project name: `CrossPostMeiOS`
- Target platforms: iPhone + iPad (iOS 17 minimum)
- Architecture: SwiftUI with a lightweight observable view model + mock data seed
- Navigation: `NavigationStack` with quick-action buttons similar to the Android Compose navigation graph

### Implemented Screens

- **Dashboard** – Displays high-level marketplace metrics, action shortcuts, and the current ads list.
- **Create Ad** – Form for drafting ads, mirroring Android field validation and auto-renew toggle.
- **Login / Register** – Simple credential forms with inline validation and simulated loading states.
- **Platform Management** – Shows connected marketplaces with quick status updates.
- **Messaging & Leads** – Lists latest inquiries with relative timestamps.

The Swift data models (`Ad`, `DashboardStats`, `PlatformAccount`, `LeadMessage`) and mock data align with the Kotlin models in `Android/app/src/main/java/com/crosspostme/data/model` to keep parity with the backend contract.

## Requirements

- Xcode 15.2 or newer (macOS Sonoma or later recommended)
- iOS 17 simulator or device

## Getting Started

1. Copy or clone this repository to a macOS machine with Xcode installed.
2. Open `IOS/CrossPostMeiOS/CrossPostMeiOS.xcodeproj` in Xcode.
3. Select the `CrossPostMeiOS` scheme and choose an iPhone/iPad simulator (or a connected device).
4. Press **Run** (`⌘R`). The app boots directly to the dashboard screen.

> **Note:** Placeholder App Icon slots are defined but do not include artwork yet. Add your PNG assets to `Assets.xcassets/AppIcon.appiconset` before shipping to TestFlight/App Store to silence build warnings.

## Customisation Tips

- Update `MockData` in `CrossPostMeiOS/Models.swift` to wire real API data once backend integration is ready.
- Replace the simulated login/register delays in `Screens.swift` with real authentication flows when the API is available.
- Use `AdsViewModel` methods as the entry point for networking or database persistence—right now they simply update the in-memory collections.

## Testing & QA

- A full Xcode build succeeds with the SwiftUI sources provided here.
- Run `codacy_cli_analyze` (see root instructions) after modifying Swift files to keep style issues in check.
- UI previews live in each SwiftUI view file; use the canvas for rapid iteration.

If you need Flutter/React Native alternatives or deeper API integration scaffolding, reach out! The current SwiftUI implementation is intentionally lean so you can iterate quickly.
