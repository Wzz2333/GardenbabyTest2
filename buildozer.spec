[app]
# 应用基础信息（必须全英文，无中文/空格）
title = GardenBaby
package.name = gardenbaby
package.domain = com.wzz2333.test

# 核心修复：指定源码目录为「当前根目录」（. 代表根目录）
source.dir = .
# 入口文件（必须和仓库里的文件名一致）
source.main = main.py
# 支持的文件格式（按需保留）
source.include_exts = py,png,jpg,kv,atlas

# 版本号
version = 0.1

# 安卓构建配置（单架构 + 自动接受许可证）
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
android.archs = armeabi-v7a  # 单架构，保证兼容
android.permissions = INTERNET

# 依赖库（初始只保留 kivy，避免冲突）
requirements = python3,kivy

# 日志级别
log_level = 2
