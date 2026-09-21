[app]
title = Quantum Oracle Dice
package.name = quantumoracledice
package.domain = org.quantumoracle
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,atlas,txt
version = 3.0.0
orientation = portrait
fullscreen = 0

# Google Play: nuevas apps requieren target Android 16 / API 36 desde 31-08-2026.
android.api = 36
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = False

# No sensores, micrófono, ubicación ni Bluetooth.
# Solo Kivy/Python para mantener el APK pequeño y estable.
requirements = python3,kivy

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
# Para builds modernos de python-for-android.
android.enable_androidx = True
android.enable_jetifier = True
