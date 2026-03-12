[app]
title = GardenBabyTest
package.name = gardenbabytest
package.domain = com.wzz2333.test
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

[buildozer]
log_level = 2  # 强制输出完整日志，方便找错

[app:android]
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
android.archs = armeabi-v7a  # 单架构，绝无编译压力
android.permissions = INTERNET
android.use_aapt2 = False
android.ndk_api = 21  # 补全NDK API版本，避免版本不匹配

[app:requirements]
requirements = python3,kivy  # 只留最基础依赖，零冲突
