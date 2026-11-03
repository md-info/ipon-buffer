$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$sdkRoot = Join-Path (Split-Path (Split-Path $projectRoot -Parent) -Parent) 'work/android-sdk'
$adbPath = Join-Path $sdkRoot 'platform-tools/adb.exe'
if ($env:ANDROID_SDK_ROOT) { $adbPath = Join-Path $env:ANDROID_SDK_ROOT 'platform-tools/adb.exe' }
& $adbPath devices
& $adbPath reverse tcp:5173 tcp:5173
if ($LASTEXITCODE -ne 0) { throw 'Connect one phone with USB debugging enabled and authorize this computer.' }
& $adbPath install -r (Join-Path $PSScriptRoot 'build/Ipon-Buffer-demo.apk')
if ($LASTEXITCODE -ne 0) { throw 'APK installation failed.' }
& $adbPath shell am start -n com.iponbuffer.app/.MainActivity
