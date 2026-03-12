[app]
# 应用基本信息（修改为你的信息，必须是英文）
title = GardenBabyTest
package.name = gardenbabytest
package.domain = com.wzz2333.test
# 入口文件
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
# 版本号
version = 0.1

# 核心构建配置（修复版本兼容问题）
android.api = 33
android.ndk = 25b
android.sdk = 24
# 自动接受 SDK 许可证（关键！解决之前的许可证问题）
android.accept_sdk_license = True
# 适配的架构（只保留主流架构，减少构建时间）
android.archs = arm64-v8a, armeabi-v7a
# 权限（按需添加，默认网络权限）
android.permissions = INTERNET
# 关闭过时的 aapt2 配置（避免警告）
android.use_aapt2 = False

# 依赖库（初始只保留 Kivy，避免第三方库依赖冲突）
requirements = python3,kivy

# 日志级别（构建失败时显示详细日志，方便排查）
log_level = 2
