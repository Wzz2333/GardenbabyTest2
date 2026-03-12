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

[app:requirements]
requirements = python3,kivy
