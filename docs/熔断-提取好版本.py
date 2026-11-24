# -*- coding: utf-8 -*-
"""熔断：从上一个可用 APK（66AFC177）提取 index_modded6.html。"""
import os
import zipfile

APK = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261128_第31轮b_联动自查修正.apk"
OUT = r"E:\TAML\_dol\work\index_from_good.apk.html"

if not os.path.exists(APK):
    print("❌ 找不到可用版本:", APK)
    raise SystemExit(1)

z = zipfile.ZipFile(APK)
idx = z.read("assets/www/index.html")
open(OUT, "wb").write(idx)
print("已提取: %d 字节 -> %s" % (len(idx), OUT))

# 对比当前
cur = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read()
print("当前 index: %d 字节" % len(cur))
print("差异: %+d" % (len(cur) - len(idx)))
