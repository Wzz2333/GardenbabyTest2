[app]
# 应用基本信息
title = 花园宝宝
package.name = gardenbaby
package.domain = org.gardenbaby
version = 0.2.5

# 源代码和资源配置（关键：包含所有文件类型）
source.dir = .
# 包含你所有的文件类型：py/png/jpg/ttf/txt
source.include_exts = py,png,jpg,ttf,txt
source.exclude_exts = spec,pyc,pyo
source.exclude_dirs = venv,build,.vscode

# 安卓核心配置
android.ndk = 25b
android.sdk = 24
android.api = 33
android.ndk_api = 21
android.build_tool = 30.0.3
# 安卓权限（允许读取/写入文件）
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# 屏幕方向（竖屏）
orientation = portrait
fullscreen = 0

# 依赖配置
requirements = python3,kivy==2.2.1,pillow
# 打包模式（debug，方便测试）
android.debug = 1

[buildozer]
log_level = 2
warn_on_root = 1