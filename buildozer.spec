[app]

title = GardenBaby
package.name = gardenbaby
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf

version = 0.1

requirements = python3,kivy,pillow
source.include_exts = py,png,jpg,jpeg,ttf,json
android.api = 33
android.minapi = 21
android.ndk = 25b

orientation = portrait
fullscreen = 0



# 架构
android.archs = arm64-v8a, armeabi-v7a

# 自动接受 SDK 协议
android.accept_sdk_license = True

# 权限
android.permissions = INTERNET

# 日志
log_level = 2


[buildozer]

log_level = 2
warn_on_root = 1

