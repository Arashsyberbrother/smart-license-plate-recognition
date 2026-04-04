<div dir="rtl">

# 📱 اپلیکیشن موبایل / دسکتاپ – تشخیص پلاک ایرانی

</div>

A Flutter application for Iranian license plate recognition.  
Builds as an **Android APK** (Android Studio or VS Code) and a **Windows EXE** (VS Code).

---

## Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Flutter SDK | ≥ 3.19 | https://flutter.dev/docs/get-started/install |
| Android Studio | ≥ Hedgehog | https://developer.android.com/studio |
| VS Code + Flutter extension | latest | https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter |
| Dart SDK | bundled with Flutter | — |

---

## Quick Start

```bash
# 1. Enter the mobile directory
cd mobile

# 2. Install Dart packages
flutter pub get

# 3. Start the FastAPI backend first (from the repo root):
#    docker-compose up -d
#    OR:  cd ../backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Run on a connected device / emulator
flutter run
```

---

## Build Android APK

### Option A – Android Studio
1. Open Android Studio → **Open** → select the `mobile/` folder.  
2. Let Gradle sync finish.  
3. **Build → Generate Signed Bundle/APK → APK → debug (for testing)**.  
4. The APK is placed in `build/app/outputs/flutter-apk/app-debug.apk`.

### Option B – Command Line (VS Code terminal or any terminal)
```bash
cd mobile
flutter build apk --debug          # debug APK (for testing on a device)
flutter build apk --release        # release APK (requires signing config)
```
APK output: `mobile/build/app/outputs/flutter-apk/app-release.apk`

---

## Build Windows EXE

```bash
# Enable Windows desktop support (one-time setup)
flutter config --enable-windows-desktop

# Add Windows platform files to this project (one-time per project)
flutter create --platforms windows .

# Build the EXE
flutter build windows --release
```
EXE output: `mobile/build/windows/runner/Release/plate_reader_app.exe`

> You can also open the folder in VS Code and press **F5** to run in debug mode on Windows.

---

## Server Configuration

On first launch the app connects to the Android emulator's localhost (`http://10.0.2.2:8000`).

**Testing on a physical Android device:**
1. Make sure your phone and PC are on the same Wi-Fi.
2. Find your PC's LAN IP (`ipconfig` on Windows, `ip a` on Linux).
3. Tap the ⚙️ gear icon in the app → enter `http://192.168.x.x:8000`.

---

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart                  # App entry point
│   ├── config/app_config.dart     # Runtime server URL setting
│   ├── models/plate_detection.dart
│   ├── screens/
│   │   ├── home_screen.dart       # Camera/gallery + result display
│   │   └── history_screen.dart    # Paginated history list
│   ├── services/api_service.dart  # HTTP calls to FastAPI backend
│   └── widgets/detection_result_card.dart
├── android/                       # Android platform project
├── windows/                       # Windows desktop platform files
└── pubspec.yaml
```

---

## Backend API Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/plates/detect` | POST | Upload image → get plate detection result |
| `/api/plates` | GET | Paginated history |
| `/api/plates/{id}` | DELETE | Delete a record |
| `/api/health` | GET | Health check |
