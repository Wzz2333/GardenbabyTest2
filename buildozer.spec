[app]
# 🔧 这里只改这3个（必须全英文，无中文/空格）
title = GardenBabyTest
package.name = gardenbabytest
package.domain = com.wzz2333.test

# 🔴 必加：解决 source.dir 缺失（绝对不能删）
source.dir = .
# 入口文件（必须和你仓库里的main.py一致）
source.main = main.py
# 支持的文件类型
source.include_exts = py,png,jpg,kv,atlas

# 版本号
version = 0.1

# 📱 安卓核心配置（单架构+自动许可）
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
# 🔴 强制单架构（绝对不能加其他架构）
android.archs = armeabi-v7a
# 基础权限
android.permissions = INTERNET
# 关闭aapt2避免警告
android.use_aapt2 = False

# 📦 依赖（只留kivy，绝对干净）
requirements = python3,kivy

# 日志级别（方便排查，不混乱）
log_level = 2
