[app]
title = MyApp
package.name = myapp
package.domain = com.test
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

[buildozer]
log_level = 2

[app:android]
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = armeabi-v7a
android.permissions = INTERNET
android.use_aapt2 = False
android.ndk_api = 21
# 为了指定 SDK/NDK 路径（如果自动检测有问题时）
android.sdk_path = ~/.buildozer/android/platform/android-sdk
# 可选：指定 NDK 路径（如果自己装的）
# android.ndk_path = ~/.buildozer/android/platform/android-ndk-*

# 指定 Build-Tools/平台版本（可根据 Workflow里sdkmanager对应版本添加）
android.minapi = 21
android.ndk_version = 25b

[app:requirements]
requirements = python3,kivy


