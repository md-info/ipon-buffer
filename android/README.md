# Ipon Buffer Android demo

The included development-signed APK is Ipon-Buffer-demo.apk. Rebuilding writes build/Ipon-Buffer-demo.apk. Requires Android 8.0+ and a current Android System WebView. It packages the app as a native WebView shell; the web UI, API, database and local AI continue running on the development computer. It is not a standalone offline app, a production release, or a GCash SDK/AAR. No public hosting is required for this USB-connected demo.

## Run on your phone

1. On the computer, from the project root, start `.venv\Scripts\python.exe scripts/demo_local_ai.py` and leave it running.
2. Connect an Android phone over USB. Enable Developer options and USB debugging, then authorize this computer on the phone.
3. From the project root run `powershell -ExecutionPolicy Bypass -File android/connect.ps1`.
4. The script forwards phone port 5173 to the computer, installs the APK and opens Ipon Buffer. Press Log in to start the synthetic demo.

USB port forwarding is required again after disconnect/restart. For an emulator, adb reverse works the same way. connect.ps1 expects exactly one authorized device. Installation, launch, login and safe system-bar bounds have been checked on Android 15 emulators, including a fresh Pixel 9 profile. Physical-device, photo-picker and broader keyboard/device coverage still require validation.

## Build

Uses existing JDK plus Android SDK platform 35, build-tools 35.0.0 and platform-tools. Set JAVA_HOME and ANDROID_SDK_ROOT to use another installation. Run `.venv\Scripts\python.exe scripts/build_android.py`. No Gradle, npm Android wrapper or additional app runtime dependency was added.

Build tools installed in the workspace fin/work/android-sdk directory. Google SDK license acceptance was explicitly authorized November 3, 2026. Command-line tool archive SHA-256 was checked against Google's download page. Build and signing verification succeeded; API minimum 26, target 35. Development keystore stays in ignored build/; do not use it for production distribution. Preserve it locally for compatible debug updates.

## Behavior

Photo uploads use Android's document picker without broad storage or camera permission. External HTTPS links open outside the app. The WebView accepts internal navigation only on 127.0.0.1:5173. HTTP cleartext is allowed only for that loopback address; there is no TLS-error bypass, location permission, native wallet bridge or automatic transfer access. Android Back closes applicable dialogs, otherwise follows web history or exits.

A standalone app requires a separate deployment decision: host the backend securely or port the backend and model runtime to Android. This demo does neither. All balances, merchant partnerships and rewards remain synthetic.
