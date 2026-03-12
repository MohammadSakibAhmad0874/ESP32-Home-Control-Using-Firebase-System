# ApnaGhar Flutter App

Smart home control app for the ApnaGhar system.

## Getting Started

### Prerequisites
- [Flutter SDK](https://flutter.dev/docs/get-started/install/windows) installed
- Android Studio or VS Code with Flutter extension

### Setup

```bash
cd apnaghar_app
flutter pub get
flutter run
```

### Build APK

```bash
flutter build apk --release
```

The APK will be at: `build/app/outputs/flutter-apk/app-release.apk`

## Backend

Connected to: `https://esp32-home-control-using-firebase-system-production.up.railway.app`

Update the URL in `lib/config/api_config.dart` if the Railway URL changes.

## Features

- 🔑 **Login** — Device ID + password authentication
- 📋 **Claim** — 2-step device registration flow  
- 👑 **Admin** — Full device management panel
- 🏠 **Dashboard** — Real-time relay control via WebSocket
- ⏰ **Schedules** — Add/toggle/delete automations
- ⚡ **Power Usage** — kWh charts and cost breakdown in ₹
