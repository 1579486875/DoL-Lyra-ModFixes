# -*- coding: utf-8 -*-
"""把新的 corset/6.png 替换进 APK。"""
import os
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
NEWFILE = r"E:\TAML\_dol\work\诊断-三类服装\corset-新\6.png"
OUT = r"E:\TAML\_dol\work\DoL-corset-fix.apk"

TARGET = "assets/www/img/clothes/under-upper/corset/6.png"

if not os.path.exists(NEWFILE):
    raise SystemExit("❌ 新文件不存在")

newdata = open(NEWFILE, "rb").read()
print("新文件:", len(newdata), "字节")

z = zipfile.ZipFile(APK)
old = z.getinfo(TARGET)
print("原文件:", old.file_size, "字节")

# 重建
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    n = 0
    for info in z.infolist():
        if info.filename == TARGET:
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, newdata)
            n += 1
        else:
            data = z.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
    print("替换:", n)

print("✅ 输出:", OUT)
print("   大小: %.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

# 校验
z2 = zipfile.ZipFile(OUT)
print("   新包内 6.png:", z2.getinfo(TARGET).file_size, "字节")
print("   条目数:", len(z2.namelist()), "(原", len(z.namelist()), ")")
