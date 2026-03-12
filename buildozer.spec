[app]

title = GardenBaby
package.name = gardenbaby
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 21

android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET

log_level = 2


[buildozer]

log_level = 2
warn_on_root = 1
