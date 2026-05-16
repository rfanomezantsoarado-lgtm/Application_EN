[app]

# (str) Title of your application
title = EN App

# (str) Package name
package.name = enapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.enapp

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,db

# (list) List of inclusions using pattern matching
source.include_patterns = images/*,factures/*

# (str) Application versioning
version = 0.1

# (list) Application requirements - AJOUT CRITIQUE
requirements = python3,kivy==2.3.0,sqlite3,android,pyjnius,reportlab,requests

# (str) Presplash of the application
presplash.filename = %(source.dir)s/images/icon.png

# (str) Icon of the application
icon.filename = %(source.dir)s/images/icon.png

# (str) Supported orientations
orientation = portrait

# (list) Permissions - AJOUT CRITIQUE
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 24

# (bool) Accept SDK license
android.accept_sdk_license = True

# (list) Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

# (str) Android logcat filters to see debug messages
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = True

# (bool) Skip byte compile for .py files (aide au debugging)
android.no-byte-compile-python = False

[buildozer]

log_level = 2
warn_on_root = 1
