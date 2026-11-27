# -*- coding: utf-8 -*-
"""搜 misc/icon/clothes 的路径构造，以及 peach 相关的花色定义。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 1) icon/clothes 路径构造 ===")
for mm in list(re.finditer(r"misc/icon/clothes", h))[:8]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 400):mm.start() + 300].replace("\n", " ")[:650]))

print("\n\n=== 2) 搜 peach 单词 ===")
for mm in list(re.finditer(r"peach", h, re.I))[:15]:
    seg = h[max(0, mm.start() - 150):mm.start() + 150]
    print("  @%d: %s" % (mm.start(), seg.replace("\n", " ")[:280]))

print("\n\n=== 3) 搜 heart 相关的 icon 名 ===")
for mm in list(re.finditer(r"heart[-\w]*\.png", h))[:15]:
    print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 100):mm.start() + 60].replace("\n", " ")[:180]))
