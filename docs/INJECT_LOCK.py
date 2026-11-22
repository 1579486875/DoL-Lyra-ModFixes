# -*- coding: utf-8 -*-
"""把 lock.png 注入指定 APK（打包流程收尾步骤，可复用）。"""
import os
import sys
import zipfile

SRC = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\signed_t21\build_fixed_unsigned-aligned-signed.apk"
DST = sys.argv[2] if len(sys.argv) > 2 else r"E:\TAML\_dol\work\build_lockpatched.apk"
MOD = r"E:\TAML\_dol\work\_downloads\SmartPhone.Alpha-v0.3.91.1.mod.zip"
TARGET = "assets/www/img/ui/phone/lock.png"

z = zipfile.ZipFile(MOD)
lock = z.read("img/ui/phone/lock.png")
print("lock.png", len(lock), "bytes")

n = 0
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zout:
    for info in zin.infolist():
        if info.filename == TARGET:
            continue
        if info.filename.upper().startswith("META-INF/") and info.filename.upper().endswith((".SF", ".RSA", ".DSA")):
            continue
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.external_attr = info.external_attr
        zi.compress_type = zipfile.ZIP_STORED if info.filename == "resources.arsc" else info.compress_type
        zout.writestr(zi, zin.read(info.filename))
        n += 1
    zi = zipfile.ZipInfo(TARGET, date_time=(2026, 11, 22, 0, 0, 0))
    zi.compress_type = zipfile.ZIP_DEFLATED
    zout.writestr(zi, lock)
    n += 1

print("entries:", n, "size MB:", round(os.path.getsize(DST) / 1048576, 2))
with zipfile.ZipFile(DST) as z2:
    print("testzip:", z2.testzip(), "| lock:", TARGET in z2.namelist())
