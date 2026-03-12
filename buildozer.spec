[app]
# 基础信息（必须全英文，无中文/空格）
title = GardenBaby
package.name = gardenbaby
package.domain = com.wzz2333.test
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# 核心构建配置（关键：只保留 armeabi-v7a，放弃 arm64-v8a）
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
android.archs = armeabi-v7a  # 只保留单架构，避免本地编译卡死
android.permissions = INTERNET

# 依赖（初始只留 kivy，后续再加其他库）
requirements = python3,kivy

# 日志级别（方便排查）
log_level = 2
